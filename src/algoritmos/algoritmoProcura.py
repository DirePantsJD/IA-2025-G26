from modelos.cidade import travel_time


class SearchAlgorithm:
    def search(self, inicial_state, objective_state):
        raise NotImplementedError


def compute_request_routes(alg, requests):
    routes = {}

    for r in requests:
        path = alg.search(r.origin, r.destination)
        if path:
            routes[r.id] = path

    return routes


def best_vehicle_for_request(graph, algo, fleet, request):
    best_vehicle = None
    best_path = None
    best_cost = float("inf")

    for vehicle in fleet:
        if vehicle.state != "idle":
            continue
        if vehicle.capacity < request.n_passengers:
            continue

        # A* paths
        path_to_pickup = algo.search(vehicle.location, request.origin)
        if not path_to_pickup:
            continue

        path_to_dropoff = algo.search(request.origin, request.origin)
        if not path_to_dropoff:
            continue

        # merge paths
        full_path = path_to_pickup[:-1] + path_to_dropoff

        # feasibility (autonomy)
        if not vehicle_can_serve(vehicle, graph, full_path):
            continue

        # objective: minimize travel time
        cost = path_travel_time(graph, full_path)

        if cost < best_cost:
            best_cost = cost
            best_vehicle = vehicle
            best_path = full_path

    return best_vehicle, best_path, best_cost


def path_travel_time(G, path):
    total = 0
    for u, v in zip(path[:-1], path[1:]):
        total += travel_time(G[u][v])
    return total


def vehicle_can_serve(vehicle, G, full_path):
    required_distance = path_distance(G, full_path)
    return vehicle.autonomy >= required_distance


def path_distance(G, path):
    total = 0
    for u, v in zip(path[:-1], path[1:]):
        total += G[u][v]["distance"]
    return total


def assign_vehicles(city, astar, dijkstra, vehicles, requests):
    assignments = {}

    for r in requests:
        idle_vehicles = [v for v in vehicles if v.state == "idle"
                            and v.autonomy > v.min_autonomy]
        if not idle_vehicles:
            continue

        best_vehicle = None
        best_cost = float("inf")

        best_astar_pickup = None
        best_astar_dropoff = None
        best_dijkstra_full = None

        cost_astar_total = None
        cost_dijkstra_total = None

        for v in idle_vehicles:
            #------- A* ---------
            path_pick, cost_pick, anx1 = astar.search(v.location, r.origin)
            if path_pick is None:
                continue

            path_drop, cost_drop, anx2 = astar.search(r.origin, r.destination)
            if path_drop is None:
                continue

            total_cost = cost_pick + cost_drop

            if total_cost < best_cost:
                best_cost = total_cost
                best_vehicle = v
                best_astar_pickup = path_pick
                best_astar_dropoff = path_drop
                cost_astar_total = total_cost

                # ---------- DIJKSTRA ----------
                dj_pick, dj_pick_cost, dnx1 = dijkstra.search(v.location, r.origin)
                dj_drop, dj_drop_cost, dnx2 = dijkstra.search(r.origin, r.destination)

                if dj_pick and dj_drop:
                    best_dijkstra_full = dj_pick + dj_drop[1:]
                    cost_dijkstra_total = dj_pick_cost + dj_drop_cost

        if best_vehicle is None:
            continue

        best_vehicle.request = r

        full_astar_path = best_astar_pickup + best_astar_dropoff[1:]

        assignments[r.id] = {
            "vehicle": best_vehicle,
            "path_to_pickup": best_astar_pickup,
            "path_to_dropoff": best_astar_dropoff,
            "full_path": full_astar_path,
            "dijkstra_path": best_dijkstra_full,
            "cost_astar": cost_astar_total,
            "astar_n_expanded": dnx1 + dnx2,
            "cost_dijkstra": cost_dijkstra_total,
            "dijkstra_n_expanded": anx1 + anx2
        }

    return assignments
