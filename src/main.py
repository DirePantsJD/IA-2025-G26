import modelos.cidade as cd
import modelos.veiculo as vc
import algoritmos.a_estrela as ae
import algoritmos.dijkstra as djk
from graficos.draw import draw_state
from simulação.simulador import Simulador, TOTAL_STEPS
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

city = cd.gen_city_graph()
fleet = vc.gen_fleet(list(city.nodes))
astar = ae.AStar(city, ae.distance_heuristic)
dijkstra = djk.Dijkstra(city)

sim = Simulador(city, fleet, astar, dijkstra)

fig, ax = plt.subplots(figsize=(10, 10))


def update(frame):
    ax.clear()
    sim.tick()
    draw_state(ax, sim.city, sim.fleet, sim.requests, sim.active_routes,
               sim.active_assignments)


ani = FuncAnimation(
    fig,
    update,
    frames=TOTAL_STEPS,
    interval=60
)

plt.show()

print("\n=== RESUMO DA SIMULAÇÃO ===")
for k, v in sim.metrics.summary().items():
    print(f"{k}: {v}")
