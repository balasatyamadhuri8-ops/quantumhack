import itertools
import math
import time
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ReliefQ | Emergency Resource Optimizer", page_icon="🌐", layout="wide", initial_sidebar_state="expanded")

NAVY = "#16324F"
TEAL = "#16A6A1"
BLUE = "#4F86C6"
ORANGE = "#F4A261"
PALE = "#F3F7FB"

st.markdown("""
<style>
.block-container{padding-top:1.15rem;padding-bottom:2rem;max-width:1500px}
[data-testid="stSidebar"]{background:#16324F}
[data-testid="stSidebar"] *{color:#fff}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#d9e7f3}
h1,h2,h3{color:#16324F}
.hero{background:linear-gradient(115deg,#16324F,#225578);padding:22px 26px;border-radius:18px;color:white;margin-bottom:18px}
.hero h1{color:white;margin:0;font-size:2rem}.hero p{color:#dbe8f3;margin:7px 0 0 0}
.kpi{background:#f3f7fb;border:1px solid #e1eaf2;border-radius:14px;padding:15px 17px;min-height:105px}
.kpi-label{color:#60758a;font-size:.84rem}.kpi-value{color:#16324F;font-size:1.75rem;font-weight:750;margin-top:5px}.kpi-sub{color:#728499;font-size:.78rem;margin-top:2px}
.section-note{color:#65788b;font-size:.88rem}
div[data-testid="stMetric"]{background:#f3f7fb;border:1px solid #e1eaf2;padding:12px 14px;border-radius:13px}
.stButton>button{border-radius:9px;font-weight:650}
hr{border-color:#e5edf4}
</style>
""", unsafe_allow_html=True)

DEFAULTS = [
    {"Village":"Tuni", "Latitude":17.35, "Longitude":82.55, "Food demand":6, "Water demand":8, "Urgency (1-10)":9},
    {"Village":"Visakhapatnam", "Latitude":17.69, "Longitude":83.22, "Food demand":5, "Water demand":7, "Urgency (1-10)":7},
    {"Village":"Srikakulam", "Latitude":18.30, "Longitude":83.90, "Food demand":4, "Water demand":5, "Urgency (1-10)":8},
]

if "villages" not in st.session_state:
    st.session_state.villages = DEFAULTS.copy()
if "page" not in st.session_state:
    st.session_state.page = "Operational Overview"
if "last_results" not in st.session_state:
    st.session_state.last_results = None

with st.sidebar:
    st.markdown("# ◈ ReliefQ")
    st.caption("QUANTUM-ASSISTED EMERGENCY RELIEF")
    st.divider()
    page = st.radio("NAVIGATION", ["Operational Overview", "Scenario Builder", "Resource Allocation", "Quantum vs Classical", "Benchmark Lab", "Analytics & Map", "About ReliefQ"], key="page")
    st.divider()
    st.markdown("**SYSTEM STATUS**")
    st.markdown("🟢 Interactive scenario builder")
    st.markdown("🔵 Exact classical baseline")
    st.markdown("🟡 QAOA simulator runs on CPU")
    st.caption("Educational prototype · Not for live emergency decisions")

st.markdown(f"""<div class="hero"><h1>ReliefQ</h1><p>Quantum-Assisted Emergency Relief Resource Optimization</p><p>Prioritize affected communities, allocate limited supplies, and compare an exact classical baseline with a Qiskit QAOA candidate.</p></div>""", unsafe_allow_html=True)

