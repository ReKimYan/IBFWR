# Integrated Blended Food Waste BioRefinery (IBFWR)

A mixed-integer nonlinear programming (MINLP) framework for the optimal design of an **Integrated Blended Food Waste BioRefinery (IBFWR)** — a system that integrates conventional **food waste management** options (animal feed, composting, incineration, anaerobic digestion) with **biorefinery pathways** (biofuels and biochemicals) into a single optimisation framework.

The model is built in Python with [Pyomo](http://www.pyomo.org/) and solved with [SCIP](https://www.scipopt.org/).

The framework supports a triple-bottom-line analysis through three simultaneous objectives:

- Economic** — Net Present Value (NPV)
- Environmental** — Global Warming Potential savings (GWP)
- Social** — Job creation potential (Social Impact, SI)

The Pareto front of optimal trade-offs is generated using the **augmented ε-constraint method**.

---

## Object-Oriented Design

The model follows an **object-oriented programming (OOP)** approach. Each major part of the IBFWR is encapsulated in its own class, all operating on a single shared Pyomo `AbstractModel` instance. This makes the code modular, easy to extend, and easy to debug.

```
            ┌─────────────────────────────────┐
            │    SetParameterVariableModel    │  ← Sets, Params, Vars
            └─────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
   GrindingModel    InequalityConstraints   VariableSelectionModel
                            │
                            ▼
              UtilityChemicalConsumptionModel
                            │
                            ▼
                    BiorefineryModel
                            │
                            ▼
                    FWManagementModel
                            │
                            ▼
                   CarbonCaptureModel
                            │
                            ▼
                       CostModel
                            │
                            ▼
                       MOOModel
                            │
                            ▼
                  ε-constraint sweep in main.py
```

Each class takes the shared model as input, attaches its own constraints, and returns control to `main.py`. There is one source of truth (the model) and clean separation of concerns.

---

## Repository Structure

```
.
├── main.py                       # Entry point: runs the ε-constraint sweep
│
├── SetParameterVariable.py       # Sets, parameters, decision variables
├── Grinding.py                   # Pre-treatment (milling) constraints
├── InequalityConstraints.py      # Global feasibility constraints
├── VariableSelection.py          # Process selection (FW allocation, biofuel, biochemical)
├── UtilityChemical.py            # Utility & chemical consumption tracking
├── Biorefinery.py                # Core biorefinery process equations
├── FWManagement.py               # Composting / AD / incineration / animal feed
├── CarbonCapture.py              # CO2 capture and compression process
├── Cost.py                       # Capex / Opex calculations
├── MOO.py                        # Economic, Environmental, and Social Impact 
│
└── Data_blending.dat             # Sets, parameters, compositions, specific mass and energy, cost, prices, etc
```

---

## Methodology

### 1. The MINLP Model

The IBFWR is described as a mixed-integer nonlinear program with:

- **Continuous variables (0–1)** — allocation of food waste to each management/biorefinery pathway, biofuel pathway shares, biochemical pathway shares, flow rates, capacities, costs, and environmental burdens.
- **Binary variables** — used **only** for:
  - Tax indicator constraints (whether positive profit is realised in a given year, triggering taxation)
  - Regulatory compatibility constraints (e.g. fish and meat waste cannot be used for animal feed)
- **Constraints** — mass balances, conversion stoichiometry, demand limits, C/N ratio bounds for AD, capacity bounds, regulatory compatibility, product demand, and management-option-selection rule.



### 2. Multi-Objective Formulation

The augmented ε-constraint method is used:

```
maximize     NPV − ρ · (SI / SI*  +  GWP_emission / GWP*)
subject to   GWP_saving  ≤  ε_GWP
             SI          ≤  ε_SI
             [all biorefinery constraints]
```


### 3. Pareto Front Construction

`main.py` solves the MINLP at each point, and stores the resulting non-dominated solutions in a CSV / Excel file.

---

## Model Coverage

### Food waste categories
Bakery, fruit & vegetable, fish, meat, potato.

### Management options & products

| Management option           | Products                                                                  |
|-----------------------------|----------------------------------------------------------------------------|
| **Animal feed**             | Feed                                                                      |
| **Composting**              | Compost                                                                   |
| **Anaerobic digestion**     | Biomethane + fertilizer                                                   |
| **Incineration**            | Heat & power recovery (electricity)                                       |
| **Biorefinery**             | Biofuels and biochemicals (with co-products and captured CO₂)             |

### Biorefinery products
- **Biofuels:** bioethanol, biodiesel, biobutanol
- **Biochemicals:** lactic acid, succinic acid, 2,3-butanediol (BDO)
- **Co-products:** glycerol, acetone, hydrogen, fertilizer
- **Captured CO₂** from anaerobic digestion off-gas, fermentation, and incineration flue gas

### Carbon Capture
Amine-based absorption with PZ/MDEA solvent, distillation regeneration, and compression for sale or sequestration.

---

## Outputs

For every point in the ε-constraint grid, the model reports:

- **Economic:** NPV, total revenue, capex, opex
- **Environmental:** GWP savings, direct emissions, utility-related GWP, chemical-LCA GWP
- **Social:** total jobs (SI)
- **Material balances:** product yields (BDO, LA, SA, ethanol, butanol, biodiesel, etc.)
- **Process selections:** food-waste allocation across management options, biofuel and biochemical pathway shares
- **Waste streams:** organic waste, solid waste, flue gas, off-gas

---

## References

To be updated upon publication.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `pyomo` | Optimization modelling framework |
| `scip` | MINLP solver (external — install separately) |
| `pandas`, `numpy` | Data handling |
| `openpyxl` | Excel file writing |

---

## 📄 License

This project is released for academic and research purposes.
