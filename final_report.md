# CE 749 Project Report
## Bi-Objective Multi-Commodity Flow Optimization for Green Freight Allocation on Indian Railways

**Student:** Niraj (Roll No: 25M1528)  
**Course:** CE 749 — Freight Transportation Planning and Logistics, IIT Bombay  

---

## 1. Introduction and Motivation

Indian Railways (IR) is the fourth-largest freight rail network globally, carrying approximately 1,500 Million Tonnes (MT) of freight annually. The Golden Quadrilateral (GQ) and its diagonals form the high-density backbone of this network, handling a significant majority of the traffic. 

IR has set an ambitious target to achieve "Net-Zero" carbon emissions by 2030. While freight transportation contributes to ~70% of IR's revenue, it is also the primary source of its carbon footprint due to heavy reliance on diesel traction in non-electrified corridors. The fundamental challenge faced by planners is **how to route multi-commodity freight across a capacity-constrained network to minimize logistics costs while simultaneously controlling CO₂ emissions.**

Standard single-objective routing models typically ignore two structural inefficiencies:
1. **Transshipment Costs:** Delays and handling charges at marshalling yards.
2. **Backhaul Costs:** The expense of repositioning empty wagons after delivery, which constitutes a massive hidden cost in rail logistics.

This project addresses these gaps by formulating a Bi-Objective Multi-Commodity Flow Linear Program (MCF-LP) that explicitly models transshipment and backhaul costs, evaluates the cost-emission tradeoff using the $\epsilon$-constraint method, and benchmarks the optimal solution against current heuristic dispatching practices.

---

## 2. Methodology

### 2.1 Problem Definition
The problem is defined on a directed graph $G = (N, A)$ where $N$ represents major railway junctions/hubs and $A$ represents the railway corridors connecting them. A set of commodities $K$ must be transported from specific origins to destinations to satisfy an annual demand matrix.

### 2.2 Mathematical Formulation

**Sets and Indices:**
- $N$: Set of nodes (16 cities)
- $A$: Set of directed arcs (50 corridors)
- $K$: Set of commodities (Coal, Cement, Foodgrains, Fertilizers)

**Parameters:**
- $D_{k,o,d}$: Demand of commodity $k$ from origin $o$ to destination $d$ (in MT/year)
- $c_{k,ij}$: Unit transportation cost of commodity $k$ on arc $(i,j)$ (in Rs/tonne)
- $\varepsilon_{k,ij}$: Unit CO₂ emission of commodity $k$ on arc $(i,j)$ (in kgCO₂/tonne)
- $U_{ij}$: Annual carrying capacity of arc $(i,j)$ (in MT/year)
- $\tau_i$: Transshipment cost at node $i$ (in Rs/tonne)
- $r_k$: Revenue rate for commodity $k$ (in Rs/tonne-km)
- $dist_{ij}$: Distance of arc $(i,j)$ (in km)
- $b_{k,ij}$: Backhaul penalty multiplier for commodity $k$ on arc $(i,j)$

**Decision Variable:**
- $f_{k,ij}$: Continuous flow of commodity $k$ on arc $(i,j)$ (in MT)

**Objective 1: Minimize Total Logistics Cost ($Z_1$)**
The cost function incorporates standard arc flow costs, transshipment charges at intermediate nodes, and empty wagon repositioning (backhaul) costs.

\[ Z_1 = \sum_{k \in K} \sum_{(i,j) \in A} c_{k,ij} f_{k,ij} + \sum_{k \in K} \sum_{i \in N} \tau_i t_{k,i} + \sum_{k \in K} \sum_{(i,j) \in A} 0.4 \cdot r_k \cdot dist_{ij} \cdot b_{k,ij} \]

*Note: $t_{k,i}$ represents the through-flow of commodity $k$ at node $i$ (flow entering and leaving the node without being the origin or destination).*

**Objective 2: Minimize Total CO₂ Emissions ($Z_2$)**

\[ Z_2 = \sum_{k \in K} \sum_{(i,j) \in A} \varepsilon_{k,ij} f_{k,ij} \]

**Constraints:**

1. **Flow Conservation:**
For all $k \in K$ and $i \in N$:
\[ \sum_{j \mid (i,j) \in A} f_{k,ij} - \sum_{j \mid (j,i) \in A} f_{k,ji} = 
\begin{cases} 
\sum_{d} D_{k,i,d} & \text{if } i \text{ is an origin} \\
-\sum_{o} D_{k,o,i} & \text{if } i \text{ is a destination} \\
0 & \text{otherwise}
\end{cases} \]