# Scenario controls are always available in an expander so any page can use the same live scenario.
with st.expander("⚙️ Configure emergency scenario", expanded=(page == "Scenario Builder")):
    top1, top2, top3, top4 = st.columns([1,1,1,1.2])
    with top1:
        food_supply = st.number_input("Available food kits", min_value=0, value=int(st.session_state.get("food_supply", 10)), step=1, key="food_supply")
    with top2:
        water_supply = st.number_input("Available water packs", min_value=0, value=int(st.session_state.get("water_supply", 12)), step=1, key="water_supply")
    with top3:
        village_count = st.number_input("Number of villages", min_value=1, value=len(st.session_state.villages), step=1, key="village_count")
    with top4:
        st.caption("Choose as many villages as your scenario requires. Very large scenarios may be limited by browser or cloud resources.")
    current = st.session_state.villages[:int(village_count)]
    while len(current) < int(village_count):
        i = len(current) + 1
        current.append({"Village":f"Village {i}","Latitude":17.0 + i*0.18,"Longitude":82.0 + i*0.16,"Food demand":3,"Water demand":3,"Urgency (1-10)":5})
    edit_df = pd.DataFrame(current, columns=["Village","Latitude","Longitude","Food demand","Water demand","Urgency (1-10)"])
    st.markdown("**Village demand and location editor**")
    st.caption("Coordinates are decimal degrees. Example: Tuni ≈ 17.35 latitude, 82.55 longitude.")
    try:
        edited = st.data_editor(edit_df, use_container_width=True, hide_index=True, num_rows="fixed", key="village_editor", column_config={
            "Village": st.column_config.TextColumn("Village name", required=True),
            "Latitude": st.column_config.NumberColumn("Latitude", min_value=-90.0, max_value=90.0, format="%.4f", required=True),
            "Longitude": st.column_config.NumberColumn("Longitude", min_value=-180.0, max_value=180.0, format="%.4f", required=True),
            "Food demand": st.column_config.NumberColumn("Food kits needed", min_value=0, step=1, required=True),
            "Water demand": st.column_config.NumberColumn("Water packs needed", min_value=0, step=1, required=True),
            "Urgency (1-10)": st.column_config.NumberColumn("Urgency (1–10)", min_value=1, max_value=10, step=1, required=True),
        })
    except Exception:
        edited = st.dataframe(edit_df, use_container_width=True, hide_index=True)
        edited = edit_df
    st.session_state.villages = edited.to_dict("records") if isinstance(edited, pd.DataFrame) else current
    st.caption("Use the sidebar to switch sections. Your current scenario feeds the overview, charts, map, and allocation model.")

villages = pd.DataFrame(st.session_state.villages)
for col in ["Food demand", "Water demand", "Urgency (1-10)"]:
    villages[col] = pd.to_numeric(villages[col], errors="coerce").fillna(0).astype(int).clip(lower=0)
villages["Urgency (1-10)"] = villages["Urgency (1-10)"].clip(1,10)
villages["Latitude"] = pd.to_numeric(villages["Latitude"], errors="coerce").fillna(0.0).clip(-90,90)
villages["Longitude"] = pd.to_numeric(villages["Longitude"], errors="coerce").fillna(0.0).clip(-180,180)
villages["Village"] = villages["Village"].astype(str).replace("", "Unnamed village")
food_demand = int(villages["Food demand"].sum())
water_demand = int(villages["Water demand"].sum())
food_allocatable = min(int(food_supply), food_demand)
water_allocatable = min(int(water_supply), water_demand)

# The discrete exact baseline chooses individual kits, respecting demand and total supply.
def exact_allocate(demands, urgency, supply):
    demands = [int(max(0,x)) for x in demands]
    urgency = [int(max(1,x)) for x in urgency]
    supply = int(max(0,supply))
    n_units = sum(demands)
    start = time.perf_counter()
    # Unit-based exact search is intentionally bounded for demo scale.
    if n_units > 20:
        # Exact dynamic programming over villages and supply; preserves optimal objective for this objective.
        dp = {0:(0.0, [])}
        for i, demand in enumerate(demands):
            nxt = {}
            for used,(score,alloc) in dp.items():
                for q in range(min(demand,supply-used)+1):
                    new_used = used+q
                    cand = (score+q*urgency[i], alloc+[q])
                    if new_used not in nxt or cand[0] > nxt[new_used][0]: nxt[new_used] = cand
            dp = nxt
        used = min(supply,n_units)
        best_score, best_alloc = dp.get(used,(0.0,[0]*len(demands)))
        return best_alloc, best_score, time.perf_counter()-start, "dynamic programming exact baseline"
    units = [i for i,d in enumerate(demands) for _ in range(d)]
    target = min(supply, len(units))
    best_score = -1
    best_bits = None
    for bits in itertools.product((0,1), repeat=len(units)):
        if sum(bits) != target: continue
        score = sum(urgency[units[j]]*bits[j] for j in range(len(units)))
        if score > best_score:
            best_score, best_bits = score, bits
    allocation = [0]*len(demands)
    if best_bits is not None:
        for j,bit in enumerate(best_bits):
            if bit: allocation[units[j]] += 1
    return allocation, max(best_score,0), time.perf_counter()-start, "exact exhaustive baseline"

