import random

# Parâmetros gerais
NUM_ELECTRIC = 10
NUM_COMBUSTION = 10
MIN_AUTONOMY_ELECTRIC = 50    # km
MAX_AUTONOMY_ELECTRIC = 150
MIN_AUTONOMY_COMBUSTION = 50
MAX_AUTONOMY_COMBUSTION = 600

MIN_CAPACITY = 3
MAX_CAPACITY = 6

COST_PER_KM_ELECTRIC = 0.10  # €/km
COST_PER_KM_COMBUSTION = 0.25


class Vehicle:
    def __init__(self, id, type, location,
                 autonomy, capacity, cost, speed):
        self.id = id
        self.type = type              # "electrico" | "combustao"
        self.location = location
        self.autonomy = autonomy
        self.capacity = capacity
        self.cost = cost
        self.speed = speed
        self.state = "idle"
        self.path = []
        self.p_idx = 0              # progresso no caminho
        self.edge_progress = 0.0   # progresso na aresta
        self.assignment_time = 0
        self.request = []
        if type == "electric":
            self.max_autonomy = MAX_AUTONOMY_ELECTRIC
            self.min_autonomy = MIN_AUTONOMY_ELECTRIC
            self.restock_rate = MAX_AUTONOMY_ELECTRIC / 15  # minutos
        else:
            self.max_autonomy = MAX_AUTONOMY_COMBUSTION
            self.min_autonomy = MIN_AUTONOMY_COMBUSTION
            self.restock_rate = MAX_AUTONOMY_COMBUSTION / 15  # minutos

    def __repr__(self):
        return f"{self.id} | {self.type} | \
                 Loc: {self.location} | \
                 Aut: {self.autonomy/self.max_autonmy} |\
                 Cap: {self.capacity} | Custo/km: {self.cost}"


def gen_fleet(nodes):
    fleet = []

    # Veículos elétricos
    for i in range(NUM_ELECTRIC):
        loc = random_start_location(nodes)
        autonomy = random.randint(MIN_AUTONOMY_ELECTRIC, MAX_AUTONOMY_ELECTRIC)
        capacity = random.randint(MIN_CAPACITY, MAX_CAPACITY)
        fleet.append(Vehicle(
            id=f"E{i}",
            type="electric",
            location=loc,
            autonomy=autonomy,
            capacity=capacity,
            cost=COST_PER_KM_ELECTRIC,
            speed=40
        ))

    # Veículos a combustão
    for i in range(NUM_COMBUSTION):
        loc = random_start_location(nodes)
        autonomy = random.randint(
                        MIN_AUTONOMY_COMBUSTION,
                        MAX_AUTONOMY_COMBUSTION
                    )
        capacity = random.randint(MIN_CAPACITY, MAX_CAPACITY)
        fleet.append(Vehicle(
            id=f"C{i}",
            type="combustion",
            location=loc,
            autonomy=autonomy,
            capacity=capacity,
            cost=COST_PER_KM_COMBUSTION,
            speed=40
        ))

    return fleet


# Possíveis localizações iniciais (nós do grafo)
def random_start_location(nodes):
    return random.choice(nodes)


def needs_restock(vehicle):
    return vehicle.autonomy <= vehicle.min_autonomy
