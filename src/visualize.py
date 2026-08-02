# CE 749 — visualize.py: All figures

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, os

OUT = "outputs"
os.makedirs(OUT, exist_ok=True)
CMAP = {1:"#E63946", 2:"#457B9D", 3:"#2A9D8F", 4:"#E9C46A"}
CNAME = {1:"Coal", 2:"Cement", 3:"Foodgrains", 4:"Fertilizers"}

def plot_pareto_frontier(pts, comparison=None):
    fig, ax = plt.subplots(figsize=(10,6))
    Z1 = [p["Z1"]/1e7 for p in pts]
    Z2 = [p["Z2"]/1e9 for p in pts]
    ax.plot(Z2, Z1, 'o-', color='#1D3557', lw=2.5, ms=8, label='Pareto Frontier', zorder=3)
    ax.scatter(Z2[0],  Z1[0],  s=150, color='#2A9D8F', zorder=5, marker='D',
               label=f'Emission-optimal')
    ax.scatter(Z2[-1], Z1[-1], s=150, color='#E63946', zorder=5, marker='D',
               label=f'Cost-optimal')
    if comparison:
        hZ1 = comparison["greedy"]["Z1"]/1e7
        hZ2 = comparison["greedy"]["Z2"]/1e9
        ax.scatter(hZ2, hZ1, s=200, color='#F4A261', zorder=5, marker='^',
                   label='Greedy Heuristic')
        ax.annotate('Greedy', (hZ2,hZ1), textcoords="offset points",
                    xytext=(8,-15), fontsize=9, color='#F4A261')
    ax.set_xlabel('Total CO₂ Emissions (Mt-CO₂)', fontsize=12)
    ax.set_ylabel('Total Transportation Cost (Rs Crore)', fontsize=12)
    ax.set_title('Pareto Frontier: Cost vs. Emissions\nBi-Objective MCF — Indian Railway Freight Allocation',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
    plt.tight_layout()
    p = f"{OUT}/fig1_pareto_frontier.png"
    plt.savefig(p, dpi=150, bbox_inches='tight'); plt.close()
    print(f"  Saved: {p}"); return p

def plot_flow_distribution(flows, suffix="Cost-Optimal"):
    from src.data import NODES
    fig, axes = plt.subplots(2,2,figsize=(14,10)); axes=axes.flatten()
    for idx,k in enumerate([1,2,3,4]):
        ax=axes[idx]; fk=flows.get(k,{})
        if not fk:
            ax.text(0.5,0.5,'No flow',ha='center',va='center'); continue
        items=sorted(fk.items(),key=lambda x:-x[1])
        vals=[v for _,v in items]
        labs=[f"{NODES[i]}→{NODES[j]}" for (i,j),_ in items]
        bars=ax.barh(labs,vals,color=CMAP[k],alpha=0.85,edgecolor='white')
        for bar,val in zip(bars,vals):
            ax.text(bar.get_width()+0.2, bar.get_y()+bar.get_height()/2,
                    f'{val:.1f}MT', va='center', fontsize=8)
        ax.set_xlabel('Flow (MT)',fontsize=10)
        ax.set_title(f'{CNAME[k]}',fontsize=11,fontweight='bold',color=CMAP[k])
        ax.grid(True,axis='x',alpha=0.3); ax.set_xlim(0,max(vals)*1.2)
    plt.suptitle(f'Freight Flow Distribution — {suffix}',fontsize=13,fontweight='bold')
    plt.tight_layout()
    p=f"{OUT}/fig2_flow_distribution.png"
    plt.savefig(p,dpi=150,bbox_inches='tight'); plt.close()
    print(f"  Saved: {p}"); return p

def plot_heuristic_comparison(comp):
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    cats=['Optimal (MCF-LP)','Greedy Heuristic']; cols=['#1D3557','#F4A261']
    for ax,(key,unit,div,lbl) in zip(axes,[("Z1","Rs",1e7,"Cost (Rs Crore)"),
                                            ("Z2","tCO₂",1e9,"Emissions (Mt-CO₂)")]):
        vals=[comp["optimal"][key]/div, comp["greedy"][key]/div]
        bars=ax.bar(cats,vals,color=cols,width=0.5,edgecolor='white',lw=1.5)
        for bar,v in zip(bars,vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.01,
                    f'{v:.2f}',ha='center',va='bottom',fontsize=10)
        gap=comp["cost_gap_pct"] if key=="Z1" else comp["emission_gap_pct"]
        ax.text(0.5,0.93,f'Gap: {gap:+.2f}%',transform=ax.transAxes,
                ha='center',fontsize=11,color='#E63946',fontweight='bold')
        ax.set_ylabel(lbl,fontsize=11); ax.grid(True,axis='y',alpha=0.3)
        ax.set_ylim(0,max(vals)*1.18)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    plt.suptitle('MCF-LP Optimal vs. Greedy Heuristic',fontsize=13,fontweight='bold')
    plt.tight_layout()
    p=f"{OUT}/fig3_heuristic_comparison.png"
    plt.savefig(p,dpi=150,bbox_inches='tight'); plt.close()
    print(f"  Saved: {p}"); return p

def plot_sensitivity(results):
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    caps=[r["capacity"] for r in results]
    z1s=[r["Z1"]/1e7 for r in results]
    z2s=[r["Z2"]/1e9 for r in results]
    for ax,(ys,lbl,col) in zip(axes,[(z1s,"Cost (Rs Crore)","#E63946"),
                                      (z2s,"Emissions (Mt-CO₂)","#1D3557")]):
        ax.plot(caps,ys,'o-',color=col,lw=2.5,ms=8)
        ax.axvline(70,color='gray',ls='--',alpha=0.6,label='Base (70 MT)')
        ax.set_xlabel('Arc Capacity (MT)',fontsize=11); ax.set_ylabel(lbl,fontsize=11)
        ax.legend(fontsize=9); ax.grid(True,alpha=0.3)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    plt.suptitle('Sensitivity Analysis: Arc Capacity vs. Objectives',
                 fontsize=13,fontweight='bold')
    plt.tight_layout()
    p=f"{OUT}/fig4_sensitivity.png"
    plt.savefig(p,dpi=150,bbox_inches='tight'); plt.close()
    print(f"  Saved: {p}"); return p

def plot_cost_breakdown(res):
    fig, ax = plt.subplots(figsize=(7,7))
    vals = [res.get("Z1_flow",0), res.get("Z1_transship",0), res.get("Z1_backhaul",0)]
    labels = ["Arc Flow Cost", "Transshipment Cost", "Backhaul Cost"]
    colors = ["#457B9D", "#F4A261", "#E63946"]
    
    if sum(vals) == 0:
        print("  WARNING: No breakdown available for plot_cost_breakdown.")
        return None
        
    ax.pie(vals, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors,
           wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
    ax.axis('equal')  
    plt.title('Total Cost Breakdown\n(Cost-Optimal Solution)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    p = f"{OUT}/fig5_cost_breakdown.png"
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {p}")
    return p

def plot_flow_comparison(cost_opt, emis_opt):
    from src.data import NODES
    fig, ax = plt.subplots(figsize=(10, 6))
    
    c_flow = {}
    e_flow = {}
    
    for k in [1,2,3,4]:
        for arc, val in cost_opt.get("flows", {}).get(k, {}).items():
            c_flow[arc] = c_flow.get(arc, 0) + val
        for arc, val in emis_opt.get("flows", {}).get(k, {}).items():
            e_flow[arc] = e_flow.get(arc, 0) + val
            
    arcs = list(set(list(c_flow.keys()) + list(e_flow.keys())))
    diff_arcs = [arc for arc in arcs if abs(c_flow.get(arc, 0) - e_flow.get(arc, 0)) > 1]
    diff_arcs.sort(key=lambda arc: abs(c_flow.get(arc, 0) - e_flow.get(arc, 0)))
    
    if not diff_arcs:
        print("  No significant flow differences found.")
        return None
        
    labels = [f"{NODES[i]}→{NODES[j]}" for (i,j) in diff_arcs]
    c_vals = [c_flow.get(arc, 0) for arc in diff_arcs]
    e_vals = [e_flow.get(arc, 0) for arc in diff_arcs]
    
    y = np.arange(len(diff_arcs))
    height = 0.35
    
    ax.barh(y - height/2, c_vals, height, label='Cost-Optimal', color='#E63946')
    ax.barh(y + height/2, e_vals, height, label='Emission-Optimal', color='#2A9D8F')
    
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Total Flow (MT)', fontsize=11)
    ax.set_title('Flow Rerouting: Cost vs Emission Optimal', fontsize=13, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(True, axis='x', alpha=0.3)
    
    plt.tight_layout()
    p = f"{OUT}/fig6_flow_comparison.png"
    plt.savefig(p, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {p}")
    return p
