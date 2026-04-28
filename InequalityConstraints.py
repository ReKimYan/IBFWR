# models/inequality_constraints.py
from pyomo.environ import *

class InequalityConstraintsModel:
    """Add global inequality constraints to the model."""

    def __init__(self, model):
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model

        ## -------------------------------
        # Food waste supply constraint
        # --------------------------------
        def FWSupply_rule(m,f):
            return   m.FWsupply[f] <= m.FWSupplyAvailability[f]
        m.FWsupplyConstraints = Constraint(m.FoodWasteCategory, rule=FWSupply_rule)      
        
        ## -------------------------------
        # Blend fraction constraint
        # --------------------------------
        def BlendFraction_rule(m, n): 
            return m.BlendFraction[n] == sum(m.FWsupply[f] * m.Composition[f,n] for f in m.FoodWasteCategory ) /  sum(m.FWsupply[f] for f in m.FoodWasteCategory)
        m.BlendFractionConstraints = Constraint(m.Macronutrients, rule=BlendFraction_rule)
        
        ## -------------------------------
        # Positive throughput
        # --------------------------------
        m.Epsilon = Param(initialize=1e-6)
        def PositiveThroughput_rule(m):
            return sum(m.FWsupply[f] for f in m.FoodWasteCategory) >= m.Epsilon
        m.PositiveThroughput = Constraint(rule=PositiveThroughput_rule)
        
        
        ## -------------------------------
        # Total blend constraint
        # --------------------------------
        def TotalBlend_rule(m):
            return sum(m.BlendFraction[n] for n in m.Macronutrients) == 1
        m.TotalBlendConstraint = Constraint(rule=TotalBlend_rule)
        
        # # -------------------------------
        # # Animal feed regulation
        # # --------------------------------       
        def Compatibility_rule(m, p, f):
            return m.FWsupply[f] <= m.BigM * (m.Allowed[p,f] + 1 - m.SelectProcess[p])
        m.CompatibilityConstraint = Constraint(m.FWManagementOption, m.FoodWasteCategory, rule=Compatibility_rule)
        
        def OneProcess_rule(m):
            return sum(m.SelectProcess[p] for p in m.FWManagementOption) == 1
        m.OneProcessConstraint = Constraint(rule=OneProcess_rule)
        
        # -------------------------------
        # C/N ratio constraint for composting and Anaerobic digestion 
        # --------------------------------
        m.CN_AD = Var(within=NonNegativeReals)
       
        # Anaerobic digestion C/N upper bound
        def CN_AD_upper_rule(m):
            C_total = sum(m.Finfeedstock[j] * (0.4   * m.BlendFraction['Carbohydrate'] + 0.531 * m.BlendFraction['Protein'] + 0.774 * m.BlendFraction['Lipid']) for j in m.FWManagementOption)
            N_total = sum( m.Finfeedstock[j] * (0.124 * m.BlendFraction['Protein']) for j in m.FWManagementOption)
            return C_total <= 35 * N_total
        m.CN_AD_upper = Constraint(rule=CN_AD_upper_rule)
        
        #Anaerobic digestion C/N lower bound
        def CN_AD_lower_rule(m):
            C_total = sum(m.Finfeedstock[j] * (0.4   * m.BlendFraction['Carbohydrate'] + 0.531 * m.BlendFraction['Protein'] + 0.774 * m.BlendFraction['Lipid']) for j in m.FWManagementOption)
            N_total = sum(m.Finfeedstock[j]  * (0.124 * m.BlendFraction['Protein']) for j in m.FWManagementOption)
            return C_total >= 25 * N_total
        m.CN_AD_lower = Constraint(rule=CN_AD_lower_rule)
        
        ## -------------------------------
        # Enzymatic hydrolysis capacity
        # --------------------------------
        def EH_capacity_bound_rule(m):
            FWsupply_EH = m.Finfeedstock['enzymatic-hydrolysis'] 
            return FWsupply_EH <= m.CapacityFWManagement['enzymatic-hydrolysis']
        m.EH_capacity_Constraint = Constraint(rule=EH_capacity_bound_rule)
        
        ## -------------------------------
        # Bioethanol
        # --------------------------------
        def Bioethanol_demand_upper_bound_rule(m):
            bioethanol_upper_product = sum(m.BioethanolProduct[ n, 'BioethanolProcess', 'Cooler'] for n in m.Components)
            return bioethanol_upper_product  <= m.ProductDemand ['bioethanol'] 
        m.BioethanoldemandUpperBoundConstraint = Constraint(rule=Bioethanol_demand_upper_bound_rule)
        
        ## -------------------------------
        # Lactic Acid 
        # --------------------------------
        def LacticAcid_demand_upper_bound_rule(m):
            lacticacid_upper_product = sum(m.LacticAcidProduct[ n, 'LacticAcidProcess','DT'] for n in m.Components)
            return lacticacid_upper_product  <= m.ProductDemand ['LacticAcid'] 
        m.LacticAciddemandUpperBoundConstraint = Constraint(rule=LacticAcid_demand_upper_bound_rule)
        
        # -------------------------------
        # Succinic Acid product
        # --------------------------------
        def SuccinicAcid_demand_upper_bound_rule(m):
            succinicacid_upper_product = sum(m.SuccinicAcidProduct [ n, 'SuccinicAcidProcess','Centrifugal'] for n in m.Components )
            return succinicacid_upper_product  <= m.ProductDemand['SuccinicAcid'] 
        m.SuccinicAciddemandUpperBoundConstraint = Constraint(rule=SuccinicAcid_demand_upper_bound_rule)
        
        ## -------------------------------
        # BDO product
        # --------------------------------
        def BDO_demand_upper_bound_rule(m):
            BDO_upper_product = sum(m.BDO_product [ n, 'BDOProcess','DT'] for n in m.Components )
            return BDO_upper_product  <=  m.ProductDemand['BDO'] 
        m.BDOdemandUpperBoundConstraint = Constraint(rule=BDO_demand_upper_bound_rule)
        
        ## -------------------------------
        # Butanol
        # --------------------------------
        def Butanol_demand_upper_bound_rule(m):
            butanol_upper_product = sum(m.Butanol_product [ n, 'ButanolProcess', 'DT'] for n in m.Components)
            return butanol_upper_product  <= m.ProductDemand ['Butanol'] 
        m.ButanoldemandUpperBoundConstraint = Constraint(rule=Butanol_demand_upper_bound_rule)
        
        ## -------------------------------
        # Biodiesel
        # --------------------------------
        def Biodiesel_demand_upper_bound_rule(m):
            biodiesel_upper_product = sum(m.Biodiesel_product [n,'BiodieselProcess','DT'] for n in m.Components)
            return biodiesel_upper_product  <= m.ProductDemand ['FAME'] 
        m.BiodieseldemandUpperBoundConstraint = Constraint(rule=Biodiesel_demand_upper_bound_rule)
        
        ## -------------------------------
        # Composting demand
        # --------------------------------
        def Composting_demand_bound_rule(m):
            Compost_product = m.Compost_product
            return Compost_product <= m.ProductDemand ['compost']
        m.Composting_demand_Constraint = Constraint(rule=Composting_demand_bound_rule)
        
        ## -------------------------------
        # AnimalFeed demand
        # --------------------------------
        def Feed_demand_bound_rule(m):
            Feed_product = m.Feed_product
            return Feed_product <= m.ProductDemand ['Feed']
        m.Feed_demand_Constraint = Constraint(rule=Feed_demand_bound_rule)
        
        #-------------------------------
        # BioCNG demand
        # -------------------------------
        def BioCNG_capacity_bound_rule(m):
            BioCNG_product = sum(m.BioCNG_product[ n,'AnaerobicDigestion']for n in m.Components)
            return BioCNG_product <= m.ProductDemand ['CH4']
        m.BioCNG_capacity_Constraint = Constraint(rule=BioCNG_capacity_bound_rule)
        
        #-------------------------------
        # Electricity capacity
        # -------------------------------        
        def Electricity_capacity_bound_rule(m):
            Electricity_product = m.ElectricityGenerated
            return Electricity_product <= m.ProductDemand ['electricity']
        m.Electricity_capacity_Constraint = Constraint(rule=Electricity_capacity_bound_rule)
        