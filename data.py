# =============================================================================
# CE 749 — Input Data (FINAL — 16 nodes, correct units, real IR data)
# Source: IR Year Book 2022-23 | DFCCIL | SFC India GHG Report | MoR GoI | IEA
#
# UNIT CONVENTION (critical for Rs crore scale):
#   Demand  : MT (Million Tonnes) — IR standard unit
#   Rate    : Rs/tonne-km (official IR tariff)
#   COST[k][arc] = rate * 1e6 * distance  → Rs per MT
#   Z1 total : Rs → divide by 1e7 = crore
#   Z2 total : kgCO2 → divide by 1e6 = thousand tonnes CO2
# =============================================================================

NODES = {
    1:"Delhi",        2:"Mumbai",       3:"Chennai",      4:"Kolkata",
    5:"Nagpur",       6:"Bhopal",       7:"Hyderabad",    8:"Pune",
    9:"Ahmedabad",    10:"Kanpur",      11:"Bhubaneswar", 12:"Vijayawada",
    13:"Raipur",      14:"Jamshedpur",  15:"Ludhiana",    16:"Vizag"
}

COMMODITIES = {1:"Coal", 2:"Cement", 3:"Foodgrains", 4:"Fertilizers"}

# ─── ARC DISTANCES (km) — IR NTES ──────────────────────────────────────────
_BASE = {
    # Original 15 corridors
    (1,10):440,   (10,4):980,   (4,11):440,   (11,12):480,
    (12,3):430,   (3,7):630,    (7,8):560,    (8,2):190,
    (2,9):490,    (9,1):940,    (1,6):710,    (6,5):360,
    (5,7):500,    (5,4):1200,   (2,5):830,
    # New corridors: Raipur (13)
    (13,5):280,   # Raipur→Nagpur  (diesel, short cheap dirty — KEY CONFLICT)
    (13,4):620,   # Raipur→Kolkata (electric, longer clean)
    (13,6):420,   # Raipur→Bhopal  (diesel)
    # New corridors: Jamshedpur (14)
    (14,4):130,   # Jamshedpur→Kolkata (electric, very short)
    (14,11):300,  # Jamshedpur→Bhubaneswar (electric)
    # New corridors: Ludhiana (15) — EDFC northern terminus
    (15,1):310,   # Ludhiana→Delhi  (electric, EDFC/existing)
    (15,10):650,  # Ludhiana→Kanpur (electric, EDFC alignment)
    # New corridors: Vizag (16)
    (16,3):780,   # Vizag→Chennai   (electric, coastal)
    (16,7):430,   # Vizag→Hyderabad (diesel, shorter — KEY CONFLICT)
    (12,16):160,  # Vijayawada→Vizag (electric, coastal)
}
ARC_DISTANCES = {}
for (i,j),d in _BASE.items():
    ARC_DISTANCES[(i,j)] = d
    ARC_DISTANCES[(j,i)] = d
ARCS = list(ARC_DISTANCES.keys())

# ─── FREIGHT RATES (Rs/tonne-km) — Ministry of Railways GoI ────────────────
FREIGHT_RATE = {1:1.40, 2:0.90, 3:1.20, 4:1.10}

# ─── ARC TRACTION — IR Electrification Map 2023 ─────────────────────────────
# Key: diesel arcs are cheaper but emit 3.5x more CO2 → creates real conflict
ARC_TRACTION = {
    # Original network
    (1,10):"electric",  (10,1):"electric",
    (10,4):"electric",  (4,10):"electric",
    (4,11):"electric",  (11,4):"electric",
    (11,12):"diesel",   (12,11):"diesel",   # Bhubaneswar-Vijayawada: diesel
    (12,3):"electric",  (3,12):"electric",
    (3,7):"electric",   (7,3):"electric",
    (7,8):"diesel",     (8,7):"diesel",     # Hyderabad-Pune: diesel
    (8,2):"electric",   (2,8):"electric",
    (2,9):"electric",   (9,2):"electric",
    (9,1):"electric",   (1,9):"electric",
    (1,6):"electric",   (6,1):"electric",
    (6,5):"diesel",     (5,6):"diesel",     # Bhopal-Nagpur: diesel
    (5,7):"diesel",     (7,5):"diesel",     # Nagpur-Hyderabad: diesel SHORT CHEAP DIRTY
    (5,4):"diesel",     (4,5):"diesel",     # Nagpur-Kolkata: diesel SHORT CHEAP DIRTY
    (2,5):"electric",   (5,2):"electric",
    # New: Raipur
    (13,5):"diesel",    (5,13):"diesel",    # Raipur-Nagpur: diesel ← KEY CONFLICT
    (13,4):"electric",  (4,13):"electric",  # Raipur-Kolkata: electric (longer, clean)
    (13,6):"diesel",    (6,13):"diesel",    # Raipur-Bhopal: diesel
    # New: Jamshedpur
    (14,4):"electric",  (4,14):"electric",  # Jamshedpur-Kolkata: electric
    (14,11):"electric", (11,14):"electric", # Jamshedpur-Bhubaneswar: electric
    # New: Ludhiana (EDFC corridor — fully electrified)
    (15,1):"electric",  (1,15):"electric",
    (15,10):"electric", (10,15):"electric",
    # New: Vizag
    (16,3):"electric",  (3,16):"electric",  # Vizag-Chennai: coastal electric
    (16,7):"diesel",    (7,16):"diesel",    # Vizag-Hyderabad: diesel ← KEY CONFLICT
    (12,16):"electric", (16,12):"electric", # Vijayawada-Vizag: coastal electric
}

