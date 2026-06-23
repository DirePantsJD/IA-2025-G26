import random
import networkx as nx
import math


NUM_NODOS = 70
NUM_BOMBAS_GASOLINA = 10  # ± 17 em Braga?
NUM_ESTACOES_CARREGAMENTO = 15  # ±25 em Braga?

RAIO_CIDADE = 10  # km
TAMANHO_MAX_ARESTA = 2  # km


def gen_city_graph():
    G = nx.Graph()

    # ---------- ZONAS DA CIDADE ----------
    for i in range(NUM_NODOS):
        x, y = random_position()
        G.add_node(
            f"Z{i}",
            type="zone",
            pos=(x, y)
        )

    # ---------- ESTAÇÕES DE RECARGA ----------
    for i in range(NUM_ESTACOES_CARREGAMENTO):
        x, y = random_position()
        G.add_node(
            f"C{i}",
            type="charging_station",
            pos=(x, y)
        )

    # ---------- POSTOS DE COMBUSTÍVEL ----------
    for i in range(NUM_BOMBAS_GASOLINA):
        x, y = random_position()
        G.add_node(
            f"F{i}",
            type="fuel_station",
            pos=(x, y)
        )

    spanning_tree(G)
    add_extra_connections(G)

    return G


def random_position():
    r = RAIO_CIDADE * math.sqrt(random.random())
    theta = random.random() * 2 * math.pi
    return r * math.cos(theta), r * math.sin(theta)


def spanning_tree(G):
    nodes = list(G.nodes(data=True))
    unconnected = set([n for n, _ in nodes])
    connected = set()

    # pick random starting node
    start = random.choice(list(unconnected))
    connected.add(start)
    unconnected.remove(start)

    while unconnected:
        # find the closest pair (connected -> unconnected)
        min_dist = float('inf')
        connect_from = None
        connect_to = None

        for u in connected:
            for v in unconnected:
                dist = euclidean(G.nodes[u]["pos"], G.nodes[v]["pos"])
                if dist < min_dist:
                    min_dist = dist
                    connect_from = u
                    connect_to = v

        # add edge
        add_road(G, connect_from, connect_to, min_dist)

        # update sets
        connected.add(connect_to)
        unconnected.remove(connect_to)


def add_extra_connections(G, max_distance=3.5, probability=0.25):
    nodes = list(G.nodes(data=True))

    for i, (u, udata) in enumerate(nodes):
        for v, vdata in nodes[i+1:]:
            if G.has_edge(u, v):
                continue

            dist = euclidean(udata["pos"], vdata["pos"])
            if dist <= max_distance and random.random() < probability:
                add_road(G, u, v, dist)


def add_road(G, u, v, dist):
    speed = random.uniform(30, 50)  # km/h
    time = dist / speed * 60        # minutes

    G.add_edge(
        u, v,
        distance=round(dist, 2),
        base_time=round(time, 2),
        traffic_factor=1.0
    )


def euclidean(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)


def update_traffic(G, hour):
    for u, v, data in G.edges(data=True):
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            data["traffic_factor"] = random.uniform(1.3, 1.8)
        else:
            data["traffic_factor"] = random.uniform(0.9, 1.2)


def travel_time(edge_data):
    return edge_data["base_time"] * edge_data["traffic_factor"]


def edge_distance(graph, u, v):
    return graph[u][v]["distance"]


def station_nodes(city, vehicle):
    if vehicle.type == "electric":
        return [
            n for n, d in city.nodes(data=True)
            if d["type"] == "charging_station"
        ]
    else:
        return [
            n for n, d in city.nodes(data=True)
            if d["type"] == "fuel_station"
        ]