food_classic, food_score, food_time, food_method = exact_allocate(villages["Food demand"].tolist(), villages["Urgency (1-10)"].tolist(), food_supply)
water_classic, water_score, water_time, water_method = exact_allocate(villages["Water demand"].tolist(), villages["Urgency (1-10)"].tolist(), water_supply)
base_df = villages.copy()
base_df["Food allocated"] = food_classic
base_df["Food unmet"] = base_df["Food demand"] - base_df["Food allocated"]
base_df["Water allocated"] = water_classic
base_df["Water unmet"] = base_df["Water demand"] - base_df["Water allocated"]
base_df["Urgency-weighted delivery"] = base_df["Urgency (1-10)"] * (base_df["Food allocated"] + base_df["Water allocated"])

if page == "Operational Overview":
    st.subheader("Operational Overview")
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Villages monitored", len(villages))
    k2.metric("Food kits allocated", f"{sum(food_classic):,} / {int(food_supply):,}", f"{food_demand} requested")
    k3.metric("Water packs allocated", f"{sum(water_classic):,} / {int(water_supply):,}", f"{water_demand} requested")
    k4.metric("Urgent villages", int((villages["Urgency (1-10)"] >= 8).sum()), "urgency ≥ 8")
    left,right = st.columns([1.55,1])
    with left:
        st.markdown("#### Resource allocation overview")
        chart_df = base_df.melt(id_vars="Village", value_vars=["Food demand","Food allocated","Water demand","Water allocated"], var_name="Measure", value_name="Packs")
        fig = px.bar(chart_df, x="Village", y="Packs", color="Measure", barmode="group", color_discrete_sequence=[NAVY,TEAL,BLUE,ORANGE])
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",legend_title_text="",margin=dict(l=10,r=10,t=20,b=10),xaxis_title="",yaxis_title="Packs")
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("#### Urgency profile")
        fig = px.bar(base_df.sort_values("Urgency (1-10)"), x="Urgency (1-10)", y="Village", orientation="h", color="Urgency (1-10)", color_continuous_scale=["#cfe8e6",TEAL, NAVY], range_x=[0,10])
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",coloraxis_showscale=False,margin=dict(l=5,r=5,t=20,b=10),xaxis_title="Urgency (1–10)",yaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
    low,mid,high = st.columns(3)
    low.metric("Food unmet demand", int(base_df["Food unmet"].sum()))
    mid.metric("Water unmet demand", int(base_df["Water unmet"].sum()))
    high.metric("Weighted delivery score", f"{food_score+water_score:.0f}")
    st.markdown("#### Current scenario snapshot")
    st.dataframe(base_df[["Village","Urgency (1-10)","Food demand","Food allocated","Food unmet","Water demand","Water allocated","Water unmet"]], use_container_width=True, hide_index=True)
    st.caption("The current classical recommendation maximizes urgency-weighted allocations while respecting each village's demand and total supply. This objective does not yet include travel time, budget, or minimum-fairness constraints.")

elif page == "Scenario Builder":
    st.subheader("Scenario Builder")
    st.write("Set the village count, edit village names and coordinates, then adjust food/water demand and urgency in the scenario editor above.")
    st.info("Changes in the editor are used by the dashboard, allocation results, map, and analytics. Village count and demand inputs have no fixed application-level maximum; practical limits depend on available memory and runtime.")
    st.dataframe(villages, use_container_width=True, hide_index=True)
    st.markdown("#### Scenario validation")
    issues=[]
    if (villages["Village"].str.strip()=="").any(): issues.append("One or more village names are blank.")
    if villages["Village"].duplicated().any(): issues.append("Village names should be unique for readable charts.")
    if not issues: st.success("Scenario inputs look valid.")
    else:
        for issue in issues: st.warning(issue)

