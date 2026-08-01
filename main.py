# CE 749 — main.py FINAL

import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from data import NODES, COMMODITIES, DEMAND, ARCS, RAKE_CAPACITY
from model import build_and_solve, generate_pareto_frontier
from heuristic import run_heuristic_comparison
from visualize import (plot_pareto_frontier, plot_flow_distribution,
                       plot_heuristic_comparison, plot_sensitivity,
                       plot_cost_breakdown, plot_flow_comparison)
from network_map import plot_network_flows

os.makedirs("outputs", exist_ok=True)

def hdr(t): print("\n"+"="*65+f"\n  {t}\n"+"="*65)

def print_flows(flows):
    from data import NODES as N
    print(f"\n  {'Commodity':<14} {'Arc':<35} {'Flow (MT)':>10}")
    print("  "+"-"*61)
    for k,arcs in flows.items():
        for (i,j),v in sorted(arcs.items(),key=lambda x:-x[1]):
            print(f"  {COMMODITIES[k]:<14} {N[i]+' -> '+N[j]:<35} {v:>10.2f}")

def print_costs(result, label):
    print(f"\n  {label}:")
    print(f"    Status:            {result['status']}")
    print(f"    Total Cost (Z1):   Rs {result['Z1']/1e7:>10,.0f} crore")
    print(f"      Arc flow:        Rs {result['Z1_flow']/1e7:>10,.0f} crore ({result['Z1_flow']/result['Z1']*100:.1f}%)")
    print(f"      Transshipment:   Rs {result['Z1_transship']/1e7:>10,.0f} crore ({result['Z1_transship']/result['Z1']*100:.1f}%)")
    print(f"      Backhaul:        Rs {result['Z1_backhaul']/1e7:>10,.0f} crore ({result['Z1_backhaul']/result['Z1']*100:.1f}%)")
    print(f"    Emissions (Z2):    {result['Z2']/1e9:>10.4f} Mt-CO2")

def sensitivity_capacity():
    import data as D
    hdr("STEP 5a — SENSITIVITY: Diesel Arc Capacity")
    base = {arc: D.ARC_CAPACITY[arc] for arc in D.ARCS}
    diesel_caps = [40, 50, 60, 70, 80, 90, 100]
    results = []
    for cap in diesel_caps:
        for arc in D.ARCS:
            D.ARC_CAPACITY[arc] = (200 if D.ARC_TRACTION[arc]=="electric"
                                   else (cap if D.ARC_DISTANCES[arc]>300 else max(cap-10,30)))
        r = build_and_solve(objective="cost", use_mip=False)
        entry = {"capacity":cap, "Z1":r["Z1"] if r["Z1"] else float('inf'),
                 "Z2":r["Z2"] if r["Z2"] else float('inf'), "status":r["status"]}
        results.append(entry)
        if r["Z1"]:
            print(f"  Diesel={cap:>3}MT | Rs{r['Z1']/1e7:>7,.0f}cr | {r['Z2']/1e9:.4f}Mt-CO2")
        else:
            print(f"  Diesel={cap:>3}MT | {r['status']}")
    for arc in D.ARCS: D.ARC_CAPACITY[arc] = base[arc]
    return results

def sensitivity_nagpur():
    import data as D
    hdr("STEP 5b — SENSITIVITY: Nagpur Transshipment Cost")
    base = D.TRANSSHIPMENT_COST[5]
    costs = [0, 60*1e6, 120*1e6, 180*1e6, 240*1e6, 300*1e6, 400*1e6]
    results = []
    for ts in costs:
        D.TRANSSHIPMENT_COST[5] = ts
        r = build_and_solve(objective="cost", use_mip=False)
        entry = {"nagpur_rs_tonne":ts/1e6, "Z1":r["Z1"] if r["Z1"] else float('inf'),
                 "Z1_ts":r.get("Z1_transship",0) or 0, "status":r["status"]}
        results.append(entry)
        if r["Z1"]:
            print(f"  Nagpur=Rs{ts/1e6:>4.0f}/t | Total Rs{r['Z1']/1e7:>7,.0f}cr | TS share={r['Z1_transship']/r['Z1']*100:.1f}%")
    D.TRANSSHIPMENT_COST[5] = base
    return results

