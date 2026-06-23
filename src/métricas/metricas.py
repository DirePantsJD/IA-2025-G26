class MetricsCollector:
    def __init__(self):
        # ---- PEDIDOS ----
        self.total_requests = 0
        self.assigned_requests = 0
        self.completed_requests = 0
        self.expired_requests = 0

        self.wait_times = []
        self.trip_times = []
        self.total_wait_time = 0
        self.total_trip_time = 0

        # ---- FROTA ----
        self.km_total = 0.0
        self.km_with_passenger = 0.0
        self.km_empty = 0.0
        self.km_electric = 0.0
        self.km_combustion = 0.0

        self.refuel_events = 0
        self.refuel_time = 0.0  # minutos

        # ---- ALGORITMOS ----
        self.astar_costs = []
        self.dijkstra_costs = []

        self.astar_expanded = []
        self.dijkstra_expanded = []

        # ---- SUSTENTABILIDADE ----
        self.electric_trips = 0
        self.combustion_trips = 0

    def on_new_request(self):
        self.total_requests += 1

    def on_assignment(self, request, vehicle, data):
        self.assigned_requests += 1

        self.astar_costs.append(data["cost_astar"])
        self.astar_expanded.append(data["astar_n_expanded"])

        self.dijkstra_costs.append(data["cost_dijkstra"])
        self.dijkstra_expanded.append(data["dijkstra_n_expanded"])

        if vehicle.type == "electric":
            self.electric_trips += 1
        else:
            self.combustion_trips += 1

    def on_pickup(self, a_t, t):
        self.total_wait_time += t - a_t
        self.wait_times.append(t - a_t)

    def on_move(self, vehicle, distance, with_passenger):
        self.km_total += distance
        if vehicle.type == "electric":
            self.km_electric += distance
        else:
            self.km_combustion += distance

        if with_passenger:
            self.km_with_passenger += distance
        else:
            self.km_empty += distance

    def on_request_completed(self, request, vehicle, end_time):
        self.completed_requests += 1
        trip_time = end_time - request.assigned_time
        self.trip_times.append(trip_time)
        self.total_requests += trip_time

    def on_request_expired(self):
        self.expired_requests += 1

    def on_refuel_start(self):
        self.refuel_events += 1

    def on_refuel_tick(self, tsm):
        self.refuel_time += tsm

    def summary(self):
        return {
            "Total pedidos": self.completed_requests + self.expired_requests,
            "Pedidos atendidos": self.completed_requests,
            "Pedidos expirados": self.expired_requests,
            "Tempo médio de espera": (
                sum(self.wait_times) / len(self.wait_times)
                if self.wait_times else 0
            ),
            "Tempo total de espera": self.total_wait_time,
            "Km totais": self.km_total,
            "Km ocupados": self.km_total - self.km_empty,
            "Km vazios": self.km_empty,
            "Km V. eletricos": self.km_electric,
            "Km V. combustão": self.km_combustion,
            "Taxa de ocupação": (
                self.km_with_passenger / self.km_total
                if self.km_total else 0
            ),
            "A* nós expandidos (médio)": (
                sum(self.astar_expanded) / len(self.astar_expanded)
                if self.astar_expanded else 0
            ),
            "Dijkstra nós expandidos (médio)": (
                sum(self.dijkstra_expanded) / len(self.dijkstra_expanded)
                if self.dijkstra_expanded else 0
            )
        }