elif page == "Resource Allocation":
    st.subheader("Resource Allocation")
    st.markdown("#### Recommended distribution · exact classical baseline")
    st.dataframe(base_df[["Village","Urgency (1-10)","Food demand","Food allocated","Food unmet","Water demand","Water allocated","Water unmet"]], use_container_width=True, hide_index=True)
    col1,col2=st.columns(2)
    with col1:
        fdf=base_df.melt(id_vars="Village",value_vars=["Food allocated","Food unmet"],var_name="Status",value_name="Kits")
        fig=px.bar(fdf,x="Village",y="Kits",color="Status",barmode="stack",color_discrete_map={"Food allocated":TEAL,"Food unmet":"#E7A35E"},title="Food: allocated vs unmet")
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",legend_title_text="",xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        wdf=base_df.melt(id_vars="Village",value_vars=["Water allocated","Water unmet"],var_name="Status",value_name="Packs")
        fig=px.bar(wdf,x="Village",y="Packs",color="Status",barmode="stack",color_discrete_map={"Water allocated":BLUE,"Water unmet":"#E7A35E"},title="Water: allocated vs unmet")
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",legend_title_text="",xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
    st.markdown("#### Optimization objective")
    st.write("The prototype maximizes **urgency × delivered units** separately for food kits and water packs, subject to total supply and each village's stated demand.")
    st.caption(f"Food: {food_method} · {food_time:.6f} seconds. Water: {water_method} · {water_time:.6f} seconds. Times depend on the machine and current load.")
    csv=base_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download allocation report (CSV)", data=csv, file_name="reliefq_allocation_report.csv", mime="text/csv")

