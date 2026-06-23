import random
from modelos.pedido import REQUEST_PROBABILITY, gen_request
from modelos.cidade import update_traffic, edge_distance, station_nodes
from modelos.veiculo import needs_restock
from algoritmos.algoritmoProcura import assign_vehicles
from métricas.metricas import MetricsCollector

TIME_STEP_MIN = 1
SIMULATION_HOURS = 6
TOTAL_STEPS = int((SIMULATION_HOURS * 60) / TIME_STEP_MIN)


class Simulador:
    def __init__(self, city, fleet, alg, alg2):
        self.hour = 8
        self.minute = 0
        self.city = city
        self.requests = []
        self.completed_rqs = []
        self.next_request_id = 0
        self.fleet = fleet
        self.alg = alg
        self.alg2 = alg2
        self.active_routes = {}
        self.active_assignments = {}

        self.metrics = MetricsCollector()

    def tick(self):
        self.minute += TIME_STEP_MIN
        self.hour = int((8 * 60 + self.minute) / 60) % 24

        update_traffic(self.city, self.hour)

        # Gera ou naõ pedido aleatoriamente
        if random.random() < REQUEST_PROBABILITY:
            r = gen_request(
                     self.city, self.hour, self.minute, self.next_request_id
                 )
            self.requests.append(r)
            self.next_request_id += 1
            self.metrics.total_requests = self.next_request_id - 1

        # ve pedidos que ultrapassam o tempo de espera
        for r in list(self.requests):
            if hasattr(r, "assigned"):
                continue

            elapsed_minutes = self.minute - r.minute
            if elapsed_minutes > r.max_wait:
                self.requests.remove(r)
                self.metrics.on_request_expired()

        # verifica veiculos que precisao de carregar/encher deposito
        for v in self.fleet:
            if v.state == "idle" and needs_restock(v):
                path = path_to_station(self.city, self.alg, v)
                if path:
                    v.state = "going_to_station"
                    v.path = path
                    v.p_idx = 0
                    v.edge_progress = 0.0

        # pedidos por atribuir
        unassigned = [
            r for r in self.requests if not hasattr(r, "assigned")
        ]
        # atribui pedidos e retorna as suas informações
        assignments = assign_vehicles(
                        self.city, self.alg, self.alg2, self.fleet, unassigned
                    )

        # altera as informações dos veiculos atribuidos
        for r_id, data in assignments.items():
            r = next(r for r in self.requests if r.id == r_id)
            r.assigned = True
            r.vehicle = data["vehicle"]

            v = data["vehicle"]

            v.request = r

            self.metrics.on_assignment(r, v, data)

            if v.state == "idle":
                v.state = "to_pickup"
                v.path = data["full_path"]
                v.pickup_index = len(data["path_to_pickup"]) - 1
                v.edge_index = 0
                v.edge_progress = 0.0
                v.assignment_time = self.minute

                self.active_routes[v.id] = v.path
                self.active_assignments[r.id] = data

        # move o veiculo
        self.move_vehicles()

        # verificação dos estados dos veiculos e cleanup
        for v in self.fleet:
            # if v.state == "to_pickup" and v.edge_index >= v.pickup_index:
            #     v.state = "to_dropoff"
            #     self.metrics.on_pickup(v.request.minute, self.minute)

            if v.state == "going_to_station" and not v.path:
                v.state = "refueling"
                self.metrics.on_refuel_start()

            if v.state == "refueling":
                self.metrics.on_refuel_tick(TIME_STEP_MIN)
                v.autonomy += v.restock_rate * TIME_STEP_MIN
                if v.autonomy >= v.max_autonomy:
                    v.autonomy = v.max_autonomy
                    v.state = "idle"

            if v.path and v.p_idx >= len(v.path) - 1:
                v.state = "idle"
                v.path = []
                v.p_idx = 0
                v.edge_progress = 0.0

                if v.id in self.active_routes:
                    del self.active_routes[v.id]

                for r_id, data in list(self.active_assignments.items()):
                    if data["vehicle"].id == v.id:
                        del self.active_assignments[r_id]
                        self.metrics.on_request_completed(r, v, self.minute)
                        self.requests = [
                            r for r in self.requests if r.id != r_id
                        ]

                for vid in list(self.active_routes.keys()):
                    v = next((v for v in self.fleet if v.id == vid), None)
                    if v is None or not v.path:
                        del self.active_routes[vid]

        # print dos custos
        for r_id, data in assignments.items():
            print(
                f"Request {r_id}: "
                f"A* cost = {data['cost_astar']:.2f}, "
                f"Dijkstra cost = {data['cost_dijkstra']:.2f}"
            )

    def move_vehicles(self):
        for v in self.fleet:
            if not v.path or v.p_idx >= len(v.path) - 1:
                continue

            u = v.path[v.p_idx]
            w = v.path[v.p_idx + 1]

            edge_len = edge_distance(self.city, u, w)          # km
            speed_km_min = v.speed / 60                 # km per minute
            advance = speed_km_min * TIME_STEP_MIN      # km this frame

            progress_increment = advance / edge_len
            v.edge_progress += progress_increment

            consume_autonomy(v, advance)

            with_passenger = (v.state == "to_dropoff")
            self.metrics.on_move(v, advance, with_passenger)

            if v.edge_progress >= 1.0:
                v.p_idx += 1
                v.edge_progress = 0.0
                v.location = w

                if v.state == "to_pickup" and v.location == v.request.origin:
                    v.state = "to_dropoff"
                    self.metrics.on_pickup(v.request.minute, self.minute)


def consume_autonomy(vehicle, distance_km):
    vehicle.autonomy -= distance_km
    vehicle.autonomy = max(vehicle.autonomy, 0)


def path_to_station(city, astar, vehicle):
    best_path = None
    best_cost = float("inf")

    for s in station_nodes(city, vehicle):
        path, cost, _ = astar.search(vehicle.location, s)
        if path and cost < best_cost:
            best_cost = cost
            best_path = path

    return best_path
