import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.patches import FancyArrowPatch, ArrowStyle
import networkx as nx
from modelos.cidade import edge_distance

TIME_STEP_MIN = 0.5


def draw_state(ax, city, fleet, requests, routes, assignments):
    ax.clear()
    pos = nx.get_node_attributes(city, "pos")

    # ---------- DESENHAR NÓS DA CIDADE ----------
    zone_nodes = [
        n for n, d in city.nodes(data=True) if d["type"] == "zone"
    ]
    charging_nodes = [
        n for n, d in city.nodes(data=True)
        if d["type"] == "charging_station"
    ]
    fuel_nodes = [
        n for n, d in city.nodes(data=True) if d["type"] == "fuel_station"
    ]

    nx.draw_networkx_nodes(
        city, pos, nodelist=zone_nodes,
        node_color="lightgray", node_size=200, label="Zones")

    nx.draw_networkx_nodes(city, pos, nodelist=charging_nodes,
                           node_color="green", node_shape="s",
                           node_size=300, label="Charging Stations")

    nx.draw_networkx_nodes(city, pos, nodelist=fuel_nodes,
                           node_color="red", node_shape="^",
                           node_size=300, label="Fuel Stations")

    # ---------- DESENHAR RUAS ----------
    nx.draw_networkx_edges(city, pos, edge_color="lightgray", alpha=0.6)

    # ---------- DESENHAR VEÍCULOS ----------
    draw_vehicles(city, fleet, pos)

    # -------- DESENHAR PEDIDOS ----------
    draw_requests(city, requests, pos)

    # --------- ATRIBUIÇÔES --------------
    draw_assignment_paths(city, assignments, pos)

    # --- ROTAS ---
    for r in requests:
        if r.id in routes:
            color = "orange" if r.priority == "urgent" else \
                    "gold" if r.priority == "premium" else "brown"

            draw_path(city, routes[r.id], pos, color=color)

    # ---------- Caixa de estatísticas ----------
    total_astar_expanded = sum(data.get("astar_n_expanded") for data in assignments.values())
    total_dijkstra_expanded = sum(data.get("dijkstra_n_expanded") for data in assignments.values())

    stats_text = f"Total nós expandidos:\nA*: {total_astar_expanded}  Dijkstra: {total_dijkstra_expanded}"
    # posição: em percentagem do eixo
    ax.text(
        0.0, 0.1, stats_text,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        ha="center",
        va="top",
        bbox=dict(facecolor="white", alpha=0.7, edgecolor="black")
    )

    legend_elements = [
        Patch(facecolor='lightgray', edgecolor='k', label='Zona'),
        Patch(facecolor='green', edgecolor='k', label='Estação de carregamento'),
        Patch(facecolor='red', edgecolor='k', label='Posto de combustível'),
        Line2D([0], [0], color='hotpink', lw=4, label='A*'),
        Line2D([0], [0], color='deepskyblue', lw=2, linestyle='--', label='Dijkstra')
    ]

    ax.legend(handles=legend_elements, loc='upper right')
    ax.axis("off")


def draw_vehicles(city, fleet, pos):
    ex, ey = [], []
    cx, cy = [], []

    for v in fleet:
        x, y = vehicle_position(city, v)

        if v.type == "electric":
            ex.append(x)
            ey.append(y)
        else:
            cx.append(x)
            cy.append(y)

    # elétricos
    plt.scatter(ex, ey,
                c="blue", s=120, marker="o",
                edgecolors="black", label="Electric Taxi",
                zorder=3)

    # combustão
    plt.scatter(cx, cy,
                c="orange", s=120, marker="o",
                edgecolors="black", label="Combustion Taxi",
                zorder=2)


def draw_requests(city, requests, pos):

    for r in requests:
        x1, y1 = pos[r.origin]
        x2, y2 = pos[r.destination]

        if r.priority == "urgent":
            color = "red"
        elif r.priority == "premium":
            color = "gold"
        else:
            color = "brown"

        # seta tracejada
        ax = plt.gca()
        style = ArrowStyle('Fancy', head_length=10,
                           head_width=10, tail_width=0.5)
        arrow = FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle=style,
            linestyle="--",
            linewidth=2,
            color=color,
            alpha=0.7,
            zorder=3
        )

        ax.add_patch(arrow)


def draw_path(G, path, pos, color="blue", linewidth=4):
    edges = list(zip(path[:-1], path[1:]))

    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=edges,
        edge_color=color,
        width=linewidth,
    )


def draw_assignment_paths(G, assignments, pos):
    for data in assignments.values():

        # ---------- A* PATH (rosa) ----------
        astar_path = data.get("full_path")
        if astar_path and len(astar_path) > 1:
            astar_edges = list(zip(astar_path[:-1], astar_path[1:]))

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=astar_edges,
                edge_color="hotpink",
                width=4,
                alpha=0.9,
                label="A*"
            )

        # ---------- DIJKSTRA PATH (azul bebé) ----------
        dijkstra_path = data.get("dijkstra_path")
        if dijkstra_path and len(dijkstra_path) > 1:
            dj_edges = list(zip(dijkstra_path[:-1], dijkstra_path[1:]))

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=dj_edges,
                edge_color="deepskyblue",
                width=2,
                alpha=0.7,
                style="dashed",
                label="Dijkstra"
            )

            cost_astar = data.get("cost_astar")
            cost_dijkstra = data.get("cost_dijkstra")
            if cost_astar is not None and cost_dijkstra is not None:
                delta = cost_dijkstra - cost_astar
                # Coloca o texto próximo do nó de pickup
                pickup_node = astar_path[0] if astar_path else None
                if pickup_node:
                    x, y = pos[pickup_node]
                    plt.text(
                        x, y + 0.2,
                        f"ΔC={delta:.1f}",
                        color="purple",
                        fontsize=9,
                        fontweight="bold"
                    )


def move_vehicles_step_speed(G, fleet):
    for v in fleet:
        if not v.path or v.edge_index >= len(v.path) - 1:
            continue  # no movement

        u = v.path[v.edge_index]
        w = v.path[v.edge_index + 1]

        edge_len = edge_distance(G, u, w)          # km
        speed_km_min = v.speed / 60                 # km per minute
        advance = speed_km_min * TIME_STEP_MIN  # km this frame

        progress_increment = advance / edge_len
        v.edge_progress += progress_increment

        if v.edge_progress >= 1.0:
            v.edge_index += 1
            v.edge_progress = 0.0
            v.location = w


def vehicle_position(G, v):
    if not v.path or v.p_idx >= len(v.path) - 1:
        return G.nodes[v.location]["pos"]

    u = v.path[v.p_idx]
    w = v.path[v.p_idx + 1]

    x1, y1 = G.nodes[u]["pos"]
    x2, y2 = G.nodes[w]["pos"]

    t = v.edge_progress
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)

    return x, y
