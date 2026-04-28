# models/grinding_model.py
from pyomo.environ import *

class GrindingModel:
    """Grinding process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach grinding constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model

        def milling_composition_flow_rule(m, n, j, k):
            if n in ['Carbohydrate', 'Protein', 'Lipid'] and j == 'grinding' and k == 'Crusher':
                return m.Fmill_component[n, j, k] == sum(m.FWsupply[f] for f in m.FoodWasteCategory) * m.BlendFraction[n]
            else:
                return m.Fmill_component[n, j, k] == 0
        m.milling_composition_flow = Constraint(m.Macronutrients, m.Milling, m.Equipment, rule=milling_composition_flow_rule)
        