# ─── EMISSION FACTORS (kgCO2/tonne-km) ─────────────────────────────────────
# Source: SFC India GHG Default Values V1.0 (May 2025) + IPCC methodology
# Electric: 0.010 kgCO2/tonne-km (India grid 0.82 kgCO2/kWh, 2022-23 CEA)
# Diesel:   0.035 kgCO2/tonne-km (IPCC fuel factors + IR fuel consumption data)
# Ratio 3.5x — verified from SFC India document and Mongabay article
TRACTION_EMISSION = {"electric": 0.010, "diesel": 0.035}
ARC_EMISSION_RATE = {arc: TRACTION_EMISSION[ARC_TRACTION[arc]] for arc in ARCS}

# Commodity emission penalty (wagon drag, load efficiency)
COMMODITY_EMISSION_PENALTY = {1:1.25, 2:1.05, 3:0.88, 4:1.00}

# ─── COST & EMISSION MATRICES ───────────────────────────────────────────────
# COST[k][arc] = Rs per MT = rate(Rs/t-km) * 1e6(t/MT) * distance(km)
COST = {k: {arc: FREIGHT_RATE[k] * 1e6 * ARC_DISTANCES[arc]
            for arc in ARCS} for k in COMMODITIES}

# EMISSION[k][arc] = kgCO2 per MT
EMISSION = {k: {arc: ARC_EMISSION_RATE[arc] * ARC_DISTANCES[arc]
                     * COMMODITY_EMISSION_PENALTY[k] * 1e6
                for arc in ARCS} for k in COMMODITIES}

# ─── ARC CAPACITY (MT/year) ─────────────────────────────────────────────────
# Source: DFCCIL Annual Report + Railway Gazette (EDFC 153-250 MT design capacity)
# Electric DFC arcs: 200 MT (current operational capacity, 2022-23)
# Diesel/conventional: 70 MT (based on actual corridor utilization data)
# New short diesel arcs (Raipur-Nagpur etc): 60 MT
ARC_CAPACITY = {}
for arc in ARCS:
    trac = ARC_TRACTION[arc]
    dist = ARC_DISTANCES[arc]
    if trac == "electric":
        ARC_CAPACITY[arc] = 200
    elif dist <= 300:   # short diesel arcs — more constrained
        ARC_CAPACITY[arc] = 60
    else:
        ARC_CAPACITY[arc] = 70

# ─── TRANSSHIPMENT COSTS (Rs per MT passing through junction) ────────────────
# Source: IR Goods Tariff + NITI Aayog IR Efficiency Report 2021
# Scaled: base Rs/tonne * 1e6 = Rs/MT
TRANSSHIPMENT_COST = {
    1: 50*1e6,   2: 50*1e6,   3: 50*1e6,   4: 50*1e6,
    5:180*1e6,   6:120*1e6,   7:150*1e6,   8: 90*1e6,
    9: 80*1e6,  10: 70*1e6,  11: 90*1e6,  12:110*1e6,
    13:100*1e6,  14: 80*1e6,  15: 60*1e6,  16:120*1e6,
}

# Backhaul fraction — IR empty wagon positioning charge = 40% of loaded rate
BACKHAUL_FRACTION = 0.40

# Rake capacity (MT per rake) — IR Rolling Stock specifications
RAKE_CAPACITY = {1:0.0035, 2:0.0028, 3:0.0024, 4:0.0026}

