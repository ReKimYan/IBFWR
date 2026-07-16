import os
import time
import numpy as np
import pandas as pd
import pyomo.environ as pyo
from pyomo.environ import *

# === Import custom model components ===
from SetParameterVariable import SetParameterVariableModel
from Grinding import GrindingModel
from InequalityConstraints import InequalityConstraintsModel
from VariableSelection import VariableSelectionModel
from UtilityChemical import UtilityChemicalConsumptionModel
from Biorefinery import BiorefineryModel
from FWManagement import FWManagementModel
from CarbonCapture import CarbonCaptureModel
from Cost import CostModel
from MOO import MOOModel


# ---------------------------
# SAFE VALUE FUNCTION
# ---------------------------
def safe_value(v):
    try:
        return pyo.value(v, exception=False)
    except:
        return None


def main():

    # ---------------------------
    # 1. MODEL
    # ---------------------------
    model = AbstractModel()

    SetParameterVariableModel(model)
    GrindingModel(model)
    InequalityConstraintsModel(model)
    VariableSelectionModel(model)
    UtilityChemicalConsumptionModel(model)
    BiorefineryModel(model)
    FWManagementModel(model)
    CarbonCaptureModel(model)
    CostModel(model)
    MOOModel(model)   # defines npv, GWPSavings, SIA (physics + economics only)

    # =========================================================
    # 2. AUGMECON  -  THREE-OBJECTIVE MAXIMIZATION FORMULATION
    # =========================================================
    #   max  NPV                         (main objective)
    #   s.t. GWPSavings >= eps_GWP        (LCA,  converted objective)
    #        SIA        >= eps_SI         (jobs, converted objective)
    # ---------------------------------------------------------

    # (a) swept epsilon levels  -  values set inside the loop
    model.eps_GWP = Param(within=Reals, mutable=True, initialize=0.0)
    model.eps_SI  = Param(within=Reals, mutable=True, initialize=0.0)

    # (b) normalization scales = single-objective maxima (known)
    model.r_GWP = Param(initialize=902000.0)   # LCA (GWPSavings) max
    model.r_SI  = Param(initialize=38200.0)    # job generation max

    # (c) non-negative slacks
    model.s_GWP = Var(within=NonNegativeReals)
    model.s_SI  = Var(within=NonNegativeReals)

    # (d) epsilon-constraints in slack (equality) form
    model.eps_con_GWP = Constraint(
        expr=model.GWPSavings - model.s_GWP == model.eps_GWP
    )
    model.eps_con_SI = Constraint(
        expr=model.SIA - model.s_SI == model.eps_SI
    )

    # (e) augmented objective: maximize NPV, reward the slacks
    model.aug = Param(initialize=1e-3)
    model.AUGMECON_obj = Objective(
        expr=model.npv + model.aug * (model.s_GWP / model.r_GWP +
                                      model.s_SI  / model.r_SI),
        sense=maximize
    )

    # ---------------------------
    # 3. DATA + INSTANCE
    # ---------------------------
    data = DataPortal()
    data.load(filename="Data_blending.dat", model=model)
    instance = model.create_instance(data)

    # ---------------------------
    # 4. SOLVER
    # ---------------------------
    opt = SolverFactory("scip")
    opt.options["limits/gap"] = 0.02
    opt.options["limits/time"] = 120

    # ---------------------------
    # 5. EPSILON GRID
    # ---------------------------
    # Upper ends = single-objective maxima you already computed.
    GWP_MAX = 902000.0    # LCA (GWPSavings) single-objective max
    SI_MAX  = 38200.0     # job generation single-objective max

    # Lower ends: start at 0 so the first points recover the max-NPV corner.
    # If GWPSavings at max-NPV is negative, set GWP_MIN below 0 to keep that
    # part of the front (SI_MIN can stay 0, jobs cannot be negative).
    GWP_MIN = 0.0
    SI_MIN  = 0.0

    steps = 10
    eps_GWP = np.linspace(GWP_MIN, GWP_MAX, steps)
    eps_SI  = np.linspace(SI_MIN,  SI_MAX,  steps)

    csv_file = "live_results_log.csv"

    if os.path.exists(csv_file):
        os.remove(csv_file)

    all_results = []

    # ---------------------------
    # 6. LOOP
    # ---------------------------
    for g in eps_GWP:
        for s in eps_SI:

            print(f"\nSolving GWP={g:.0f}, SI={s:.0f}")

            instance.eps_GWP.set_value(g)
            instance.eps_SI.set_value(s)

            start_time = time.time()
            results = opt.solve(instance, tee=False)
            runtime = time.time() - start_time

            status = str(results.solver.status)
            term = str(results.solver.termination_condition)

            is_feasible = term not in ["infeasible", "noSolution"]
            is_optimal = (
                results.solver.status == SolverStatus.ok and
                results.solver.termination_condition == TerminationCondition.optimal
            )

            # ---------------------------
            # MAIN RESULTS
            # ---------------------------
            result_dict = {
                "epsilon_GWP": g,
                "epsilon_SI": s,
                "status": status,
                "termination": term,
                "runtime_sec": runtime,
                "is_feasible": is_feasible,
                "is_optimal": is_optimal,

                "NPV": safe_value(instance.npv),
                "GWPsaving": safe_value(instance.GWPSavings),
                "SI": safe_value(instance.SIA),
                "slack_GWP": safe_value(instance.s_GWP),
                "slack_SI": safe_value(instance.s_SI),
                "BDO": safe_value(instance.TotalBDO),
                "LA": safe_value(instance.TotalLA),
                "SA": safe_value(instance.TotalSA),
                "Bioethanol": safe_value(instance.TotalBioethanol),
                "Butanol": safe_value(instance.TotalButanol),
                "Acetone": safe_value(instance.TotalAcetoneCoproduct),
                "H2": safe_value(instance.TotalH2Coproduct),
                "Ethanol": safe_value(instance.EthanolCoproduct),
                "Biodiesel": safe_value(instance.TotalBiodiesel),
                "Protein": safe_value(instance.TotalProtein),
                "BioCNG": safe_value(instance.TotalBioCNG),
                "CO2": safe_value(instance.TotalCO2),
                "Fertilizer": safe_value(instance.TotalFertilizer),
                "Glycerol": safe_value(instance.TotalGlycerol),
                "Electricity": safe_value(instance.ElectricityGenerated),
                "Compost": safe_value(instance.Compost_product),
                "Feed": safe_value(instance.Feed_product),
                "Opex": safe_value(instance.total_operating_cost),
                "Capex": safe_value(instance.total_capital_investment),
                "Revenue": safe_value(instance.total_product_revenue),
                "OrganicWaste": safe_value(instance.Organicwaste),
                "SolidWaste": safe_value(instance.SolidWaste),
                "FlueGas": safe_value(instance.FlueGasStream),
                "OffGas": safe_value(instance.OffgasStream),
            }

            # ---------------------------
            # INDEXED VARIABLES
            # ---------------------------
            for n in instance.FWManagementOption:
                result_dict[f"Finfeedstock_{n}"] = safe_value(instance.Finfeedstock[n])

            for n in instance.Macronutrients:
                result_dict[f"BlendFraction_{n}"] = safe_value(instance.BlendFraction[n])

            for fw in instance.FoodWasteCategory:
                result_dict[f"FWsupply_{fw}"] = safe_value(instance.FWsupply[fw])

            for bio in instance.Biochemicals:
                result_dict[f"ProcessBiochemicalSelected_{bio}"] = safe_value(instance.ProcessBiochemicalSelected[bio])

            for bf in instance.Biofuels:
                result_dict[f"ProcessBiofuelSelected_{bf}"] = safe_value(instance.ProcessBiofuelSelected[bf])

            # ---------------------------
            # SAVE ALWAYS
            # ---------------------------
            all_results.append(result_dict)

            pd.DataFrame([result_dict]).to_csv(
                csv_file,
                mode='a',
                header=not os.path.exists(csv_file),
                index=False
            )

            # ---------------------------
            # OPTIONAL SPEED BREAK
            # ---------------------------
            # Both sweeps ascend, so once a row is infeasible the tighter
            # SI points above it will be too -> skip the rest of the row.
            if not is_feasible:
                print("Infeasible region, skipping rest of this row")
                break

    # ---------------------------
    # 7. FINAL SAVE
    # ---------------------------
    df_all = pd.DataFrame(all_results)
    df_all.to_excel("Final_MOO_Analysis.xlsx", index=False)

    print("\nDONE")
    print(f"Total runs saved: {len(df_all)}")


if __name__ == "__main__":
    main()