elif page == "Quantum vs Classical":
    st.subheader("Quantum vs Classical")
    st.write("QAOA searches for a high-utility food-kit allocation. The benchmark compares it with the exact classical optimum on the same instance.")
    st.warning("This version uses Qiskit's statevector simulator on a classical CPU. It evaluates QAOA quality; it does not by itself prove quantum advantage or quantum-hardware speedup.")

    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector
        from scipy.optimize import minimize
        qiskit_available = True
    except Exception as e:
        qiskit_available = False
        st.error("Qiskit or SciPy is unavailable. Check requirements.txt and the Streamlit deployment logs.")
        st.code(str(e))

    demands = villages["Food demand"].astype(int).tolist()
    urgencies = villages["Urgency (1-10)"].astype(int).tolist()
    supply = int(food_supply)
    units = [i for i, demand in enumerate(demands) for _ in range(demand)]
    n = len(units)
    target = min(supply, n)
    eligible = 1 <= n <= 12
    if not eligible:
        st.info(f"The statevector QAOA demo is limited to 1–12 food-demand units to keep browser/cloud memory and runtime manageable. Current unit count: {n}. The classical allocation remains available.")

    depth = st.select_slider("QAOA depth (p)", options=[1, 2, 3], value=2)
    restarts = st.select_slider("Independent parameter starts", options=[1, 3, 5], value=3)
    st.caption("The benchmark uses the same objective and constraints for both methods. QAOA uses a standard cost Hamiltonian with RZ/RZZ phase-separation gates and RX mixer gates; multiple initial parameter seeds reduce dependence on one lucky start.")

    if st.button("Run QAOA + benchmark", type="primary", disabled=(not eligible or not qiskit_available)):
        benefits = np.array([urgencies[i] for i in units], dtype=float)
        # C(x) = -utility(x) + P(sum(x)-target)^2. Expanding this gives
        # linear x_i terms and pairwise x_i*x_j terms, encoded as Z_i and Z_i Z_j.
        penalty = float(max(10, 2 * max(urgencies, default=1) * max(1, n)))
        linear_x = -benefits + penalty * (1 - 2 * target)
        pair_x = 2 * penalty

        def bits_idx(idx, count=n):
            return np.array([(idx >> i) & 1 for i in range(count)], dtype=int)

        def utility(bits):
            return float(np.dot(benefits, np.asarray(bits, dtype=float)))

        def objective(bits):
            return -utility(bits) + penalty * (int(np.sum(bits)) - target) ** 2

        def make_cost_terms(count):
            # Drop identity/global phase terms. H = sum(h_i Z_i) + sum(J_ij Z_i Z_j).
            h = np.zeros(count, dtype=float)
            J = {}
            for i in range(count):
                h[i] += -linear_x[i] / 2.0
            for i in range(count):
                for j in range(i + 1, count):
                    h[i] += -pair_x / 4.0
                    h[j] += -pair_x / 4.0
                    J[(i, j)] = pair_x / 4.0
            return h, J

        h, J = make_cost_terms(n)

        def circuit(params, p_depth):
            gammas = params[:p_depth]
            betas = params[p_depth:]
            qc = QuantumCircuit(n)
            qc.h(range(n))
            for layer in range(p_depth):
                gamma = float(gammas[layer])
                beta = float(betas[layer])
                # exp(-i gamma h_i Z_i) is RZ(2 gamma h_i).
                for q in range(n):
                    angle = 2.0 * gamma * h[q]
                    if abs(angle) > 1e-12:
                        qc.rz(angle, q)
                # exp(-i gamma J_ij Z_i Z_j) is RZZ(2 gamma J_ij).
                for (i, j), coeff in J.items():
                    angle = 2.0 * gamma * coeff
                    if abs(angle) > 1e-12:
                        qc.rzz(angle, i, j)
                for q in range(n):
                    qc.rx(2.0 * beta, q)
            return qc

        def expected_cost(params, p_depth):
            state = Statevector.from_instruction(circuit(params, p_depth))
            probs = np.asarray(state.probabilities())
            return float(sum(probs[idx] * objective(bits_idx(idx)) for idx in range(2 ** n)))

        # Exact optimum by enumerating all bitstrings (small demo instances only).
        start_classical = time.perf_counter()
        feasible_classical = [(utility(bits_idx(idx)), bits_idx(idx))
                              for idx in range(2 ** n)
                              if int(np.sum(bits_idx(idx))) == target]
        exact_score, exact_bits = max(feasible_classical, key=lambda item: item[0])
        classical_runtime = time.perf_counter() - start_classical

        start_qaoa = time.perf_counter()
        runs = []
        for run_id in range(restarts):
            rng = np.random.default_rng(210 + run_id)
            x0 = np.r_[rng.uniform(0, np.pi, depth), rng.uniform(0, np.pi / 2, depth)]
            result = minimize(expected_cost, x0, args=(depth,), method="COBYLA",
                              options={"maxiter": 80, "rhobeg": 0.6, "tol": 1e-3})
            state = Statevector.from_instruction(circuit(result.x, depth))
            probs = np.asarray(state.probabilities())
            feasible = []
            feasible_probability = 0.0
            for idx, probability in enumerate(probs):
                bits = bits_idx(idx)
                if int(np.sum(bits)) == target:
                    feasible_probability += float(probability)
                    feasible.append((utility(bits), float(probability), bits))
            if feasible:
                score, probability, bits = max(feasible, key=lambda item: (item[0], item[1]))
                runs.append({"run": run_id + 1, "score": score, "probability": probability,
                             "feasible_probability": feasible_probability, "bits": bits,
                             "optimizer_cost": float(result.fun), "success": bool(result.success)})
        q_runtime = time.perf_counter() - start_qaoa

        if not runs:
            st.error("QAOA did not produce a feasible bitstring in these runs. Try a different depth or scenario.")
        else:
            best = max(runs, key=lambda run: run["score"])
            q_score, q_bits = best["score"], best["bits"]
            q_alloc = [0] * len(demands)
            classical_alloc = [0] * len(demands)
            for j, bit in enumerate(q_bits):
                if bit:
                    q_alloc[units[j]] += 1
            for j, bit in enumerate(exact_bits):
                if bit:
                    classical_alloc[units[j]] += 1
            gap = 0.0 if exact_score == 0 else max(0.0, 100.0 * (exact_score - q_score) / exact_score)
            avg_score = float(np.mean([run["score"] for run in runs]))
            match_rate = sum(abs(run["score"] - exact_score) < 1e-9 for run in runs) / len(runs)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Exact classical optimum", f"{exact_score:.1f}")
            m2.metric("Best QAOA feasible score", f"{q_score:.1f}")
            m3.metric("Optimality gap", f"{gap:.1f}%")
            m4.metric("QAOA runs matching optimum", f"{match_rate:.0%}")

            compare = villages[["Village", "Food demand", "Urgency (1-10)"]].copy()
            compare["Exact classical allocation"] = classical_alloc
            compare["Best QAOA allocation"] = q_alloc
            st.dataframe(compare, use_container_width=True, hide_index=True)
            chart = compare.melt(id_vars="Village", value_vars=["Exact classical allocation", "Best QAOA allocation"],
                                 var_name="Method", value_name="Food kits")
            fig = px.bar(chart, x="Village", y="Food kits", color="Method", barmode="group",
                         color_discrete_sequence=[TEAL, BLUE], title="Same-instance allocation comparison")
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", legend_title_text="", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)

            b1, b2, b3 = st.columns(3)
            b1.metric("Exact solver runtime", f"{classical_runtime:.4f} s")
            b2.metric("Total QAOA simulation runtime", f"{q_runtime:.2f} s")
            b3.metric("Mean QAOA score across starts", f"{avg_score:.1f}")
            st.dataframe(pd.DataFrame([{k: run[k] for k in ["run", "score", "probability", "feasible_probability", "optimizer_cost", "success"]} for run in runs]),
                         use_container_width=True, hide_index=True)

            st.markdown("#### What this benchmark supports")
            if abs(q_score - exact_score) < 1e-9:
                st.success("The best QAOA candidate matched the exact classical objective on this instance.")
            else:
                st.info("QAOA did not reach the exact optimum on this instance. This is a valid benchmark result, not a failure of the comparison.")
            st.caption("Important: this is an algorithm-quality comparison on a classical CPU simulator. It is not evidence of quantum speedup. A quantum-advantage claim requires repeated, reproducible tests at suitable scales and a fair comparison with strong classical methods, ideally including quantum-hardware results where relevant.")

