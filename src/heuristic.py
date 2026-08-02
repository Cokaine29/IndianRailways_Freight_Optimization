# CE 749 — heuristic.py: Greedy Shortest Path Benchmark
import heapq
from src.data import NODES, COMMODITIES, ARCS, COST, EMISSION, DEMAND, TRANSSHIPMENT_COST, BACKHAUL_FRACTION, FREIGHT_RATE, ARC_DISTANCES

def dijkstra(source, weights):
    dist = {n: float('inf') for n in NODES}
    prev = {n: None for n in NODES}
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        for (i,j) in ARCS:
            if i == u:
                alt = dist[u] + weights.get((i,j), float('inf'))
                if alt < dist[j]:
                    dist[j] = alt; prev[j] = u
                    heapq.heappush(pq, (alt, j))
    paths = {}
    for node in NODES:
        path=[]; cur=node
        while cur is not None:
            path.append(cur); cur=prev[cur]
        paths[node] = list(reversed(path))
    return dist, paths

def greedy_heuristic():
    total_cost=0; total_emis=0
    flows={k:{} for k in COMMODITIES}
    for (k,o,d), demand in DEMAND.items():
        weights = {arc: COST[k][arc] for arc in ARCS}
        _, paths = dijkstra(o, weights)
        path = paths[d]
        if len(path) < 2: continue
        for idx in range(len(path)-1):
            arc = (path[idx], path[idx+1])
            if arc not in ARCS: continue
            flows[k][arc] = flows[k].get(arc,0) + demand
            total_cost   += COST[k][arc] * demand
            total_emis   += EMISSION[k][arc] * demand
            
    flows = {k:{arc:v for arc,v in flows[k].items() if v>0.001} for k in COMMODITIES}
    
    # Add transshipment and backhaul costs
    total_transship = 0
    total_backhaul = 0
    for k in COMMODITIES:
        for i in NODES:
            ins = sum(v for (u, v_node), v in flows[k].items() if v_node == i)
            net = sum(d if o==i else (-d if dd==i else 0) for (kk,o,dd),d in DEMAND.items() if kk==k)
            t_val = ins + net
            if t_val > 0:
                total_transship += TRANSSHIPMENT_COST[i] * t_val
                
        for (i, j) in ARCS:
            f_ij = flows[k].get((i, j), 0)
            f_ji = flows[k].get((j, i), 0)
            bv = f_ij - f_ji
            if bv > 0:
                total_backhaul += BACKHAUL_FRACTION * FREIGHT_RATE[k] * 1e6 * ARC_DISTANCES[(i,j)] * bv
                
    total_cost += total_transship + total_backhaul
    
    return {"Z1":round(total_cost,2), "Z2":round(total_emis,2), "flows":flows}

def run_heuristic_comparison(optimal):
    print("\n"+"="*60+"\nGREEDY HEURISTIC BENCHMARK\n"+"="*60)
    g = greedy_heuristic()
    oZ1,oZ2 = optimal["Z1"], optimal["Z2"]
    gZ1,gZ2 = g["Z1"], g["Z2"]
    cgap = (gZ1-oZ1)/oZ1*100
    egap = (gZ2-oZ2)/oZ2*100
    print(f"\n  {'Metric':<30} {'Optimal (LP)':>16} {'Greedy':>16} {'Gap':>8}")
    print("  "+"-"*72)
    print(f"  {'Total Cost (Rs Crore)':<30} {oZ1/1e7:>16,.0f} {gZ1/1e7:>16,.0f} {cgap:>+8.2f}%")
    print(f"  {'Total Emissions (Mt-CO2)':<30} {oZ2/1e9:>16,.4f} {gZ2/1e9:>16,.4f} {egap:>+8.2f}%")
    return {"optimal":{"Z1":oZ1,"Z2":oZ2},
            "greedy": {"Z1":gZ1,"Z2":gZ2},
            "cost_gap_pct":round(cgap,2),
            "emission_gap_pct":round(egap,2)}
