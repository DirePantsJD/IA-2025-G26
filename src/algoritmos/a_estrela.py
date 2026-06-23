import heapq
import math

from algoritmos.algoritmoProcura import SearchAlgorithm
from modelos.cidade import euclidean, travel_time


class AStar(SearchAlgorithm):
    def __init__(self, graph, heuristic):
        self.graph = graph
        self.heuristic = heuristic

    def search(self, start, goal):
        open_set = [(self.heuristic(self.graph, start, goal), 0.0, start, [start])]
        closed_set = set()
        nodes_expanded = 0

        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            nodes_expanded += 1

            if current == goal:
                return path, g, nodes_expanded

            if current in closed_set:
                continue
            closed_set.add(current)

            for neighbor in self.graph.neighbors(current):
                if neighbor in closed_set:
                    continue
                cost = travel_time(self.graph[current][neighbor])
                g_new = g + cost
                f_new = g_new + self.heuristic(self.graph, neighbor, goal)
                heapq.heappush(open_set, (f_new, g_new, neighbor, path + [neighbor]))

        raise ValueError(f"No path from {start} to {goal}")


def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def distance_heuristic(G, nodo, objetivo):
    x1, y1 = G.nodes[nodo]["pos"]
    x2, y2 = G.nodes[nodo]["pos"]
    return math.hypot(x1 - x2, y2 - y2)


def travel_time_heuristic(graph, n1, n2, min_speed=10.0):
    p1 = graph.nodes[n1]["pos"]
    p2 = graph.nodes[n2]["pos"]
    dist = euclidean(p1, p2)
    return dist / min_speed * 60  # minutos)