elif page == "Benchmark Lab":
    st.subheader("QAOA Benchmark Lab")
    st.write("Run repeatable small-instance experiments and compare QAOA quality with an exact classical optimum. This is research benchmarking, not proof of quantum advantage.")
    st.warning("All QAOA runs here use Qiskit's statevector simulator on a classical CPU. Runtime includes classical parameter optimization and simulation overhead.")
    try:
        from qiskit import QuantumCircuit
        from qiskit.quantum_info import Statevector
        from scipy.optimize import minimize
        bench_ready = True
    except Exception as e:
        bench_ready = False
        st.error(f"Qiskit/SciPy unavailable: {e}")

    bdepth = st.select_slider("Benchmark QAOA depth", options=[1, 2], value=1)
    biter = st.select_slider("COBYLA iterations per instance", options=[20, 40, 60], value=20)
    st.caption("The suite tests 4, 6, and 8 binary food-kit units. QAOA solutions are evaluated using 2,048 simulated measurement shots per instance; the code does not simply select the best feasible bitstring from the full statevector. Small sizes are deliberate because statevector memory grows exponentially.")

    if st.button("Run multi-size benchmark", type="primary", disabled=not bench_ready):
        records = []
        progress = st.progress(0)
        for case_no, nbits in enumerate([4, 6, 8], start=1):
            rng_case = np.random.default_rng(800 + nbits)
            benefits = rng_case.integers(2, 11, size=nbits).astype(float)
            target_count = max(1, nbits // 2)
            penalty = float(max(10, 2 * int(np.max(benefits)) * nbits))
            # Binary objective: maximize weighted units subject to exactly target_count selected.
            def bits_for(idx, count=nbits):
                return np.array([(idx >> i) & 1 for i in range(count)], dtype=int)
            def utility_for(bits):
                return float(np.dot(benefits, np.asarray(bits, dtype=float)))
            def objective_for(bits):
                return -utility_for(bits) + penalty * (int(np.sum(bits)) - target_count) ** 2
            linear_x = -benefits + penalty * (1 - 2 * target_count)
            pair_x = 2 * penalty
            h = np.zeros(nbits, dtype=float)
            couplings = {}
            for i in range(nbits):
                h[i] += -linear_x[i] / 2.0
            for i in range(nbits):
                for j in range(i + 1, nbits):
                    h[i] += -pair_x / 4.0
                    h[j] += -pair_x / 4.0
                    couplings[(i, j)] = pair_x / 4.0
            def make_circuit(params):
                gammas, betas = params[:bdepth], params[bdepth:]
                qc = QuantumCircuit(nbits)
                qc.h(range(nbits))
                for layer in range(bdepth):
                    for q in range(nbits):
                        angle = 2.0 * float(gammas[layer]) * h[q]
                        if abs(angle) > 1e-12:
                            qc.rz(angle, q)
                    for (i, j), coeff in couplings.items():
                        angle = 2.0 * float(gammas[layer]) * coeff
                        if abs(angle) > 1e-12:
                            qc.rzz(angle, i, j)
                    for q in range(nbits):
                        qc.rx(2.0 * float(betas[layer]), q)
                return qc
            def expected_cost(params):
                state = Statevector.from_instruction(make_circuit(params))
                probs = np.asarray(state.probabilities())
                return float(sum(probs[idx] * objective_for(bits_for(idx)) for idx in range(2 ** nbits)))

            t0 = time.perf_counter()
            exact_candidates = [(utility_for(bits_for(idx)), bits_for(idx)) for idx in range(2 ** nbits)
                                if int(np.sum(bits_for(idx))) == target_count]
            exact_score, _ = max(exact_candidates, key=lambda x: x[0])
            classical_seconds = time.perf_counter() - t0
            t1 = time.perf_counter()
            rng_params = np.random.default_rng(1200 + nbits)
            x0 = np.r_[rng_params.uniform(0, np.pi, bdepth), rng_params.uniform(0, np.pi / 2, bdepth)]
            opt = minimize(expected_cost, x0, method="COBYLA", options={"maxiter": int(biter), "rhobeg": 0.6, "tol": 1e-3})
            state = Statevector.from_instruction(make_circuit(opt.x))
            probs = np.asarray(state.probabilities(), dtype=float)
            # Evaluate actual finite-shot outcomes, rather than scanning every feasible
            # state in the simulator (which would leak an exhaustive-search advantage).
            shots = 2048
            rng_shots = np.random.default_rng(4200 + nbits)
            sampled_indices = rng_shots.choice(len(probs), size=shots, p=probs / probs.sum())
            sampled_feasible = [idx for idx in sampled_indices
                                if int(np.sum(bits_for(int(idx)))) == target_count]
            q_score = max((utility_for(bits_for(int(idx))) for idx in sampled_feasible), default=float("nan"))
            feasible_prob = sum(float(probs[idx]) for idx in range(2 ** nbits)
                                if int(np.sum(bits_for(idx))) == target_count)
            q_seconds = time.perf_counter() - t1
            gap = 0.0 if exact_score == 0 else max(0.0, 100.0 * (exact_score - q_score) / exact_score)
            records.append({"Binary units": nbits, "Selected units": target_count, "Classical optimum": exact_score,
                            "Best feasible QAOA score": q_score, "Optimality gap (%)": gap,
                            "Feasible-state probability (%)": 100.0 * feasible_prob,
                            "Exact classical time (s)": classical_seconds, "QAOA CPU simulation time (s)": q_seconds,
                            "COBYLA success flag": bool(opt.success)})
            progress.progress(case_no / 3)
        result_df = pd.DataFrame(records)
        st.dataframe(result_df, use_container_width=True, hide_index=True)

        # A transparent assessment panel: it evaluates evidence instead of assuming advantage.
        st.markdown("#### Quantum Advantage Assessment")
        total_classical = float(result_df["Exact classical time (s)"].sum())
        total_qaoa = float(result_df["QAOA CPU simulation time (s)"].sum())
        mean_gap = float(result_df["Optimality gap (%)"].mean())
        exact_matches = int((result_df["Optimality gap (%)"] <= 1e-9).sum())
        a1, a2, a3 = st.columns(3)
        a1.metric("Instances matching optimum", f"{exact_matches}/{len(result_df)}")
        a2.metric("Mean optimality gap", f"{mean_gap:.2f}%")
        a3.metric("QAOA / classical time", f"{total_qaoa / max(total_classical, 1e-12):.1f}×")
        st.warning("VERDICT: Quantum advantage is NOT established. QAOA here runs on a classical CPU statevector simulator, and these small instances are not sufficient to demonstrate quantum hardware speedup.")
        st.caption("This panel reports measured outcomes honestly. A defensible quantum-advantage claim requires a suitable real-QPU experiment and a fair comparison against competitive, tuned classical methods at relevant problem sizes.")

        st.download_button("Download benchmark results (CSV)", data=result_df.to_csv(index=False).encode("utf-8"),
                           file_name="reliefq_qaoa_benchmark.csv", mime="text/csv")
        st.markdown("#### How to interpret this")
        st.write("A zero optimality gap means the best feasible bitstring observed in finite-shot samples matched the exact objective on that test instance. It does not mean QAOA was faster. Compare timings cautiously: these are small instances, and the statevector simulator is classical.")
        st.info("Quantum advantage is not established by this experiment. A defensible claim needs repeatable results against strong tuned classical baselines at relevant scales and, where appropriate, real quantum-hardware tests.")

elif page == "Analytics & Map":
    st.subheader("Analytics & Geographic View")
    st.markdown("#### Village locations")
    map_df=base_df.copy()
    map_df["Hover details"] = map_df.apply(lambda r: f"Urgency {r['Urgency (1-10)']} · Food {r['Food allocated']}/{r['Food demand']} · Water {r['Water allocated']}/{r['Water demand']}",axis=1)
    fig=px.scatter_geo(map_df,lat="Latitude",lon="Longitude",hover_name="Village",hover_data={"Latitude":":.4f","Longitude":":.4f","Urgency (1-10)":True,"Food allocated":True,"Food demand":True,"Water allocated":True,"Water demand":True},color="Urgency (1-10)",size="Urgency (1-10)",color_continuous_scale=["#b8e3df",TEAL,NAVY],projection="natural earth",title="Configured village locations and urgency")
    fig.update_geos(fitbounds="locations", visible=True, showcountries=True, showland=True, landcolor="#f1f5f9", countrycolor="#cbd5e1")
    fig.update_layout(height=500,margin=dict(l=0,r=0,t=45,b=0),paper_bgcolor="white",geo_bgcolor="white",coloraxis_colorbar_title="Urgency")
    st.plotly_chart(fig,use_container_width=True)
    left,right=st.columns(2)
    with left:
        fig=px.pie(base_df,names="Village",values="Food allocated",hole=.55,title="Share of food allocation")
        fig.update_layout(paper_bgcolor="white",legend_title_text="")
        st.plotly_chart(fig,use_container_width=True)
    with right:
        fig=px.bar(base_df,x="Village",y=["Food unmet","Water unmet"],barmode="group",title="Unmet demand by village",color_discrete_sequence=[ORANGE,BLUE])
        fig.update_layout(plot_bgcolor="white",paper_bgcolor="white",legend_title_text="",xaxis_title="")
        st.plotly_chart(fig,use_container_width=True)
    st.caption("Map positions are based on the latitude/longitude values in Scenario Builder. Enter realistic coordinates for your scenario; the map does not verify real-world incident reports.")

else:
    st.subheader("About ReliefQ")
    st.markdown("""
**Problem statement**  
Emergency response teams have limited food and water supplies, while affected villages have different demand levels and urgency. ReliefQ is a decision-support prototype that helps explore transparent, urgency-aware allocations.

**Classical optimization**  
For each resource, the exact baseline maximizes urgency-weighted units delivered subject to available supply and each village's demand. Small instances use exhaustive search; larger instances use exact dynamic programming for this simplified objective.

**Quantum component**  
The Quantum vs Classical section uses Qiskit QAOA with a standard Z/ZZ cost Hamiltonian and statevector simulation for small food-kit instances (up to 12 demand units in the comparison page). Village count, resource supply, and demand inputs have no fixed application-level maximum, but the quantum simulator is deliberately bounded because statevector cost grows exponentially.

**Current prototype limitations**  
The demo uses user-entered scenario data, optimizes food and water separately, and does not yet model road distance, vehicle capacity, budgets, spoilage, or minimum-fairness guarantees. QAOA runs on a classical CPU; this is not quantum hardware and does not demonstrate quantum advantage. Validate real allocations with relief professionals before operational use.
""")
    st.markdown("#### Technology")
    tech1,tech2,tech3,tech4=st.columns(4)
    tech1.info("**UI & charts**\n\nStreamlit + Plotly")
    tech2.info("**Classical baseline**\n\nExact enumeration / DP")
    tech3.info("**Quantum algorithm**\n\nQiskit QAOA simulator")
    tech4.info("**Reporting**\n\nCSV export")

st.divider()
st.caption(f"ReliefQ prototype · Scenario updated {datetime.now().strftime('%d %b %Y, %H:%M')} · Educational decision-support only.")
