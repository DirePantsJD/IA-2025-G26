import random


REQUEST_PROBABILITY = 0.1  # probabilidade de surgir pedido por passo
MAX_PASSENGERS = 5


class Request:
    def __init__(self, id, hour, minute, origin, destination, n_passengers,
                 max_wait, priority, eco_pref):
        self.id = id
        self.hour = hour
        self.minute = minute
        self.origin = origin
        self.destination = destination
        self.n_passengers = n_passengers
        self.max_wait = max_wait
        self.priority = priority
        self.eco_pref = eco_pref
        self.state = "waiting"
        self.assigned_time = -1


def gen_random_request(G, time, next_id):
    requests = []

    if random.random() < REQUEST_PROBABILITY:
        requests.append(gen_request(G, time, next_id))

    return requests


def gen_request(G, hour, minute, request_id):
    zones = get_zone_nodes(G)

    origin = random.choice(zones)
    destination = random.choice(zones)
    while destination == origin:
        destination = random.choice(zones)

    return Request(
        id=request_id,
        origin=origin,
        destination=destination,
        n_passengers=random.randint(1, MAX_PASSENGERS),
        max_wait=random.randint(5, 15),   # minutos
        priority=random.choice(["normal", "urgent", "premium"]),
        eco_pref=random.choice([True, False]),
        hour=hour,
        minute=minute
    )


def get_zone_nodes(G):
    return [n for n, d in G.nodes(data=True) if d["type"] == "zone"]
