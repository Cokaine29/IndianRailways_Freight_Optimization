# CE 749 — model.py FINAL: MCF-MIP with Transshipment + Backhaul
import pulp, numpy as np
from src.data import (NODES, COMMODITIES, ARCS, ARC_DISTANCES, FREIGHT_RATE,
                  COST, EMISSION, ARC_CAPACITY, DEMAND,
                  TRANSSHIPMENT_COST, BACKHAUL_FRACTION, RAKE_CAPACITY)

def build_and_solve(epsilon=None, objective="cost", use_mip=True):
    import time as _t; prob = pulp.LpProblem(f"MCF_{int(_t.time()*1e6)}", pulp.LpMinimize)

    # Integer rake counts (MT = n_rakes * rake_capacity)
    if use_mip:
        n = {k: {arc: pulp.LpVariable(f"n{k}_{arc[0]}_{arc[1]}", lowBound=0, cat="Integer")
                 for arc in ARCS} for k in COMMODITIES}
        f = {k: {arc: n[k][arc] * RAKE_CAPACITY[k] for arc in ARCS} for k in COMMODITIES}
    else:
        f = {k: {arc: pulp.LpVariable(f"f{k}_{arc[0]}_{arc[1]}", lowBound=0)
                 for arc in ARCS} for k in COMMODITIES}

    # Transshipment auxiliary
    t = {k: {i: pulp.LpVariable(f"t{k}_{i}", lowBound=0)
             for i in NODES} for k in COMMODITIES}

    # Backhaul auxiliary
    bv = {k: {arc: pulp.LpVariable(f"bv{k}_{arc[0]}_{arc[1]}", lowBound=0)
              for arc in ARCS} for k in COMMODITIES}

    Z1_flow     = pulp.lpSum(COST[k][arc]*f[k][arc]
                              for k in COMMODITIES for arc in ARCS)
    Z1_transship= pulp.lpSum(TRANSSHIPMENT_COST[i]*t[k][i]
                              for k in COMMODITIES for i in NODES)
    Z1_backhaul = pulp.lpSum(
        BACKHAUL_FRACTION * FREIGHT_RATE[k] * 1e6 * ARC_DISTANCES[arc] * bv[k][arc]
        for k in COMMODITIES for arc in ARCS)
    Z1 = Z1_flow + Z1_transship + Z1_backhaul

    Z2 = pulp.lpSum(EMISSION[k][arc]*f[k][arc]
                    for k in COMMODITIES for arc in ARCS)

    prob += (Z1 if objective=="cost" else Z2)

    for k in COMMODITIES:
        for i in NODES:
            out = pulp.lpSum(f[k][(i,j)] for (a,j) in ARCS if a==i)
            ins = pulp.lpSum(f[k][(j,i)] for (j,b_) in ARCS if b_==i)
            net = sum(d if o==i else (-d if dd==i else 0)
                      for (kk,o,dd),d in DEMAND.items() if kk==k)
            prob += (out - ins == net,   f"FC_{k}_{i}")
            prob += (t[k][i] >= ins+net, f"TS_{k}_{i}")

    for arc in ARCS:
        prob += (pulp.lpSum(f[k][arc] for k in COMMODITIES) <= ARC_CAPACITY[arc],
                 f"Cap_{arc[0]}_{arc[1]}")

    for k in COMMODITIES:
        for (i,j) in ARCS:
            if (j,i) in ARCS:
                prob += (bv[k][(i,j)] >= f[k][(i,j)] - f[k][(j,i)],
                         f"BH_{k}_{i}_{j}")

    if epsilon is not None:
        prob += (Z2 <= epsilon, "EpsCon")

    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=120))
    status = pulp.LpStatus[prob.status]
    if prob.status not in [1]:
        return {"status":status,"Z1":None,"Z2":None,"flows":None}

    if use_mip:
        flows = {k:{arc: round(pulp.value(n[k][arc])*RAKE_CAPACITY[k],4)
                    for arc in ARCS
                    if (pulp.value(n[k][arc]) or 0)>0.001}
                 for k in COMMODITIES}
    else:
        flows = {k:{arc:round(pulp.value(f[k][arc]),4) for arc in ARCS
                    if (pulp.value(f[k][arc]) or 0)>0.001}
                 for k in COMMODITIES}

    ts_val = sum(TRANSSHIPMENT_COST[i]*(pulp.value(t[k][i]) or 0)
                 for k in COMMODITIES for i in NODES)
    bh_val = sum(BACKHAUL_FRACTION*FREIGHT_RATE[k]*1e6*ARC_DISTANCES[arc]
                 *(pulp.value(bv[k][arc]) or 0)
                 for k in COMMODITIES for arc in ARCS)

    return {"status":status,
            "Z1":round(pulp.value(Z1),2),
            "Z1_flow":round(pulp.value(Z1_flow),2),
            "Z1_transship":round(ts_val,2),
            "Z1_backhaul":round(bh_val,2),
            "Z2":round(pulp.value(Z2),2),
            "flows":flows, "epsilon":epsilon}


def generate_pareto_frontier(n_points=12, use_mip=True):
    print("\n"+"="*60)
    print(f"GENERATING PARETO FRONTIER ({'MIP' if use_mip else 'LP'})")
    print("="*60)
    c = build_and_solve(objective="cost",     use_mip=use_mip)
    e = build_and_solve(objective="emission", use_mip=use_mip)

    if not c["Z1"] or not e["Z1"]:
        print("ERROR: extreme points infeasible"); return [],c,e

    Z2_max,Z2_min = c["Z2"],e["Z2"]
    print(f"  Cost-opt : Z1=Rs {c['Z1']/1e7:.0f}cr | Z2={c['Z2']/1e9:.4f} Mt-CO2")
    print(f"  Emis-opt : Z1=Rs {e['Z1']/1e7:.0f}cr | Z2={e['Z2']/1e9:.4f} Mt-CO2")
    print(f"  Cost penalty: +{(e['Z1']-c['Z1'])/c['Z1']*100:.2f}% | "
          f"Emis saving: {(Z2_max-Z2_min)/Z2_max*100:.2f}%")

    pareto = [{"Z1":e["Z1"],"Z2":e["Z2"],"flows":e["flows"],
               "Z1_flow":e["Z1_flow"],"Z1_transship":e["Z1_transship"],
               "Z1_backhaul":e["Z1_backhaul"]}]

    for eps in np.linspace(Z2_min, Z2_max, n_points)[1:-1]:
        print(f"  eps={eps/1e9:.4f}...", end=" ", flush=True)
        r = build_and_solve(epsilon=eps, objective="cost", use_mip=use_mip)
        if r["status"]=="Optimal":
            pareto.append(r)
            print(f"Z1=Rs {r['Z1']/1e7:.0f}cr | Z2={r['Z2']/1e9:.4f}")
        else:
            print(r["status"])

    pareto.append({"Z1":c["Z1"],"Z2":c["Z2"],"flows":c["flows"],
                   "Z1_flow":c["Z1_flow"],"Z1_transship":c["Z1_transship"],
                   "Z1_backhaul":c["Z1_backhaul"]})

    seen,unique=set(),[]
    for p in sorted(pareto,key=lambda x:x["Z2"]):
        key=(round(p["Z1"]/1e6,0), round(p["Z2"]/1e6,1))
        if key not in seen:
            seen.add(key); unique.append(p)

    print(f"\n  {len(unique)} unique Pareto points found.")
    return unique, c, e
