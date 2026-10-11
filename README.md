# ReliefQ — Quantum-Assisted Emergency Relief Resource Optimization

## Project Metadata

- **Project Title:** ReliefQ — Quantum-Assisted Emergency Relief Resource Optimization
- **Team Name:** QubitMind
- **Chosen Track:** Track 2: Open-Domain Optimization & Real-World Solvers
- **Video Presentation Link:** [Insert your public Google Drive / YouTube / Loom video link]
- **Live Demo:** https://reliefq-quantum.streamlit.app/
- **GitHub Repository:** https://github.com/balasatyamadhuri8-ops/quantumhack
- **Live Demo Timestamp in Video:** [00:00 — enter the time when the website demonstration begins]

## Team Members (Max 4 members)

| Name | Email | GitHub Username |
|---|---|---|
| Athili Bala Satya Madhuri | balasatyamadhuri8@gmail.com | balasatyamadhuri8-ops |

---

## 1. Project Overview & Motivation

- **Summary (3–4 sentences):**

  ReliefQ is a quantum-assisted decision-support prototype designed to optimize the distribution of limited emergency relief resources among affected villages during natural disasters and other emergencies. It considers resource availability, village requirements, and priority levels to identify feasible and useful allocation strategies. The project combines classical optimization with Qiskit-based exploration of the Quantum Approximate Optimization Algorithm (QAOA). ReliefQ demonstrates how quantum optimization techniques can be explored for real-world resource allocation challenges.

- **Why this problem / game?**

  During floods, cyclones, earthquakes, and other disasters, relief teams often face shortages of food kits, drinking water, medicines, and other essential supplies. Different villages may have different requirements and urgency levels, making resource distribution a challenging optimization problem. ReliefQ models this challenge mathematically and explores ways to distribute limited resources while considering demand and priority. The project connects quantum computing with a meaningful humanitarian problem.

## 2. Quantum Architecture & Mechanics

- **Core Quantum Principles Used:**

  ReliefQ explores the Quantum Approximate Optimization Algorithm (QAOA), a hybrid quantum-classical algorithm designed for combinatorial optimization problems.

  The relevant quantum concepts include:

  - **Superposition:** Hadamard gates can prepare qubits in superposition, allowing multiple computational basis states to contribute to the quantum state.
  - **Quantum Interference:** Parameterized quantum operations influence the probabilities of candidate solutions.
  - **Measurement:** The quantum circuit produces classical measurement outcomes that can be interpreted as candidate solutions.
  - **Cost Hamiltonian:** The optimization objective and constraints can be represented using a cost function or Hamiltonian.
  - **Hybrid Optimization:** A classical optimizer can update circuit parameters based on the measured objective values.

- **How the Quantum Circuit is Integrated:**

  The relief allocation problem is represented through decision variables describing resource distribution among villages. Resource availability, demand limits, and priority scores define the optimization objective and constraints.

  Qiskit provides the quantum circuit and simulation framework for exploring QAOA-based candidate solutions. The candidate allocations can be evaluated against the modeled constraints and compared with a classical optimization baseline. The Streamlit application provides an accessible interface for exploring the problem and viewing allocation results.

  QAOA is used as an experimental optimization approach. The project does not assume quantum advantage or claim that quantum computing always outperforms classical methods.

- **Circuit Details:**

  - **Number of Qubits:** Depends on the decision-variable encoding and optimization instance implemented in `app.py`.
  - **Key Gates Used:** Report the gates actually implemented in the QAOA circuit, such as Hadamard, parameterized rotation, problem-dependent phase, and measurement operations where applicable.
  - **Primitives Used:** Report the Qiskit circuit execution, simulator, or sampler interfaces actually used by the application.
  - **Other Technologies Used:** Python, Streamlit, Qiskit, and classical optimization logic.

  The exact circuit configuration and quantum implementation should be verified against the submitted source code.

## 3. Repository Structure & How to Run

### Project Structure

```text
quantumhack/
├── app.py
├── requirements.txt
└── README.md
```

- **`app.py`** — Main Python application containing the ReliefQ interface and implemented optimization workflow.
- **`requirements.txt`** — Lists the Python packages required to run the application.
- **`README.md`** — Documents the project, quantum approach, setup instructions, demonstration, and limitations.

### Installation & Execution Instructions

**Requirements:** Python and the dependencies listed in `requirements.txt`.

1. **Clone the repository:**

   ```bash
   git clone https://github.com/balasatyamadhuri8-ops/quantumhack.git
   cd quantumhack
   ```