def main():
    t0=time.time()
    print("\n"+"#"*65)
    print("#  CE 749 — Bi-Objective MCF for Indian Railway Freight")
    print("#  16-node Golden Quadrilateral + Diagonals Network")
    print("#  LP + Epsilon-Constraint | Transshipment + Backhaul")
    print("#"*65)

    hdr("PROBLEM STATISTICS")
    total_d = sum(DEMAND.values())
    print(f"  Nodes={len(NODES)} | Arcs={len(ARCS)} | Commodities=4 | OD pairs={len(DEMAND)}")
    print(f"  Total demand = {total_d} MT/year")
    for k,name in COMMODITIES.items():
        kd=sum(v for (kk,o,d),v in DEMAND.items() if kk==k)
        print(f"    {name:<14}: {kd} MT")
    print(f"\n  Model features: Real demand | Transshipment | Backhaul | LP+epsilon-constraint")

    # Step 1
    hdr("STEP 1 — COST-OPTIMAL SOLUTION")
    cost_opt = build_and_solve(objective="cost", use_mip=False)
    print_costs(cost_opt, "Cost-Optimal")
    print_flows(cost_opt["flows"])

    # Step 2
    hdr("STEP 2 — EMISSION-OPTIMAL SOLUTION")
    emis_opt = build_and_solve(objective="emission", use_mip=False)
    print_costs(emis_opt, "Emission-Optimal")
    cp = (emis_opt["Z1"]-cost_opt["Z1"])/cost_opt["Z1"]*100
    es = (cost_opt["Z2"]-emis_opt["Z2"])/cost_opt["Z2"]*100
    cost_diff_rs = emis_opt["Z1"] - cost_opt["Z1"]
    emis_diff_tonnes = (cost_opt["Z2"] - emis_opt["Z2"]) / 1000  # Z2 is in kg, convert to tonnes
    carbon_breakeven = cost_diff_rs / emis_diff_tonnes if emis_diff_tonnes > 0 else 0
    print(f"\n  -> Cost of going green: +{cp:.2f}%")
    print(f"  -> Emission saving:     -{es:.2f}%")
    print(f"  -> Carbon breakeven:    Rs {carbon_breakeven:.0f} / tCO2")

    # Step 3: Pareto
    hdr("STEP 3 — PARETO FRONTIER (Epsilon-Constraint)")
    pareto, c_opt, e_opt = generate_pareto_frontier(n_points=12, use_mip=False)
    print(f"\n  {'Pt':<4} {'Cost (Crore)':>14} {'CO2 (Mt)':>12} {'Cost+%':>8} {'EmSave%':>9}")
    print("  "+"-"*52)
    min_z1 = pareto[0]["Z1"]
    for i,p in enumerate(pareto):
        ex = (p["Z1"]-min_z1)/min_z1*100
        es2 = (pareto[-1]["Z2"]-p["Z2"])/pareto[-1]["Z2"]*100
        print(f"  {i+1:<4} {p['Z1']/1e7:>14,.0f} {p['Z2']/1e9:>12.4f} {ex:>+7.2f}% {es2:>8.2f}%")

    # Step 4: Heuristic
    hdr("STEP 4 — GREEDY HEURISTIC BENCHMARK")
    comparison = run_heuristic_comparison(cost_opt)

    # Step 5: Sensitivity
    sens_cap = sensitivity_capacity()
    sens_ts  = sensitivity_nagpur()

    # Step 6: Figures
    hdr("STEP 6 — GENERATING FIGURES")
    plot_network_flows(cost_opt["flows"], emis_opt["flows"])
    plot_pareto_frontier(pareto, comparison)
    plot_flow_distribution(cost_opt["flows"], "Cost-Optimal")
    plot_heuristic_comparison(comparison)
    valid = [r for r in sens_cap if r["Z1"]!=float('inf')]
    if len(valid)>=3: plot_sensitivity(valid)
    plot_cost_breakdown(cost_opt)
    plot_flow_comparison(cost_opt, emis_opt)

    # Save JSON
    summary = {
        "network": {"nodes":len(NODES),"arcs":len(ARCS),"od_pairs":len(DEMAND),"total_demand_MT":total_d},
        "cost_optimal": {"Z1_crore":round(cost_opt["Z1"]/1e7,0),"Z2_MtCO2":round(cost_opt["Z2"]/1e9,4),
                         "Z1_flow_crore":round(cost_opt["Z1_flow"]/1e7,0),
                         "Z1_transship_crore":round(cost_opt["Z1_transship"]/1e7,0),
                         "Z1_backhaul_crore":round(cost_opt["Z1_backhaul"]/1e7,0)},
        "emission_optimal": {"Z1_crore":round(emis_opt["Z1"]/1e7,0),"Z2_MtCO2":round(emis_opt["Z2"]/1e9,4)},
        "tradeoff": {"cost_penalty_pct":round(cp,2),"emission_saving_pct":round(es,2)},
        "pareto": [{"Z1_crore":round(p["Z1"]/1e7,0),"Z2_MtCO2":round(p["Z2"]/1e9,4)} for p in pareto],
        "heuristic": comparison,
    }
    with open("outputs/results_summary.json","w") as f: json.dump(summary,f,indent=2)

    hdr("COMPLETE")
    print(f"  Runtime: {time.time()-t0:.1f}s")
    print(f"\n  KEY RESULTS:")
    print(f"  Cost-optimal   : Rs {cost_opt['Z1']/1e7:,.0f} crore | {cost_opt['Z2']/1e9:.4f} Mt-CO2")
    print(f"  Emis-optimal   : Rs {emis_opt['Z1']/1e7:,.0f} crore | {emis_opt['Z2']/1e9:.4f} Mt-CO2")
    print(f"  Green penalty  : +{cp:.2f}%  |  Emission saving: -{es:.2f}%")
    print(f"  Carbon price   : Rs {carbon_breakeven:,.0f} / tCO2 breakeven")
    print(f"  Pareto points  : {len(pareto)}")
    print(f"  Heuristic gap  : {comparison['cost_gap_pct']:+.2f}% cost | {comparison['emission_gap_pct']:+.2f}% emissions")
    print(f"\n  Cost breakdown:")
    print(f"    Arc flow     : Rs {cost_opt['Z1_flow']/1e7:,.0f} crore ({cost_opt['Z1_flow']/cost_opt['Z1']*100:.1f}%)")
    print(f"    Transshipment: Rs {cost_opt['Z1_transship']/1e7:,.0f} crore ({cost_opt['Z1_transship']/cost_opt['Z1']*100:.1f}%)")
    print(f"    Backhaul     : Rs {cost_opt['Z1_backhaul']/1e7:,.0f} crore ({cost_opt['Z1_backhaul']/cost_opt['Z1']*100:.1f}%)")

if __name__ == "__main__":
    main()