# ─── OD DEMAND (MT/year) ────────────────────────────────────────────────────
# Source: IR Year Book 2022-23 zone-wise proportions + DFCCIL traffic projections
# Scale: GQ+diagonal subnetwork, annual planning horizon
#
# NATIONAL FY22-23: Coal 727 MT | Cement 144 MT | FG 71 MT | Fert 56 MT
# GQ corridor (~55%): Coal 400 | Cement 79 | FG 39 | Fert 31 MT
# Our 16-node subnetwork: ~65% of GQ flows
#
# KEY CONFLICT OD PAIRS (cheapest ≠ greenest path):
#   Raipur→Delhi:     diesel via Nagpur-Bhopal vs electric via Kolkata-Kanpur
#   Raipur→Kanpur:    diesel via Nagpur vs electric via Kolkata
#   Kolkata→Hyderabad:diesel via Nagpur vs electric via east coast
#   Mumbai→Kolkata:   diesel via Nagpur vs electric via Ahmedabad-Delhi-Kanpur
#   Vizag→Delhi:      diesel via Hyderabad-Nagpur-Bhopal vs electric via Chennai
# =============================================================================

DEMAND = {
    # ── COAL (260 MT) ────────────────────────────────────────────────────────
    # SECL mines (Raipur) → power plants nationwide
    (1, 13,  1): 60,   # Raipur→Delhi         ← STRONG CONFLICT (diesel Nagpur vs electric Kolkata)
    (1, 13, 10): 40,   # Raipur→Kanpur         ← CONFLICT
    (1, 13,  7): 30,   # Raipur→Hyderabad      (diesel via Nagpur, very short)
    # Jharia/Bokaro (Jamshedpur/Kolkata zone) → power plants
    (1,  4,  1): 50,   # Kolkata→Delhi         (electric trunk)
    (1,  4, 10): 30,   # Kolkata→Kanpur        (electric)
    (1, 14,  1): 20,   # Jamshedpur→Delhi      (electric via Kolkata)
    (1, 11,  7): 15,   # Bhubaneswar→Hyderabad ← CONFLICT (east coast vs Nagpur)
    (1, 15,  6): 15,   # Ludhiana→Bhopal       (FCI reverse → thermal plants MP)

    # ── CEMENT (75 MT) ────────────────────────────────────────────────────────
    (2,  2,  1): 15,   # Mumbai→Delhi          (electric WR)
    (2,  2,  7): 10,   # Mumbai→Hyderabad
    (2,  5,  4): 20,   # Nagpur→Kolkata        ← CONFLICT (diesel vs electric)
    (2,  5,  1): 10,   # Nagpur→Delhi
    (2,  3,  7): 10,   # Chennai→Hyderabad     ← CONFLICT
    (2, 13,  7):  5,   # Raipur→Hyderabad      (Raipur has cement plants — ACClaimed, OCL)
    (2,  5, 16):  5,   # Nagpur→Vizag          (diesel coastal)

    # ── FOODGRAINS (55 MT) ────────────────────────────────────────────────────
    (3, 15,  3): 15,   # Ludhiana→Chennai      ← STRONG CONFLICT (EDFC electric vs diesel)
    (3, 15,  7): 10,   # Ludhiana→Hyderabad    ← CONFLICT
    (3,  1,  3):  8,   # Delhi→Chennai
    (3,  1,  7):  6,   # Delhi→Hyderabad
    (3, 10,  7):  5,   # Kanpur→Hyderabad
    (3,  6,  4):  6,   # Bhopal→Kolkata        ← CONFLICT (diesel Nagpur vs electric Delhi)
    (3,  6,  3):  5,   # Bhopal→Chennai

    # ── FERTILIZERS (45 MT) ───────────────────────────────────────────────────
    (4,  2,  1): 10,   # Mumbai→Delhi          (electric)
    (4,  2,  4):  8,   # Mumbai→Kolkata        ← CONFLICT (Nagpur diesel vs north electric)
    (4, 16,  1): 10,   # Vizag→Delhi           ← STRONG CONFLICT (diesel Hyd-Nagpur vs electric Chennai)
    (4, 16, 10):  7,   # Vizag→Kanpur          ← CONFLICT
    (4,  3,  1):  5,   # Chennai→Delhi
    (4,  3, 10):  5,   # Chennai→Kanpur
}

# Round all demands to nearest integer MT (rakes are already ~integer at this scale)
# 1 MT of coal = 285 rakes — integer rounding of 1 MT is negligible
DEMAND = {k: round(v) for k,v in DEMAND.items()}
