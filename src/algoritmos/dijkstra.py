import heapq
from algoritmos.algoritmoProcura import SearchAlgorithm
from modelos.cidade import travel_time


class Dijkstra(SearchAlgorithm):
    def __init__(self, graph):
        self.graph = graph

    def search(self, start, goal):
        frontier = [(0.0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0.0}
        nodes_expanded = 0

        while frontier:
            current_cost, current = heapq.heappop(frontier)
            nodes_expanded += 1

            if current == goal:
                break

            for neighbor in self.graph.neighbors(current):
                cost = travel_time(self.graph[current][neighbor])
                new_cost = current_cost + cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    heapq.heappush(frontier, (new_cost, neighbor))

        # Reconstruir caminho
        path = []
        node = goal
        while node:
            path.append(node)
            node = came_from.get(node)
        path.reverse()

        return path, cost_so_far.get(goal, float("inf")), nodes_expanded