2. **Arc Capacity Constraint:**
For all $(i,j) \in A$:
\[ \sum_{k \in K} f_{k,ij} \leq U_{ij} \]

3. **Non-Negativity:**
For all $k \in K$ and $(i,j) \in A$:
\[ f_{k,ij} \geq 0 \]

### 2.3 Solution Approach
The model is solved using the **$\epsilon$-constraint method** to generate the Pareto frontier. We minimize the primary objective ($Z_1$) while transforming the secondary objective ($Z_2$) into a constraint: $Z_2 \leq \epsilon$. By iteratively varying $\epsilon$ between the minimum and maximum possible emissions, we extract the exact tradeoff curve.

---

## 3. Results and Analysis

### 3.1 Network Overview
- **Network Size:** 16 nodes, 50 directed arcs.
- **Demand:** 435 MT/year across 28 Origin-Destination pairs.
- **Commodity Split:** Coal (260 MT), Cement (75 MT), Foodgrains (55 MT), Fertilizers (45 MT).

### 3.2 LP Optimal vs. Current Practice (Baseline)
To quantify the value of the optimization model, it was benchmarked against a **Greedy Shortest Path Heuristic**, which mirrors the current decentralized dispatching practices of Indian Railways zones (routing freight on the cheapest individual path without global capacity consideration).

| Metric | Current Practice (Greedy) | Proposed (MCF-LP Optimal) | Improvement |
| :--- | :--- | :--- | :--- |
| **Total Cost** | Rs 1,09,799 Crore | **Rs 99,614 Crore** | **10.22% (Rs 10,185 Cr saved)** |
| **Emissions** | 11.21 Mt-CO₂ | **10.22 Mt-CO₂** | **9.69% (0.99 Mt-CO₂ saved)** |

**Takeaway:** The exact LP optimization significantly outperforms heuristic routing, simultaneously saving over Rs 10,000 Crore annually and eliminating nearly 1 Million Tonnes of CO₂.

### 3.3 The Hidden Cost of Backhaul
Decomposing the cost-optimal objective value ($Z_1 = 99,614$ Crore) reveals a critical structural insight:
- **Arc Flow (Tariff):** Rs 64,201 Crore (64.4%)
- **Backhaul (Empty Wagons):** Rs 25,680 Crore (25.8%)
- **Transshipment (Yards):** Rs 9,733 Crore (9.8%)

**Takeaway:** Empty wagon repositioning accounts for **more than one-fourth** of the total logistics cost. Traditional single-objective models that ignore backhaul severely misrepresent the true cost of rail freight.

### 3.4 The Cost-Emission Tradeoff (Pareto Frontier)
The $\epsilon$-constraint method generated 12 unique Pareto-efficient solutions ranging from the cost-optimal extreme to the emission-optimal extreme.

- **Cost-Optimal Solution:** Rs 99,614 Crore | 10.22 Mt-CO₂
- **Emission-Optimal Solution:** Rs 1,15,001 Crore | 9.34 Mt-CO₂

**Takeaway:** Indian Railways can achieve an **8.66% reduction in emissions** by incurring a **15.45% cost premium**. This quantifies the "price of green." The implied **Carbon Breakeven Price** is **Rs 1,73,930 per tonne of CO₂**. Below this carbon tax threshold, cost-optimal routing remains strictly cheaper than green routing.

### 3.5 Sensitivity Analysis: Diesel Capacity
Sensitivity analysis on diesel arc capacities demonstrated that tightening diesel capacity below 70 MT forces traffic onto longer electrified routes, sharply increasing costs. At 70 MT, the system operates at an inflection point where cost efficiency is maximized without aggressively restricting flows. 

---

## 4. Conclusion

This project successfully developed and implemented a Bi-Objective Multi-Commodity Flow model for the Indian Railways Golden Quadrilateral network. 

**Key Contributions:**
1. Proved that centralized LP optimization saves **10.22% in costs** and **9.69% in emissions** over current heuristic dispatching.
2. Uncovered that **empty wagon backhaul accounts for 25.8% of logistics costs**, highlighting the need for better rake repositioning strategies.
3. Quantified the exact tradeoff for decarbonization, showing that an 8.66% emission cut requires a 15.45% cost increase, providing policymakers with a precise **Rs 1.74 Lakh/tCO₂ carbon breakeven price** to justify future electrification investments. 

The full implementation, written in Python using PuLP, is highly scalable and establishes a rigorous quantitative foundation for green freight logistics planning.
