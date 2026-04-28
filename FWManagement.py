from pyomo.environ import *

# ======================================================
# Composting Model
# ======================================================
class CompostingModel:
    """Composting process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach composting constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Composting
        # --------------------------------        
        # Flow compost product
        def flow_composting_product_rule(m):
                return m.Compost_product == m.Finfeedstock['Composting']  * m.CompostYield['compost']
        m.flow_composting_product_rule = Constraint(rule=flow_composting_product_rule)

# ======================================================
# AnimalFeed Model
# ======================================================
class AnimalFeedModel:
    """AnimalFeed process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach AnimalFeed constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # AnimalFeed
        # --------------------------------        
        # Flow animalfeed product
        def flow_AnimalFeed_product_rule(m):
                return m.Feed_product == m.Finfeedstock['AnimalFeed'] * m.FeedYield['Feed']
        m.flow_AnimalFeed_product_rule = Constraint(rule=flow_AnimalFeed_product_rule)

# ======================================================
# Anaerobic Digestion Model
# ======================================================
class AnaerobicDigestionModel:
    """AnaerobicDigestion process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Anaerobic digestion constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Food waste consumption
        # --------------------------------        
        def flow_anaerobicdigestion_balance_rule(m, n, j, k):
            if n in ['Carbohydrate','Protein','Lipid'] and j =='AnaerobicDigestion' and k in ['Cooler', 'Digester']:
                return m.FAD[n,j,k] == m.Finfeedstock['AnaerobicDigestion'] * m.BlendFraction[n]
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return  m.FAD[n,j,k] == 0
            else:
                  return Constraint.Skip
        m.flow_anaerobicdigestion_balance_rule = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=flow_anaerobicdigestion_balance_rule)

        ## -------------------------------
        # Flow waste from biorefinery 
        # --------------------------------
        def flow_waste_balance_rule(m, n, j, k):
            if n in ['glucose','bioethanol','LacticAcid','MethylLactate','FAME','Lipid','SuccinicAcid','AceticAcid','ButyricAcid','Butanol'] and j =='AnaerobicDigestion' and k in ['Cooler', 'Digester']:
                return m.FWaste[n,j,k] == m.totalwaste_bioethanol [n,'BioethanolProcess'] + m.Lactic_waste [n,'LacticAcidProcess'] + m.totalwaste_biodiesel [n,'BiodieselProcess'] + m.Succinic_waste[n,'SuccinicAcidProcess'] + m.totalwaste_Butanol [n,'ButanolProcess']
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FWaste [n,j,k] == 0 
            else:
                  return Constraint.Skip
        m.flow_waste_balance_rule = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule= flow_waste_balance_rule)
        ## -------------------------------
        # Flow water waste from biorefinery 
        # --------------------------------
        # --------------------------------
        def Water_waste_balance_rule(m, n, j, k):
            if n in ['Water'] and j =='AnaerobicDigestion' and k in ['Cooler', 'Digester']:
                return m.FWaterWaste[n,j,k] == m.totalwaste_bioethanol [n,'BioethanolProcess'] + m.Lactic_waste [n,'LacticAcidProcess'] + m.totalwaste_biodiesel [n,'BiodieselProcess'] + m.Succinic_waste[n,'SuccinicAcidProcess'] + m.totalwaste_Butanol [n,'ButanolProcess']
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FWaterWaste[n,j,k] == 0 
            else:
                  return Constraint.Skip
        m.Water_waste_balance_rule = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule= Water_waste_balance_rule)

        ## -------------------------------
        # Initial moles (mass to moles) 
        # --------------------------------
        def Digester_initial_moles_rule(m, n, j, k):
            if n in ['Carbohydrate','Protein','Lipid','Water','glucose','bioethanol','LacticAcid','MethylLactate','FAME','SuccinicAcid','AceticAcid','ButyricAcid','Butanol'] and j =='AnaerobicDigestion' and k == 'Digester':
                return m.InitialMolesDigester[ n,j,k] ==  (m.FAD[ n, j, 'Digester'] + m.FWaste[n,j,'Digester']++ m.FWaterWaste[n,j,'Digester']) / m.MolecularWeightDigester[n]
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.InitialMolesDigester[ n,j,k] == 0  
            else:
                return Constraint.Skip
        m.DigesterInitialMolesConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment,rule=Digester_initial_moles_rule)
        # -------------------------------
        # Reaction-1
        # -------------------------------
        def reaction1_Digester_constraint_rule(m, n,  j, k):
            if n in ['CH4','CO2'] and j =='AnaerobicDigestion'and k == 'Digester':
                return m.MolesReactedDigester1[ n,  j, k] == m.StoichiometricCoeffDigester1[n] * m.ConversionFactorDigester['Carbohydrate'] * m.InitialMolesDigester[ 'Carbohydrate',j,'Digester']
            elif n in ['Carbohydrate','Water'] and j =='AnaerobicDigestion' and k == 'Digester':
                return  m.MolesReactedDigester1[ n, j, k]  == -m.StoichiometricCoeffDigester1[n] *  m.ConversionFactorDigester['Carbohydrate'] * m.InitialMolesDigester[ 'Carbohydrate',j,'Digester']
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return m.MolesReactedDigester1[ n, j, k] == 0  
            else:
                return Constraint.Skip
        m.Reaction1DigesterConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment,rule=reaction1_Digester_constraint_rule)
        # -------------------------------
        # Reaction-2
        # -------------------------------
        def reaction2_Digester_constraint_rule(m, n,  j, k):
            if n in ['CH4','CO2','NH3'] and j =='AnaerobicDigestion' and k == 'Digester':
                return m.MolesReactedDigester2[ n,  j, k] == m.StoichiometricCoeffDigester2[n] * m.ConversionFactorDigester['Protein'] * m.InitialMolesDigester[ 'Protein',j,'Digester']
            elif n in ['Protein','Water'] and j =='AnaerobicDigestion' and k == 'Digester':
                return  m.MolesReactedDigester2[ n,  j, k]  == -m.StoichiometricCoeffDigester2[n] *  m.ConversionFactorDigester['Protein'] * m.InitialMolesDigester[ 'Protein',j,'Digester'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return  m.MolesReactedDigester2[ n,  j, k]  == 0  
            else:
                return Constraint.Skip
        m.Reaction2DigesterConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment,rule=reaction2_Digester_constraint_rule)
        # -------------------------------
        # Reaction-3
        # -------------------------------
        def reaction3_Digester_constraint_rule(m, n,  j, k):
            if n in ['CH4','CO2'] and j =='AnaerobicDigestion' and k == 'Digester':
                return m.MolesReactedDigester3[ n,  j, k] == m.StoichiometricCoeffDigester3[n] * m.ConversionFactorDigester['Lipid'] * m.InitialMolesDigester[ 'Lipid',j,'Digester']
            elif n in ['Lipid','Water'] and j =='AnaerobicDigestion' and k == 'Digester':
                return  m.MolesReactedDigester3[ n,  j, k]  == -m.StoichiometricCoeffDigester3[n] *  m.ConversionFactorDigester['Lipid'] * m.InitialMolesDigester[ 'Lipid',j,'Digester']  
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return  m.MolesReactedDigester3[ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.Reaction3DigesterConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment,rule=reaction3_Digester_constraint_rule)
        # -------------------------------
        # Reaction-4
        # -------------------------------
        def reaction4_Digester_constraint_rule(m, n,  j, k):
            if n in ['CH4','CO2'] and j =='AnaerobicDigestion' and k == 'Digester':
                return m.MolesReactedDigester4[ n,  j, k] == m.StoichiometricCoeffDigester4[n] * m.ConversionFactorDigester['glucose'] * m.InitialMolesDigester[ 'glucose',j,'Digester']
            elif n =='glucose' and j =='AnaerobicDigestion' and k == 'Digester':
                return  m.MolesReactedDigester4[ n,  j, k]  == -m.StoichiometricCoeffDigester4[n] *  m.ConversionFactorDigester['glucose'] * m.InitialMolesDigester[ 'glucose',j,'Digester'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return  m.MolesReactedDigester4[ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.Reaction4DigesterConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment,rule=reaction4_Digester_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_Digester_moles_rule(m, n,  j, k):
            if n in ['Carbohydrate','Water','Lipid','Protein','glucose'] and j =='AnaerobicDigestion' and k == 'Digester':
                return m.FinalMolesDigester[ n,  j, k] ==  m.InitialMolesDigester[ n, j,k]  - m.MolesReactedDigester1[ n,  j, k] - m.MolesReactedDigester2[ n,  j, k] - m.MolesReactedDigester3[ n,  j, k] - m.MolesReactedDigester4[ n,  j, k] 
            elif n in ['CO2','CH4','NH3','bioethanol','LacticAcid','MethylLactate','FAME','SuccinicAcid','AceticAcid','ButyricAcid','Butanol'] and j =='AnaerobicDigestion' and k == 'Digester':
                return m.FinalMolesDigester[ n, j, k] == m.InitialMolesDigester[ n, j,k]  + m.MolesReactedDigester1[ n,  j, k] + m.MolesReactedDigester2[ n,  j, k] + m.MolesReactedDigester3[ n,  j, k] + m.MolesReactedDigester4[ n,  j, k] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return  m.FinalMolesDigester[ n, j, k] == 0  
            else:
                return Constraint.Skip
        m.FinalMolesDigesterConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment,rule=final_Digester_moles_rule)
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_Digester_mass_rule(m,  n,  j, k):
            if n in ['CO2','CH4','NH3','Water','Protein','Carbohydrate','Lipid','bioethanol','LacticAcid','MethylLactate','FAME','SuccinicAcid','AceticAcid','ButyricAcid','Butanol'] and j =='AnaerobicDigestion' and k in ['Digester','FlashDrum']:
                return m.FinalMassDigester[n, j, k] == m.FinalMolesDigester[ n,'AnaerobicDigestion','Digester'] * m.MolecularWeightDigester[n]
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return  m.FinalMassDigester[ n, j, k] == 0  
            else:
                return Constraint.Skip
        m.FinalMassDigesterConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule= final_Digester_mass_rule)
        
        #FlashDrum
        # -------------------------------
        # FlashDrum gas outflow
        # -------------------------------
        def flashdrum5_top_outflow_rule(m, n, j, k):
            if n in ['CO2','CH4','NH3'] and j =='AnaerobicDigestion' and k in ['Comp','Membrane']:
                return m.Fflashdrum5_gas[n, j, k] == m.FinalMassDigester[ n,  j,'FlashDrum']
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.Fflashdrum5_gas[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.Topflashdrum5outflow = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=flashdrum5_top_outflow_rule)
        # -------------------------------
        # FlashDrum liquid outflow 
        # -------------------------------
        def flashdrum5_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','Protein','Carbohydrate','Lipid','bioethanol','LacticAcid','MethylLactate','FAME','SuccinicAcid','AceticAcid','ButyricAcid','Butanol'] and j =='AnaerobicDigestion' and k =='Centrifugal':
                return m.Fflashdrum5_liquid[n, j, k] == m.FinalMassDigester[ n,  j,'FlashDrum'] - m.Fflashdrum5_gas[n, j,'FlashDrum']
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.Fflashdrum5_liquid[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.Bottomflashdrum5outflow = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=flashdrum5_bottom_outflow_rule)
        
        #Centrifugal
        # -----------------------------------------------
        # Centrifugal - Solid (Fertilizer coproduct)
        # -----------------------------------------------
        def centrifugal5_solid_outflow_rule(m, n, j, k):
            if j == 'AnaerobicDigestion' and k == 'Centrifugal':
                # Total solids (keep actual proportions from FlashDrum output)
                total_solids = (m.Fflashdrum5_liquid['Carbohydrate', j, 'Centrifugal'] + m.Fflashdrum5_liquid['Protein', j, 'Centrifugal'] + m.Fflashdrum5_liquid['Lipid', j, 'Centrifugal'])
                # Total fertilizer mass (solids = 25% of total)
                total_fertilizer = total_solids / 0.25
                # Water portion in fertilizer (75% of total)
                water_in_fertilizer = 0.75 * total_fertilizer
                # Component-wise fertilizer flow
                if n == 'Water':
                    return m.Fertilizer_coproduct[n, j, k] == water_in_fertilizer
                elif n in ['Carbohydrate', 'Protein', 'Lipid']:
                    # Keep real solid flows (actual ratios from FlashDrum)
                    return m.Fertilizer_coproduct[n, j, k] == m.Fflashdrum5_liquid[n, j, 'Centrifugal']
                else:
                    return m.Fertilizer_coproduct[n, j, k] == 0
            else:
                return Constraint.Skip
        m.centrifugal5_solid_outflow_constraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=centrifugal5_solid_outflow_rule)
        # -----------------------------------------------
        # Centrifugal - Liquid (remaining water stream)
        # -----------------------------------------------
        def centrifugal5_liquid_outflow_rule(m, n, j, k):
            if n == 'Water' and j == 'AnaerobicDigestion' and k == 'Centrifugal':
                # Remaining water = total FlashDrum water - fertilizer water
                return m.FCentrifugal5_liquid[n, j, k] == ( m.Fflashdrum5_liquid[n, j, 'Centrifugal']- m.Fertilizer_coproduct['Water', j, k])
            elif n in ['bioethanol','LacticAcid','MethylLactate','FAME','SuccinicAcid','AceticAcid','ButyricAcid','Butanol'] and j =='AnaerobicDigestion'  and k == 'Centrifugal':
                return m.FCentrifugal5_liquid [n, j, k] == m.Fflashdrum5_liquid[n, j,'Centrifugal'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FCentrifugal5_liquid[n, j, k] == 0
            else:
                return Constraint.Skip
        m.centrifugal5_liquid_outflow_constraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=centrifugal5_liquid_outflow_rule)

        #Membrane-1
        # -------------------------------
        # Top stage
        # -------------------------------
        def Stage1_top_outflow_rule(m, n, j, k):
              if n in ['CH4','CO2'] and j == 'AnaerobicDigestion'  and k =='Membrane':
                  return m.FoutStage1_top[ n,  j, k]  ==  m.Fflashdrum5_gas[ n,  j, 'Membrane'] * m.Recoverymembrane1 [n] 
              elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return m.FoutStage1_top [ n,  j, k]  == 0 
              else:
                  return Constraint.Skip
        m.Stage1Topflow = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=Stage1_top_outflow_rule)
        # -------------------------------
        # Bottom stage
        # -------------------------------
        def Stage1_bottom_outflow_rule(m, n, j, k):
            if n in ['CH4','CO2','NH3'] and j == 'AnaerobicDigestion'  and k == 'Membrane':
                return m.FoutStage1_CO2[n, j, k] == m.Fflashdrum5_gas[ n,  j, 'Membrane']  - m.FoutStage1_top[ n,  j, 'Membrane'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FoutStage1_CO2[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomStage1outflow = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=Stage1_bottom_outflow_rule)
        
        #Membrane-2
        # -------------------------------
        # Top stage
        # -------------------------------
        def Stage2_top_outflow_rule(m,n,j):
            if n in ['CH4','CO2'] and j == 'AnaerobicDigestion' :
                return m.BioCNG_product [n,j]==  m.FoutStage1_top[ n,'AnaerobicDigestion', 'Membrane'] * m.Recoverymembrane2 [n] 
            elif n in m.Components and j in m.FWManagementOption:
                return m.BioCNG_product [n,j]  == 0 
            else:
                return Constraint.Skip
        m.Stage2Topflow = Constraint(m.Components, m.FWManagementOption,rule=Stage2_top_outflow_rule)
        # -------------------------------
        # Bottom stage
        # -------------------------------
        def Stage2_bottom_outflow_rule(m, n, j, k):
              if n in ['CH4','CO2']  and j == 'AnaerobicDigestion'  and k == 'Membrane':
                  return m.FoutStage2_CO2[n, j, k] == m.FoutStage1_top[ n,'AnaerobicDigestion' , 'Membrane'] - m.BioCNG_product [n,'AnaerobicDigestion']
              elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return m.FoutStage2_CO2[n, j, k]  == 0 
              else:
                  return Constraint.Skip
        m.BottomStage2outflow = Constraint(m.Components,  m.FWManagementOption, m.Equipment, rule=Stage2_bottom_outflow_rule)

# ======================================================
# Incineration Model
# ======================================================
class IncinerationModel:
    """Incineration process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach incineration constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Fuel consumption
        # --------------------------------        
        def Finfuel_composition_inflow_rule(m,n,j):
            if n in ['Carbohydrate', 'Protein', 'Lipid'] and j == 'Incineration': 
                return m.Ffuel[ n, j] ==  m.Finfeedstock['Incineration'] * m.BlendFraction[n]  + m.FCentrifugal4_Solid[n, 'ProteinExtraction', 'Centrifugal']
            elif n in m.Macronutrients and j in m.FWManagementOption : 
                return  m.Ffuel[ n, j] == 0 
            else:
                return Constraint.Skip
        m.Total_fuel_composition_inflow = Constraint(m.Macronutrients, m.FWManagementOption , rule= Finfuel_composition_inflow_rule)

        #----------------------------------
        #Air inflow for combustion (dynamic)
        #----------------------------------
        def air_comp4_inflow_rule(m, n, j, k):
            if j == 'Incineration' and k == 'Comp' and n in ['O2', 'N2']:
                # Calculate total stoichiometric O2 required based on fuel composition
                # For each macronutrient (Carbohydrate, Lipid, Protein)
                stoich_O2_demand = ( m.Ffuel['Carbohydrate', 'Incineration'] * m.StoichiometricO2['Carbohydrate'] + m.Ffuel['Lipid', 'Incineration'] * m.StoichiometricO2['Lipid'] + m.Ffuel['Protein', 'Incineration'] * m.StoichiometricO2['Protein'])
                # Apply dynamic excess air ratio (lambda)
                total_O2_needed = stoich_O2_demand * m.ExcessAirRatio
                # Air composition: 21% O2, 79% N2 (mole or mass fraction basis)
                if n == 'O2':
                    return m.FComp4[n, j, k] == total_O2_needed
                elif n == 'N2':
                    return m.FComp4[n, j, k] == total_O2_needed * (0.79 / 0.21)
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FComp4[n, j, k] == 0
            else:
                return Constraint.Skip
        m.AirinflowComp4 = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=air_comp4_inflow_rule)
        
        # -------------------------------
        # Inlet to burner 
        # -------------------------------
        def Burner_composition_inflow_rule(m, n, j, k):
            if n in ['Carbohydrate', 'Protein', 'Lipid'] and j == 'Incineration' and k == 'Burner':
                return m.FBurner [ n, j, k] ==  m.Ffuel[ n, j]
            elif n in ['O2','N2'] and j == 'Incineration' and k == 'Burner':
                return m.FBurner [ n, j, k] ==  m.FComp4[n, j, 'Comp']
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FBurner [n,j,k] == 0 
            else:
                return Constraint.Skip
        m.Burner_composition_inflow = Constraint(m.Components, m.FWManagementOption, m.Equipment,   rule=Burner_composition_inflow_rule)
        
        # Conversion and reaction constraints in Incineration
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def Burner_initial_moles_rule(m, n, j, k):
            if n in ['Carbohydrate', 'Protein', 'Lipid','O2','N2']   and j == 'Incineration' and k == 'Burner':
                return m.InitialMolesBurner[ n,j,k] == m.FBurner [ n, j,'Burner'] / m.MolecularWeightBurner[n]
            elif n in m.Components and j in m.FWManagementOption  and k in m.Equipment:
                return m.InitialMolesBurner[ n,j,k] == 0 
            else:
                return Constraint.Skip
        m.BurnerInitialMolesConstraint = Constraint(m.Components, m.FWManagementOption , m.Equipment,  rule=Burner_initial_moles_rule)        
        # -------------------------------
        # Reaction-1
        # -------------------------------
        def reaction1_Burner_constraint_rule(m, n,  j, k):
            if n in ['CO2','Water'] and j == 'Incineration' and k == 'Burner':
                return m.MolesReacted1Burner[ n,  j, k] == m.StoichiometricCoeffReaction1[n] * m.ConversionFactorBurner['Carbohydrate'] * m.InitialMolesBurner['Carbohydrate',  j, 'Burner'] 
            elif n in ['Carbohydrate','O2'] and j == 'Incineration' and k == 'Burner':
                return  m.MolesReacted1Burner[ n,  j, k] == -m.StoichiometricCoeffReaction1[n] * m.ConversionFactorBurner['Carbohydrate'] * m.InitialMolesBurner['Carbohydrate',  j, 'Burner'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return  m.MolesReacted1Burner[ n,  j, k] == 0
            else:
                return Constraint.Skip
        m.Reaction1BurnerConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=reaction1_Burner_constraint_rule)       
        # -------------------------------
        # Reaction-2
        # -------------------------------
        def reaction2_Burner_constraint_rule(m, n,  j, k):
            if n in ['CO2','Water','N2'] and j == 'Incineration' and k == 'Burner':
                return m.MolesReacted2Burner[ n,  j, k] == m.StoichiometricCoeffReaction2[n] * m.ConversionFactorBurner['Protein'] * m.InitialMolesBurner['Protein',  j, 'Burner'] 
            elif n in ['Protein','O2'] and j == 'Incineration' and k == 'Burner':
                return  m.MolesReacted2Burner[ n,  j, k] == -m.StoichiometricCoeffReaction2[n] * m.ConversionFactorBurner['Protein'] * m.InitialMolesBurner['Protein',  j, 'Burner'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return  m.MolesReacted2Burner[ n,  j, k] == 0
            else:
                return Constraint.Skip
        m.Reaction2BurnerConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment,   rule=reaction2_Burner_constraint_rule)
        # -------------------------------
        # Reaction-3
        # -------------------------------
        def reaction3_Burner_constraint_rule(m, n,  j, k):
            if n in ['CO2','Water'] and j == 'Incineration' and k == 'Burner':
                return m.MolesReacted3Burner[ n,  j, k] == m.StoichiometricCoeffReaction3[n] * m.ConversionFactorBurner['Lipid'] * m.InitialMolesBurner['Lipid',  j,'Burner'] 
            elif n in ['Lipid','O2'] and j == 'Incineration' and k == 'Burner':
                return  m.MolesReacted3Burner[ n,  j, k] == -m.StoichiometricCoeffReaction3[n] * m.ConversionFactorBurner['Lipid'] * m.InitialMolesBurner['Lipid',  j,'Burner'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return  m.MolesReacted3Burner[ n,  j, k] == 0
            else:
                return Constraint.Skip
        m.Reaction3BurnerConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=reaction3_Burner_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_Burner_moles_rule(m, n,  j, k):
            if n in ['Carbohydrate','Protein','Lipid','O2'] and j == 'Incineration' and k == 'Burner':
                return m.FinalMolesBurner[ n,  j, k] ==  m.InitialMolesBurner[ n, j,k]  - m.MolesReacted1Burner[ n,  j, k] - m.MolesReacted2Burner[ n,  j, k] - m.MolesReacted3Burner[ n,  j, k]
            elif n in ['Water','CO2','N2'] and j == 'Incineration' and k == 'Burner':
                return  m.FinalMolesBurner[ n,  j, k] == m.InitialMolesBurner[ n, j,k] + m.MolesReacted1Burner[ n,  j, k] + m.MolesReacted2Burner[ n,  j, k] + m.MolesReacted3Burner[ n,  j, k] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return  m.FinalMolesBurner[ n,  j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesBurnerConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment,  rule=final_Burner_moles_rule)      
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_Burner_mass_rule(m,  n,  j, k):
            if n in ['Carbohydrate', 'Protein', 'Lipid', 'Water','CO2','O2','N2'] and j == 'Incineration' and k in ['Burner','Turbine','Economizer']:
                return m.FinalMassBurner[n, j, k] == m.FinalMolesBurner[ n,  j, 'Burner'] * m.MolecularWeightBurner[n]
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FinalMassBurner[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassBurnerConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule= final_Burner_mass_rule)
                
        #-------------------------------
        # Electricity generation
        # -------------------------------
        def electricity_generated_rule(m):
            # Conversion factor: MJ/day to kWh/h
            MJ_to_kWh = 0.000277777778 / 24
            # Total energy from incineration
            FW_energy = m.Finfeedstock['Incineration'] * m.LHVFW 
            #Total energy from solidwaste
            solidwaste_energy = sum(m.FCentrifugal4_Solid[n, 'ProteinExtraction', 'Centrifugal'] * m.LHVSolidWaste for n in m.Components)
            # Net electricity generated
            return m.ElectricityGenerated == (FW_energy + solidwaste_energy) * MJ_to_kWh * m.EffBoiler * m.EffTurbine #kWh
        m.ElectricityGenerated_constraint = Constraint(rule=electricity_generated_rule)
        
        #-------------------------------
        # steam generation at 454 oC, 60 bar
        # -------------------------------
        def Heat_generated_rule(m):
            # Total energy from incineration
            FW_energy = m.Finfeedstock['Incineration'] * m.LHVFW 
            #Total energy from solidwaste
            solidwaste_energy = sum(m.FCentrifugal4_Solid[n, 'ProteinExtraction', 'Centrifugal'] * m.LHVSolidWaste for n in m.Components)
            return m.HeatGenerated ==  (FW_energy + solidwaste_energy) * m.EffComb  * m.EffBoiler / (m.SpecificEnthalpySteam - m.SpecificEnthalpyWater)
        m.HeatGenerated_constraint = Constraint(rule=Heat_generated_rule)
                
        #-------------------------------
        # Pump15, Economizer2, and Cooler12
        # -------------------------------
        def Coolflow_composition_inflow_rule(m, n, j, k):
            if n == 'Water' and j == 'Incineration' and k in ['Pump','Economizer','Cooler']:
                return m.FCooler [n, j, k] == m.HeatGenerated
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return  m.FCooler [n, j, k] == 0
            else:
                return Constraint.Skip
        m.Coolflow_composition_inflow =  Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=Coolflow_composition_inflow_rule)
        
        #-------------------------------
        # Flue gas
        # ------------------------------- 
        def Fluegas_composition_inflow_rule(m, n, j, k):
            if n in ['CO2','O2','N2','Water'] and j == 'Incineration' and k=='Cyclone':
                return m.Fluegas [n, j, k] == m.FinalMassBurner [n, j, 'Economizer']
            elif n in m.Components and j in m.FWManagementOption  and k in m.Equipment:
                return  m.Fluegas  [n, j, k] == 0
            else:
                return Constraint.Skip
        m.Fluegas_composition_inflow =  Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=Fluegas_composition_inflow_rule)
        
        #-------------------------------
        # Ash
        # -------------------------------
        def Ash_composition_inflow_rule(m, n, j, k):
            if n in ['Carbohydrate', 'Protein', 'Lipid'] and j == 'Incineration' and k=='Cyclone':
                return m.Ash [n, j, k] == m.FinalMassBurner [n, j, 'Economizer']
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return   m.Ash [n, j, k] == 0
            else:
                return Constraint.Skip
        m.Ash_composition_inflow =  Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=Ash_composition_inflow_rule)

# ======================================================
# Food Waste Management Model
# ======================================================
class FWManagementModel:
    """Unified class that groups AnaerobicDigestion, Composting, and Incineration models."""

    def __init__(self, model):
        """Attach all process constraints to one existing AbstractModel."""
        self.model = model
        self.composting = CompostingModel(model)
        self.AnimalFeed = AnimalFeedModel(model)
        self.anaerobic = AnaerobicDigestionModel(model)
        self.incineration = IncinerationModel(model)

    def get_models(self):
        """Return all sub-models (for inspection or solving separately)."""
        return {
            'composting': self.composting.model,
            'AnimalFeed' : self.AnimalFeed.model,
            'anaerobic': self.anaerobic.model,
            'incineration': self.incineration.model
        }