2. **Create and activate a virtual environment (recommended):**

   On Windows:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   On macOS or Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   streamlit run app.py
   ```

   Streamlit will provide a local URL where the application can be opened in a browser.

**Online Demo:** https://reliefq-quantum.streamlit.app/

## 4. Implementation Walkthrough & Live Demo

- **Walkthrough of Gameplay / Optimization Pipeline:**

  1. **Define the emergency scenario:** Specify the available relief resources and the requirements of the affected villages.
  2. **Set priorities:** Provide priority values to represent the relative urgency of different villages.
  3. **Model the allocation problem:** Define decision variables, resource limits, demand constraints, and the optimization objective.
  4. **Calculate candidate allocations:** Use the implemented classical optimization method and, where implemented, the Qiskit-based QAOA approach to explore possible allocations.
  5. **Validate feasibility:** Check whether the proposed allocation respects the available resource limit and village demand constraints.
  6. **Display results:** Present the allocation and its objective score through the ReliefQ interface.
  7. **Evaluate the outcome:** Compare the classical and quantum-assisted approaches using the same scenario and evaluation criteria, where both are implemented.

- **Key Screenshots / Terminal Output:**

  Include genuine screenshots from the running application showing:

  - ReliefQ's main interface.
  - Resource availability and village requirements.
  - Priority values used in the scenario.
  - Classical allocation results.
  - QAOA circuit, quantum measurement results, or quantum-assisted allocation results, if implemented.
  - Comparison of objective scores and feasibility.

  The screenshots and outputs should demonstrate the actual behavior of the submitted application.

## 5. Classical vs. Quantum Comparison

- **Classical Baseline / Counterpart:**

  The classical baseline evaluates possible allocations and selects a feasible solution with a high objective score. For small instances, exhaustive enumeration can be used to check feasible combinations and identify the best-scoring allocation.

  For example, consider 10 available food kits and two villages that each need up to 6 kits. If Village A has priority 10 and Village B has priority 4, a weighted objective can prioritize Village A while ensuring that the total allocation does not exceed the available supply.

- **Comparative Analysis:**

  ReliefQ provides a framework for examining classical optimization alongside quantum-assisted optimization. Both approaches should be evaluated using the same resource limits, demand requirements, priority values, and objective function.

  The comparison can include:

  - Total weighted priority score.
  - Number of resources allocated.
  - Demand satisfaction for each village.
  - Feasibility and constraint violations.
  - Execution time for the tested scenario.
  - Best objective value across repeated runs.

  The classical approach provides a reference for evaluating QAOA-generated candidate solutions. QAOA results may vary because of parameter selection, measurement sampling, circuit design, and optimization settings.

  The prototype does not claim a quantum speedup. Any performance advantage must be supported by reproducible experiments and comparable measurements.

## 6. Performance, Results & Limitations

- **Key Results & Observations:**

  ReliefQ demonstrates how limited emergency supplies can be modeled as an optimization problem involving resource constraints, village demand, and priority scores. The classical baseline provides a reference for evaluating feasible allocations, while the Qiskit-based component explores quantum-assisted optimization where implemented.

  Actual results should be reported using executed test scenarios, including the available resources, village requirements, resulting allocation, objective score, feasibility, and measured runtime.

  No experimental performance figures or quantum advantage claims are assumed in this README. Results should reflect the behavior of the submitted code.

- **Critical Reflection on Limitations:**

  ReliefQ is an experimental decision-support prototype and is not a replacement for professional emergency-response planning. The quality of its recommendations depends on accurate input data, appropriate priority values, and the assumptions used in the optimization model.

  Real-world emergency distribution also involves uncertain demand, transportation routes, changing weather conditions, storage capacity, fairness, and time constraints. These factors may not be fully represented in the prototype.

  QAOA can face limitations involving circuit depth, qubit requirements, measurement noise, parameter optimization, and hardware errors. Larger problems may require more sophisticated encodings and additional computational resources. A simulator-based experiment alone does not establish performance on real quantum hardware or demonstrate a practical quantum advantage.

  Future improvements could include geographic constraints, dynamic demand updates, fairness-aware allocation, uncertainty modeling, larger benchmark scenarios, and evaluation on quantum hardware where available.

## 7. References & Acknowledgments

- **Qiskit Documentation:** https://docs.quantum.ibm.com/
- **Qiskit Learning Resources:** https://learning.quantum.ibm.com/
- **Qiskit Optimization Documentation:** https://qiskit-community.github.io/qiskit-optimization/
- **Qiskit Aer Documentation:** https://qiskit.github.io/qiskit-aer/
- **IBM Quantum Learning:** https://quantum.cloud.ibm.com/learning
- **Streamlit Documentation:** https://docs.streamlit.io/

**Acknowledgments:** We thank the organizers of Qiskit Fall Fest 2026 and the IIIT Kottayam Quantum Hackathon for the opportunity to explore quantum computing and optimization. We also acknowledge the Qiskit and Python open-source communities for their tools and educational resources.

---

**Project:** ReliefQ — Quantum-Assisted Emergency Relief Resource Optimization

**Team:** QubitMind

**Disclaimer:** ReliefQ is an educational and experimental decision-support prototype. Its outputs are illustrative and should not be used as the sole basis for real emergency resource distribution without validation by qualified emergency-response personnel.
