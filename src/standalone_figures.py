"""
standalone_figures.py
=====================
Regenerate any individual figure without running the full pipeline.

Usage:
    python standalone_figures.py             # regenerates ALL figures
    python standalone_figures.py 0           # network map only
    python standalone_figures.py 1           # Pareto frontier only
    python standalone_figures.py 2           # flow distribution only
    python standalone_figures.py 3           # heuristic comparison only
    python standalone_figures.py 4           # sensitivity only

Each figure is saved to outputs/ directory.
Runtime: ~3-7 seconds depending on which figures are selected.
"""

import sys
import os
os.makedirs("outputs", exist_ok=True)

from src.model import build_and_solve, generate_pareto_frontier
from src.heuristic import run_heuristic_comparison
from src.visualize import (plot_pareto_frontier, plot_flow_distribution,
                       plot_heuristic_comparison, plot_sensitivity)
from src.network_map import plot_network_flows

# ─── Figure 0: Network Map ────────────────────────────────────────────────────
def make_fig0():
    """
    Geographic map of the 16-node network showing freight flows.
    Left panel: cost-optimal flows | Right panel: emission-optimal flows
    Line width proportional to total flow (MT).
    Blue arcs = electric traction | Orange arcs = diesel traction
    """
    print("Generating fig0: Network map...")
    cost_opt = build_and_solve(objective="cost", use_mip=False)
    emis_opt = build_and_solve(objective="emission", use_mip=False)
    plot_network_flows(cost_opt["flows"], emis_opt["flows"])
    print("  -> outputs/fig0_network_map.png")


# ─── Figure 1: Pareto Frontier ────────────────────────────────────────────────
def make_fig1():
    """
    Pareto frontier: cost (Rs Crore) vs emissions (Mt-CO2).
    Shows 12 non-dominated solutions from epsilon-constraint method.
    Greedy heuristic point shown for comparison.
    """
    print("Generating fig1: Pareto frontier...")
    pareto, cost_opt, emis_opt = generate_pareto_frontier(n_points=12, use_mip=False)
    comparison = run_heuristic_comparison(cost_opt)
    plot_pareto_frontier(pareto, comparison)
    print("  -> outputs/fig1_pareto_frontier.png")


# ─── Figure 2: Flow Distribution ─────────────────────────────────────────────
def make_fig2():
    """
    4-panel bar chart showing freight flows per arc for each commodity
    in the cost-optimal solution.
    """
    print("Generating fig2: Flow distribution...")
    cost_opt = build_and_solve(objective="cost", use_mip=False)
    plot_flow_distribution(cost_opt["flows"], "Cost-Optimal")
    print("  -> outputs/fig2_flow_distribution.png")


# ─── Figure 3: Heuristic Comparison ──────────────────────────────────────────
def make_fig3():
    """
    Bar chart comparing MCF-LP optimal vs Greedy Shortest Path heuristic
    on both cost (Rs Crore) and emissions (Mt-CO2).
    """
    print("Generating fig3: Heuristic comparison...")
    cost_opt = build_and_solve(objective="cost", use_mip=False)
    comparison = run_heuristic_comparison(cost_opt)
    plot_heuristic_comparison(comparison)
    print("  -> outputs/fig3_heuristic_comparison.png")


# ─── Figure 4: Sensitivity Analysis ──────────────────────────────────────────
def make_fig4():
    """
    Sensitivity of optimal cost and emissions to diesel arc capacity (MT).
    Shows the binding constraint threshold and cost plateau.
    """
    import src.data as D
    print("Generating fig4: Sensitivity analysis...")
    base = {arc: D.ARC_CAPACITY[arc] for arc in D.ARCS}
    diesel_caps = [40, 50, 60, 70, 80, 90, 100]
    results = []
    for cap in diesel_caps:
        for arc in D.ARCS:
            D.ARC_CAPACITY[arc] = (200 if D.ARC_TRACTION[arc] == "electric"
                                   else (cap if D.ARC_DISTANCES[arc] > 300 else max(cap - 10, 30)))
        r = build_and_solve(objective="cost", use_mip=False)
        if r["Z1"]:
            results.append({"capacity": cap, "Z1": r["Z1"], "Z2": r["Z2"], "status": r["status"]})
    for arc in D.ARCS:
        D.ARC_CAPACITY[arc] = base[arc]
    valid = [r for r in results if r["Z1"] != float('inf')]
    if len(valid) >= 3:
        plot_sensitivity(valid)
        print("  -> outputs/fig4_sensitivity.png")
    else:
        print("  WARNING: Not enough feasible points for sensitivity plot")


# ─── Figure 5: Cost Breakdown ──────────────────────────────────────────────────
def make_fig5():
    """
    Pie chart showing the breakdown of total cost into arc flow, transshipment,
    and backhaul costs.
    """
    from src.visualize import plot_cost_breakdown
    print("Generating fig5: Cost breakdown...")
    cost_opt = build_and_solve(objective="cost", use_mip=False)
    plot_cost_breakdown(cost_opt)

# ─── Figure 6: Flow Comparison ───────────────────────────────────────────────
def make_fig6():
    """
    Horizontal bar chart showing arcs with significant flow differences
    between cost-optimal and emission-optimal solutions.
    """
    from src.visualize import plot_flow_comparison
    print("Generating fig6: Flow comparison...")
    cost_opt = build_and_solve(objective="cost", use_mip=False)
    emis_opt = build_and_solve(objective="emission", use_mip=False)
    plot_flow_comparison(cost_opt, emis_opt)


# ─── Dispatch ─────────────────────────────────────────────────────────────────
FIGURES = {
    "0": ("Network Map",          make_fig0),
    "1": ("Pareto Frontier",       make_fig1),
    "2": ("Flow Distribution",     make_fig2),
    "3": ("Heuristic Comparison",  make_fig3),
    "4": ("Sensitivity Analysis",  make_fig4),
    "5": ("Cost Breakdown",        make_fig5),
    "6": ("Flow Comparison",       make_fig6),
}

if __name__ == "__main__":
    import time

    args = sys.argv[1:]

    if not args:
        # Run all
        print("Regenerating ALL figures...\n")
        t0 = time.time()
        for key, (name, fn) in FIGURES.items():
            fn()
        print(f"\nAll figures saved to outputs/ ({time.time()-t0:.1f}s)")
    else:
        # Run specific figures
        for arg in args:
            if arg in FIGURES:
                name, fn = FIGURES[arg]
                print(f"\n--- Figure {arg}: {name} ---")
                t0 = time.time()
                fn()
                print(f"Done ({time.time()-t0:.1f}s)")
            else:
                print(f"Unknown figure '{arg}'. Choose from: {list(FIGURES.keys())}")
