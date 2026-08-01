# Guidelines for Writing Operations Research (OR) Projects on Resumes

Based on the analysis of senior M.Tech IEOR resumes, here are the key guidelines for structuring and writing impactful OR project descriptions, especially tailored for Course/Technical Projects vs. M.Tech Theses.

## 1. Structure of the Project Header
* **Format:** `Project Title | Project Type (Course Name/Self/Thesis) | Duration` 
* **Example:** `Bi-Objective Freight Allocation Optimization | Course Project: Transportation Planning | (Jan'25 - May'25)`

## 2. The Difference: M.Tech Thesis vs. Course Project
* **M.Tech Thesis:** 
  * Usually includes `Guide: Prof. [Name]`.
  * Starts with a broad **Objective** statement.
  * Highlights research novelty, algorithm development (e.g., custom heuristics, RL integration), real-world industry collaboration (e.g., Delhi Metro, Solar Park), and extensive literature review.
* **Course/Technical Project (Focus for your Indian Railways Project):**
  * Focuses heavily on the **application of concepts** taught in class.
  * Highlights the **mathematical formulation** (e.g., MILP, MCF, VRP), the **solver/tools** used, and the **scale** of the data.
  * Bullet points should directly state what was modeled, how it was solved, and the quantifiable business/technical impact.

## 3. The "STAR" Bullet Point Formula for OR
Each bullet point should answer: What did you do? How did you do it (tools/models)? What was the impact (metrics)?
* **Action Verb:** Modeled, Formulated, Optimized, Simulated, Developed, Evaluated.
* **Method/Tool:** MILP, MCF-LP, Epsilon-Constraint, Pyomo, PuLP, Gurobi, AnyLogic.
* **Impact/Metrics:** % reduction in cost/emissions, $ savings, execution time (3x faster), scale (10k+ variables).

## 4. Specific Rules for Your Indian Railways (CE 749) Project
Since you want to showcase this as a **Key Technical Project / Course Project**, follow these rules:

* **Rule 1: Highlight the Mathematical Model & Scale.** Explicitly mention that it's a Bi-Objective Multi-Commodity Flow Linear Program (MCF-LP). Mention the network scale (16-node Golden Quadrilateral, 50 arcs, 4 commodities).
* **Rule 2: Highlight the Constraints & Complexities.** OR recruiters look for complexity. Mention that you modeled *transshipment costs* and *backhaul/empty wagon repositioning* (which accounted for 25.8% of costs).
* **Rule 3: Emphasize the Trade-off Analysis.** Since it's a bi-objective model, mention the **Epsilon-Constraint method** and the **Pareto Frontier**. 
* **Rule 4: State Quantifiable Outcomes.** Use your exact metrics: e.g., "Achieved an 8.66% emission reduction for a 15.45% cost premium."
* **Rule 5: Mention Benchmarking.** State that you compared the LP optimal against a Greedy Shortest Path heuristic.
* **Rule 6: List the Tech Stack.** Python, PuLP (CBC Solver), Matplotlib (for spatial network maps).

## 5. Sample Resume Draft for Your Project
Here is how your Indian Railways project should look on your resume under Key Technical Projects:

**Bi-Objective Freight Allocation Optimization for Indian Railways** | *Course Project (CE 749)*
* **Formulated** a Bi-Objective Multi-Commodity Flow LP (MCF-LP) to optimize annual freight routing (435 MT) across a 16-node Golden Quadrilateral network, balancing cost and CO₂ emissions.
* **Modeled** complex logistics constraints including multi-modal traction (diesel vs. electric), junction transshipment, and empty-wagon backhaul penalties using **Python** and **PuLP (CBC Solver)**.
* **Implemented** the Epsilon-Constraint method to generate a 12-point **Pareto frontier**, revealing an optimal tradeoff of 8.66% emission reduction at a 15.45% cost premium.
* **Benchmarked** the exact LP solution against a custom **Greedy Shortest Path heuristic**, and visualized spatial flow distributions and capacity sensitivities using **Matplotlib**.
