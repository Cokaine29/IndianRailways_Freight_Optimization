# CE 749 — network_map.py: Geographic network visualization

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

OUT = "outputs"

# Approximate geographic coordinates (lon, lat) for each node
NODE_COORDS = {
    1:  (77.1, 28.7),   # Delhi
    2:  (72.8, 19.1),   # Mumbai
    3:  (80.3, 13.1),   # Chennai
    4:  (88.4, 22.6),   # Kolkata
    5:  (79.1, 21.1),   # Nagpur
    6:  (77.4, 23.3),   # Bhopal
    7:  (78.5, 17.4),   # Hyderabad
    8:  (73.9, 18.5),   # Pune
    9:  (72.6, 23.0),   # Ahmedabad
    10: (80.3, 26.5),   # Kanpur
    11: (85.8, 20.3),   # Bhubaneswar
    12: (80.6, 16.5),   # Vijayawada
    13: (81.6, 21.3),   # Raipur
    14: (86.2, 22.8),   # Jamshedpur
    15: (75.8, 30.9),   # Ludhiana
    16: (83.3, 17.7),   # Vizag
}

NODE_NAMES = {
    1:"Delhi", 2:"Mumbai", 3:"Chennai", 4:"Kolkata",
    5:"Nagpur", 6:"Bhopal", 7:"Hyderabad", 8:"Pune",
    9:"Ahmedabad", 10:"Kanpur", 11:"Bhubaneswar", 12:"Vijayawada",
    13:"Raipur", 14:"Jamshedpur", 15:"Ludhiana", 16:"Vizag"
}

CMAP  = {1:"#E63946", 2:"#457B9D", 3:"#2A9D8F", 4:"#E9C46A"}
CNAME = {1:"Coal", 2:"Cement", 3:"Foodgrains", 4:"Fertilizers"}


def plot_network_flows(cost_flows, emis_flows):
    """Plot side-by-side network maps: cost-optimal vs emission-optimal flows"""
    from src.data import ARC_TRACTION

    fig, axes = plt.subplots(1, 2, figsize=(18, 10))
    fig.patch.set_facecolor('#F8F9FA')

    for ax, (flows, title) in zip(axes, [
        (cost_flows, "Cost-Optimal Allocation"),
        (emis_flows, "Emission-Optimal Allocation")
    ]):
        ax.set_facecolor('#EEF2F7')

        # Draw all arcs (light grey background)
        drawn = set()
        for (i, j) in ARC_TRACTION:
            if (j, i) in drawn: continue
            drawn.add((i, j))
            x1, y1 = NODE_COORDS[i]
            x2, y2 = NODE_COORDS[j]
            color = '#AAAAAA' if ARC_TRACTION[(i,j)] == 'electric' else '#DDBBAA'
            lw = 1.5 if ARC_TRACTION[(i,j)] == 'electric' else 1.0
            ls = '-' if ARC_TRACTION[(i,j)] == 'electric' else '--'
            ax.plot([x1, x2], [y1, y2], color=color, lw=lw, ls=ls, zorder=1, alpha=0.5)

        # Aggregate total flow per arc across all commodities
        arc_flow = {}
        for k, arcs in flows.items():
            for (i, j), v in arcs.items():
                key = (min(i,j), max(i,j))
                arc_flow[key] = arc_flow.get(key, 0) + v

        max_flow = max(arc_flow.values()) if arc_flow else 1

        # Draw flow arcs (width proportional to flow)
        for (i, j), total in arc_flow.items():
            if total < 0.5: continue
            x1, y1 = NODE_COORDS[i]
            x2, y2 = NODE_COORDS[j]
            lw = 1.5 + (total / max_flow) * 8
            trac = ARC_TRACTION.get((i,j), ARC_TRACTION.get((j,i), 'electric'))
            color = '#1D6FA4' if trac == 'electric' else '#C45C2A'
            ax.plot([x1, x2], [y1, y2], color=color, lw=lw,
                    alpha=0.75, zorder=2, solid_capstyle='round')
            # Flow label at midpoint
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my, f'{total:.0f}', fontsize=6.5, ha='center', va='center',
                    color='white', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.15', facecolor=color, alpha=0.8, lw=0))

        # Draw nodes
        hub_nodes = {1, 2, 3, 4, 13, 14, 15, 16}
        for n, (x, y) in NODE_COORDS.items():
            size  = 160 if n in hub_nodes else 80
            color = '#1D3557' if n in hub_nodes else '#457B9D'
            ax.scatter(x, y, s=size, color=color, zorder=5, edgecolors='white', linewidths=1.5)
            offset_x = 0.4 if x < 79 else -0.4
            offset_y = 0.5 if y > 20 else -0.6
            ax.text(x+offset_x, y+offset_y, NODE_NAMES[n],
                    fontsize=8, ha='center', fontweight='bold',
                    color='#1D3557',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, lw=0))

        ax.set_title(title, fontsize=13, fontweight='bold', pad=12, color='#1D3557')
        ax.set_xlim(70, 92); ax.set_ylim(11, 32)
        ax.set_xlabel('Longitude', fontsize=9, color='gray')
        ax.set_ylabel('Latitude', fontsize=9, color='gray')
        ax.tick_params(labelsize=8, colors='gray')
        for spine in ax.spines.values(): spine.set_edgecolor('#CCCCCC')

    # Shared legend
    elec_patch  = mpatches.Patch(color='#1D6FA4', label='Electric traction (low emission)')
    diesel_patch = mpatches.Patch(color='#C45C2A', label='Diesel traction (high emission)')
    hub_patch   = mpatches.Patch(color='#1D3557', label='Major hub (Delhi/Mumbai/Chennai/Kolkata)')
    fig.legend(handles=[elec_patch, diesel_patch, hub_patch],
               loc='lower center', ncol=3, fontsize=9,
               framealpha=0.9, bbox_to_anchor=(0.5, 0.01))

    plt.suptitle('Freight Flow Network — Indian Railway Golden Quadrilateral\n'
                 'Line width ∝ total flow (MT) | Numbers = total flow in MT',
                 fontsize=14, fontweight='bold', y=1.0, color='#1D3557')
    plt.tight_layout(rect=[0, 0.06, 1, 0.97])
    path = f"{OUT}/fig0_network_map.png"
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"  Saved: {path}")
    return path
