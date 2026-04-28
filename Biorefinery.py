from pyomo.environ import *

# ======================================================
# Pretreatment Model
# ======================================================
class EnzymaticHydrolysisModel:
    """Enzymatic hydrolysis process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach grinding constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Pump constraints
        # -------------------------------
        def flowin_pump1_rule(m, c, j, k):
            # Ensure only water is used in Pump1
            if c == 'Water' and j == 'enzymatic-hydrolysis' and k == 'Pump':
                return m.Fpump1[c, j, k] == m.Finfeedstock['enzymatic-hydrolysis'] * m.ChemicalPretreatmentConsumption ['Water', 'enzymatic-hydrolysis','Pump']
            elif c in m.Chemicals and j in m.FWManagementOption and k in m.Equipment:
                # Set other components' inflow to Pump1 as zero
                return m.Fpump1[c, j, k] == 0
            else:
                return Constraint.Skip

        m.flowin_pump1_constraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=flowin_pump1_rule)
        
        # -------------------------------
        # Flow balance pretreatment
        # -------------------------------
        def flow_pretreatment_balance_rule(m, n, j, k):
            if n in ['Water'] and j =='enzymatic-hydrolysis' and k in ['Heater', 'Autoclave', 'Cooler', 'Reactor']:
                return m.FPretreatment_component[n,j,k] ==  m.Fpump1['Water', j, 'Pump']
            elif n in ['Carbohydrate','Protein','Lipid'] and j =='enzymatic-hydrolysis' and k in ['Heater', 'Autoclave', 'Cooler', 'Reactor']:
                return m.FPretreatment_component[n,j,k] ==  m.Finfeedstock['enzymatic-hydrolysis'] * m.BlendFraction[n]
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                  return  m.FPretreatment_component[n,j,k] == 0   
            else:
                  return Constraint.Skip
        m.flow_pretreatment_balance_rule = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=flow_pretreatment_balance_rule)

        # Conversion and reaction constraints in Hydrolysis
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def hydrolysis_initial_moles_rule(m, n, j, k):
            if n in ['Carbohydrate', 'Protein', 'Lipid', 'Water', 'glucose'] and j=='enzymatic-hydrolysis' and k == 'Reactor':
                return m.InitialMoles[n, j, k] == m.FPretreatment_component[n, j, 'Reactor'] / m.MolecularWeight[n]
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.InitialMoles[n, j, k] == 0
            else:
                return Constraint.Skip
        m.HydrolysisInitialMolesConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=hydrolysis_initial_moles_rule)  
        # -------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_constraint_rule(m, n, j, k):
            if n == 'glucose' and j=='enzymatic-hydrolysis' and k == 'Reactor':
                return m.MolesReacted[n, j, k] == m.StoichiometricCoeff[n] * m.ConversionFactor * m.InitialMoles['Carbohydrate', j, k]
            elif n in ['Carbohydrate', 'Water'] and j=='enzymatic-hydrolysis' and k == 'Reactor':
                return m.MolesReacted[n, j, k] == -m.StoichiometricCoeff[n] * m.ConversionFactor * m.InitialMoles['Carbohydrate',j, k]
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.MolesReacted[n,j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=reaction_constraint_rule)        
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_moles_rule(m, n, j, k):
            if n in ['Carbohydrate', 'Water'] and j=='enzymatic-hydrolysis' and k == 'Reactor':
                return m.FinalMoles[n, j, k] == m.InitialMoles[n, j, k] - m.MolesReacted[n, j, k]
            elif n in ['Protein', 'Lipid', 'glucose'] and j=='enzymatic-hydrolysis' and k == 'Reactor':
                return m.FinalMoles[n, j, k] == m.InitialMoles[n, j, k] + m.MolesReacted[n, j, k]
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FinalMoles[n, j, k] == 0
            else:
                return  Constraint.Skip
        m.FinalMolesConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=final_moles_rule)       
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_mass_rule(m,n, j, k):
            if n in ['Carbohydrate', 'Protein', 'Lipid', 'Water', 'glucose'] and j=='enzymatic-hydrolysis' and k in ['Reactor','Centrifugal']:
                return m.FinalMass[n, j, k] == m.FinalMoles[n, j, 'Reactor'] * m.MolecularWeight[n] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FinalMass[n, j, k] == 0
            else:
                return Constraint.Skip
        m.FinalMassConstraint = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=final_mass_rule)
        
        #Centrifugal 
        # -------------------------------
        # Centrifugal liquid outflow
        # -------------------------------
        def centrifugal1_liquid_composition_outflow_rule(m, n, j, k):
            if n in ['glucose', 'Water'] and j=='enzymatic-hydrolysis' and k == 'Centrifugal':
                return m.FCentrifugal1_liquid[n, j, k] == m.FinalMass[ n, j,'Centrifugal'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FCentrifugal1_liquid[n, j, k] == 0
            else:
                return Constraint.Skip
        m.centrifugal1_liquid_composition_outflow = Constraint(m.Components, m.FWManagementOption, m.Equipment, rule=centrifugal1_liquid_composition_outflow_rule)
        # -------------------------------
        # Centrifugal solid outflow
        # -------------------------------
        def centrifugal1_solid_composition_outflow_rule(m, n, j, k):
            if n in ['Carbohydrate', 'Protein', 'Lipid'] and j=='enzymatic-hydrolysis' and k == 'Centrifugal':
                return m.FCentrifugal1_Solid[n, j, k] == m.FinalMass[ n, j,'Centrifugal'] 
            elif n in m.Components and j in m.FWManagementOption and k in m.Equipment:
                return m.FCentrifugal1_Solid[n, j, k] == 0
            else:
                return Constraint.Skip
        m.centrifugal1_solid_composition_outflow = Constraint(m.Components, m.FWManagementOption, m.Equipment,  rule=centrifugal1_solid_composition_outflow_rule)

# # # ======================================================
# Bioethanol Process Model
# ======================================================
class BioethanolModel:
    """Bioethanol process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach grinding constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Flow balance pretreatment constraints 
        # --------------------------------        
        def flow_bioethanol_rule(m, n, j, k):
            if n in ['glucose','Water'] and j =='BioethanolProcess' and k in ['Pump', 'Cooler', 'Fermenter']:
                return m.FBioethanol1[n,j,k] ==  m.Finglucose_biofuel_component [n,'BioethanolProcess']
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                 return  m.FBioethanol1[n,j,k] == 0 
            else:
                 return Constraint.Skip
        m.flow_bioethanol1_balance_constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule=flow_bioethanol_rule)
        
        # Conversion and reaction constraints in Biethanol
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def fermenter1_initial_moles_rule(m, n, j, k):
            if n in ['Water','glucose','bioethanol','CO2'] and j =='BioethanolProcess' and k=='Fermenter':
                return m.InitialMolesFermenter1[ n,j,k] == m.FBioethanol1 [ n, j, 'Fermenter'] / m.MolecularWeightFermenter1[n]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.InitialMolesFermenter1[ n,j,k] == 0
            else:
                return Constraint.Skip
        m.Fermenter1InitialMolesConstraint = Constraint(m.Components, m.Biofuels, m.Equipment,  rule=fermenter1_initial_moles_rule)
        # -------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_fermenter1_constraint_rule(m, n,  j, k):
            if n in ['bioethanol','CO2'] and j =='BioethanolProcess' and k=='Fermenter':
                return m.MolesReactedFermenter1[ n,  j, k] == m.StoichiometricCoeffFermenter1[n] * m.ConversionFactorFermenter1 * m.InitialMolesFermenter1['glucose',  j,'Fermenter'] 
            elif n == 'glucose'and j =='BioethanolProcess' and k=='Fermenter':
                return m.MolesReactedFermenter1[ n, j, k] == -m.StoichiometricCoeffFermenter1[n] * m.ConversionFactorFermenter1 * m.InitialMolesFermenter1['glucose', j,'Fermenter'] 
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return  m.MolesReactedFermenter1[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionFermenter1Constraint = Constraint(m.Components,m.Biofuels, m.Equipment,  rule=reaction_fermenter1_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_fermenter1_moles_rule(m, n,  j, k):
            if n == 'glucose'and j =='BioethanolProcess' and k=='Fermenter':
                return m.FinalMolesFermenter1[ n,  j, k] ==  m.InitialMolesFermenter1[ n, j,k]  - m.MolesReactedFermenter1[ n,  j, k]
            elif n in ['bioethanol','CO2','Water'] and j =='BioethanolProcess' and k=='Fermenter':
                return m.FinalMolesFermenter1[ n, j, k] == m.InitialMolesFermenter1[ n, j,k]  + m.MolesReactedFermenter1[ n,  j, k]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FinalMolesFermenter1[ n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesFermenter1Constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule=final_fermenter1_moles_rule)      
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_fermenter1_mass_rule(m,  n,  j, k):
            if n in [ 'Water','glucose','bioethanol', 'CO2'] and j =='BioethanolProcess' and k in ['Fermenter','FlashDrum']:
                return m.FinalMassFermenter1[n, j, k] == m.FinalMolesFermenter1[ n,j, 'Fermenter'] * m.MolecularWeightFermenter1[n] 
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FinalMassFermenter1[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassFermenter1Constraint = Constraint(m.Components, m.Biofuels, m.Equipment,  rule= final_fermenter1_mass_rule)
        
        #FlashDrum
        # -------------------------------
        # FlashDrum gas outflow
        # -------------------------------
        def flashdrum1_gas_composition_outflow_rule(m, n, j, k):
            if  n in ['CO2'] and j =='BioethanolProcess' and k=='FlashDrum':
                return m.Fflashdrum1_gas[ n, j, k] == m.FinalMassFermenter1[ n,  j, 'FlashDrum']
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.Fflashdrum1_gas[ n, j, k] == 0
            else: 
                return Constraint.Skip
        m.flashdrum1_gas_composition_outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=flashdrum1_gas_composition_outflow_rule)
        # -------------------------------
        # FlashDrum liquid outflow 
        # -------------------------------
        def flashdrum1_liquid_composition_outflow_rule(m, n, j, k):
            if n in ['Water','glucose','bioethanol'] and j == 'BioethanolProcess' and k in ['FlashDrum','Pump', 'Heater','DT']:
                return m.Fflashdrum1_liquid[n, j, k] == m.FinalMassFermenter1[ n,  j, 'FlashDrum']
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return m.Fflashdrum1_liquid[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.flashdrum1_liquid_composition_outflow = Constraint(m.Components, m.Biofuels, m.Equipment,   rule=flashdrum1_liquid_composition_outflow_rule)
        
        #DistillationColumn-1
        # -------------------------------
        # Top column-1
        # -------------------------------
        def DT1_top_outflow_rule(m, n, j, k):
            if n in ['Water', 'bioethanol'] and j == 'BioethanolProcess' and k=='DT':
                return m.FDT1_top[n, j, k] == m.Fflashdrum1_liquid [ n,  j, 'DT'] * m.RecoveryTopDT1[n]
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return m.FDT1_top[n, j, k] == 0 
            else:
                Constraint.Skip
        m.TopDT1outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT1_top_outflow_rule)
        # -------------------------------
        # Bottom column-2
        # -------------------------------
        def DT1_bottom_outflow_rule(m, n, j, k):
            if n in ['Water', 'bioethanol','glucose'] and j == 'BioethanolProcess' and k=='DT':
                return m.FDT1_bottom[n, j, k] == m.Fflashdrum1_liquid [ n,  j, 'DT'] - m.FDT1_top[n, j, 'DT']
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return m.FDT1_bottom[n, j, k] == 0 
            else:
                Constraint.Skip
        m.BottomDT1outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT1_bottom_outflow_rule)

        #DistillationColumn-2
        # -------------------------------
        # Top column-2
        # -------------------------------
        def DT2_top_outflow_rule(m, n, j, k):
            if n in ['Water', 'bioethanol'] and j == 'BioethanolProcess' and k in ['DT','Heater','MS']:
                return m.FDT2_top[n, j, k] == m.FDT1_top[ n,  j, 'DT'] * m.RecoveryTopDT2[n]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FDT2_top[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.TopDT2outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT2_top_outflow_rule)
        # -------------------------------
        # Bottom column-2
        # -------------------------------
        def DT2_bottom_outflow_rule(m, n, j, k):
            if n in ['Water', 'bioethanol'] and j == 'BioethanolProcess' and k=='DT':
                return m.FDT2_bottom[n, j, k] == m.FDT1_top [ n,  j, 'DT'] - m.FDT2_top[n, j, k]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FDT2_bottom[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.BottomDT2outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT2_bottom_outflow_rule)
        
        #Molecular sieve
        # -------------------------------
        # Top MS
        # -------------------------------
        def MS_bioethanol_outflow_rule(m, n, j, k):
            if n in ['Water', 'bioethanol'] and j == 'BioethanolProcess' and k in ['MS','Cooler']:
                return m.BioethanolProduct [n, j, k] ==  m.FDT2_top[ n, j, 'MS']  * m.RecoveryProductMS[n]
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return m.BioethanolProduct[ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.BioethanolMSoutflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=MS_bioethanol_outflow_rule)
        # -------------------------------
        # Bottom MS
        # -------------------------------
        def MS_bottom_outflow_rule(m, n, j, k):
            if  n in ['Water', 'bioethanol'] and j == 'BioethanolProcess' and k=='MS':
                return m.FMS_bottom[n, j, k] == m.FDT2_top[ n,  j, 'MS']  - m.BioethanolProduct[n, j, 'MS']
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return m.FMS_bottom[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomMSoutflow = Constraint(m.Components, m.Biofuels, m.Equipment,   rule=MS_bottom_outflow_rule)

        # -------------------------------
        # Bioethanol waste stream
        # -------------------------------
        def total_bioethanol_waste_rule(m, n,j):
            if n in ['Water','glucose','bioethanol'] and j =='BioethanolProcess':
                return m.totalwaste_bioethanol [n,j] == m.FDT1_bottom[n, 'BioethanolProcess', 'DT'] +  m.FDT2_bottom[n, 'BioethanolProcess', 'DT'] + m.FMS_bottom[n, 'BioethanolProcess', 'MS']
            elif n in m.Components  and j in m.Biofuels :
                return m.totalwaste_bioethanol [n,j]  == 0 
            else:
                return Constraint.Skip
        m.total_bioethanol_waste_constraint = Constraint(m.Components, m.Biofuels, rule=total_bioethanol_waste_rule)

# ======================================================
# Butanol Process Model
# ====================================================== 
class ButanolModel:
    """Butanol process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Butanol constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model

        ## -------------------------------
        # Flow balance pretreatment constraints (generalized for the same equipment)
        # -------------------------------- 
        def flow_butanol_balance_rule(m, n, j, k):
            if n in ['glucose','Water'] and j =='ButanolProcess' and k in ['Pump', 'Cooler', 'Fermenter']:
                return m.FinButanol_component [n,j,k] == m.Finglucose_biofuel_component [n,'ButanolProcess']
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                  return  m.FinButanol_component[n,j,k] == 0 
            else:
                  return Constraint.Skip
        m.flow_butanol_balance_constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule=flow_butanol_balance_rule)

        # Conversion and reaction constraints in Butanol
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def Fermenter3_initial_moles_rule(m, n, j, k):
            if n in ['glucose','Water'] and j =='ButanolProcess' and k == 'Fermenter':
                return m.InitialMolesFermenter3[ n,j,k] == m.FinButanol_component  [ n, j,'Fermenter'] / m.MolecularWeightButanol[n]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.InitialMolesFermenter3[n,j,k] == 0 
            else:
                return Constraint.Skip
        m.Fermenter3InitialMolesConstraint = Constraint(m.Components, m.Biofuels, m.Equipment,  rule=Fermenter3_initial_moles_rule)
        #-------------------------------
        # Reaction-1
        # -------------------------------
        def reaction1_fermenter3_constraint_rule(m, n,  j, k):
            if n in ['Acetone','CO2','H2'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted1Fermenter3[ n,  j, k] == m.StoichiometricCoeffButanol1[n] * m.ConversionFactorButanol1 * m.InitialMolesFermenter3['glucose',  j, 'Fermenter'] 
            elif n in['Water','glucose'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted1Fermenter3[ n, j, k] == -m.StoichiometricCoeffButanol1[n] * m.ConversionFactorButanol1 * m.InitialMolesFermenter3['glucose', j, 'Fermenter'] 
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return  m.MolesReacted1Fermenter3[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.Reaction1Fermenter3Constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule=reaction1_fermenter3_constraint_rule)
        #-------------------------------
        # Reaction-2
        # -------------------------------
        def reaction2_fermenter3_constraint_rule(m, n,  j, k):
            if n in ['Butanol','CO2','Water'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted2Fermenter3[ n,  j, k] == m.StoichiometricCoeffButanol2[n] * m.ConversionFactorButanol2 * m.InitialMolesFermenter3['glucose',  j, 'Fermenter'] 
            elif n in['glucose'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted2Fermenter3[ n, j, k] == -m.StoichiometricCoeffButanol2[n] * m.ConversionFactorButanol2 * m.InitialMolesFermenter3['glucose', j, 'Fermenter'] 
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return  m.MolesReacted2Fermenter3[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.Reaction2Fermenter3Constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule=reaction2_fermenter3_constraint_rule)
        #-------------------------------
        # Reaction-3
        # -------------------------------
        def reaction3_fermenter3_constraint_rule(m, n,  j, k):
            if n in ['bioethanol','CO2'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted3Fermenter3[ n,  j, k] == m.StoichiometricCoeffButanol3[n] * m.ConversionFactorButanol3 * m.InitialMolesFermenter3['glucose',  j, 'Fermenter'] 
            elif n in['glucose'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted3Fermenter3[ n, j, k] == -m.StoichiometricCoeffButanol3[n] * m.ConversionFactorButanol3 * m.InitialMolesFermenter3['glucose', j, 'Fermenter'] 
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return  m.MolesReacted3Fermenter3[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.Reaction3Fermenter3Constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule=reaction3_fermenter3_constraint_rule)
        #-------------------------------
        # Reaction-4
        # -------------------------------
        def reaction4_fermenter3_constraint_rule(m, n,  j, k):
            if n in ['AceticAcid','CO2','H2'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted4Fermenter3[ n,  j, k] == m.StoichiometricCoeffButanol4[n] * m.ConversionFactorButanol4 * m.InitialMolesFermenter3['glucose',  j, 'Fermenter'] 
            elif n in['glucose'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted4Fermenter3[ n, j, k] == -m.StoichiometricCoeffButanol4[n] * m.ConversionFactorButanol4 * m.InitialMolesFermenter3['glucose', j, 'Fermenter'] 
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return  m.MolesReacted4Fermenter3[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.Reaction4Fermenter3Constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule=reaction4_fermenter3_constraint_rule)
        #-------------------------------
        # Reaction-5
        # -------------------------------
        def reaction5_fermenter3_constraint_rule(m, n,  j, k):
            if n in ['ButyricAcid','CO2','H2'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted5Fermenter3[ n,  j, k] == m.StoichiometricCoeffButanol5[n] * m.ConversionFactorButanol5 * m.InitialMolesFermenter3['glucose',  j, 'Fermenter'] 
            elif n in['glucose'] and j =='ButanolProcess' and k=='Fermenter':
                return m.MolesReacted5Fermenter3[ n, j, k] == -m.StoichiometricCoeffButanol5[n] * m.ConversionFactorButanol5 * m.InitialMolesFermenter3['glucose', j, 'Fermenter'] 
            elif n in m.Components  and j in m.Biofuels and k in m.Equipment:
                return  m.MolesReacted5Fermenter3[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.Reaction5Fermenter3Constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule=reaction5_fermenter3_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_Fermenter3_moles_rule(m, n,  j, k):
            if n =='glucose' and j =='ButanolProcess' and k == 'Fermenter':
                return m.FinalMolesFermenter3[ n,  j, k] ==  m.InitialMolesFermenter3[ n, j,k]  - m.MolesReacted1Fermenter3[ n,  j, k] -m.MolesReacted2Fermenter3[ n,  j, k]-m.MolesReacted3Fermenter3[ n,  j, k] -m.MolesReacted4Fermenter3[ n,  j, k] -m.MolesReacted5Fermenter3[ n,  j, k] 
            if n =='Water' and j =='ButanolProcess' and k == 'Fermenter':
                return m.FinalMolesFermenter3[ n,  j, k] ==  m.InitialMolesFermenter3[ n, j,k]  - m.MolesReacted1Fermenter3[ n,  j, k] +m.MolesReacted2Fermenter3[ n,  j, k]-m.MolesReacted4Fermenter3[ n,  j, k] 
            elif n in ['bioethanol','H2','CO2','ButyricAcid','Butanol','AceticAcid','Acetone'] and j =='ButanolProcess' and k == 'Fermenter':
                return  m.FinalMolesFermenter3[ n,  j, k] ==  m.InitialMolesFermenter3[ n, j,k]  + m.MolesReacted1Fermenter3[ n,  j, k]+m.MolesReacted2Fermenter3[ n,  j, k]+m.MolesReacted3Fermenter3[ n,  j, k]+m.MolesReacted4Fermenter3[ n,  j, k]+m.MolesReacted5Fermenter3[ n,  j, k]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return  m.FinalMolesFermenter3[ n,  j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesFermenter3Constraint = Constraint(m.Components, m.Biofuels, m.Equipment,  rule=final_Fermenter3_moles_rule)
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_Fermenter3_mass_rule(m,  n,  j, k):
            if n in ['glucose','Water','bioethanol','H2','CO2','ButyricAcid','Butanol','AceticAcid','Acetone'] and j =='ButanolProcess' and k in ['Fermenter','FlashDrum']:
                return m.FinalMassFermenter3[n, j, k] == m.FinalMolesFermenter3[ n,j, 'Fermenter'] * m.MolecularWeightButanol[n]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FinalMassFermenter3[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassFermenter3Constraint = Constraint(m.Components, m.Biofuels, m.Equipment, rule= final_Fermenter3_mass_rule)

        # Flash Drum
        # -------------------------------
        # Top 
        #-------------------------------
        def flashdrum4_top_outflow_rule(m, n, j, k):
            if n in ['CO2','H2']and j == 'ButanolProcess' and k in ['FlashDrum','PSA']:
                return m.Foutflashdrum4_gas_component[n, j, k] == m.FinalMassFermenter3[ n,  j,'FlashDrum'] 
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.Foutflashdrum4_gas_component[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.Topflashdrum4outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=flashdrum4_top_outflow_rule)
        # -------------------------------
        # Bottom 
        # -------------------------------
        def flashdrum4_bottom_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone']  and j == 'ButanolProcess' and k in ['FlashDrum','DT']:
                return m.Foutflashdrum4_liquid_component[n, j, k] == m.FinalMassFermenter3[ n,  j,'FlashDrum'] - m.Foutflashdrum4_gas_component[n, j,'FlashDrum']
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.Foutflashdrum4_liquid_component[n, j, k]== 0 
            else:
                return Constraint.Skip
        m.Bottomflashdrum4outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=flashdrum4_bottom_outflow_rule)

        #PSA
        #-------------------------------
        #Top 
        #-------------------------------
        def PSA_top_outflow_rule(m, n, j, k):
            if n =='CO2' and j == 'ButanolProcess' and k=='PSA':
                return m.CO2_stream_Butanol[n, j, k] ==  m.Foutflashdrum4_gas_component[n, j, 'PSA']
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.CO2_stream_Butanol[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.PSAoutflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=PSA_top_outflow_rule)
        # -------------------------------
        # Bottom 
        # -------------------------------
        def PSA_bottom_outflow_rule(m, n, j, k):
            if n =='H2' and j == 'ButanolProcess' and k=='PSA':
                return m.H2_coproduct[n, j, k] ==  m.Foutflashdrum4_gas_component[n, j, 'PSA'] - m.CO2_stream_Butanol[n, j, 'PSA']
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.H2_coproduct[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.BottomPSAoutflow = Constraint(m.Components, m.Biofuels, m.Equipment,  rule=PSA_bottom_outflow_rule)

        #DistillationColumn-1
        # -------------------------------
        # Top column-1
        # -------------------------------
        def DT4_top_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k=='DT':
                return m.FoutDT4_top_component[n, j, k]  == m.Foutflashdrum4_liquid_component[n, j, 'DT'] * m.TopDT4 [n]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FoutDT4_top_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT4outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT4_top_outflow_rule)

        # -------------------------------
        # Bottom column-1
        #-------------------------------
        def DT4_bottom_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k=='DT':
                return m.FoutDT4_bottom_component[n, j, k] ==  m.Foutflashdrum4_liquid_component[n, j,'DT'] -  m.FoutDT4_top_component[n, j, 'DT']
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FoutDT4_bottom_component[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.BottomDT4outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT4_bottom_outflow_rule)
        
        #DistillationColumn-2
        #-------------------------------
        #Bottom column-2
        #-------------------------------
        def DT5_top_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k=='DT':
                return m.Acetone_coproduct[n, j, k] == m.FoutDT4_top_component[n, j, 'DT']  * m.TopDT5 [n]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.Acetone_coproduct[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.TopDT5outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT5_top_outflow_rule)
        # -------------------------------
        # Top column-2
        # -------------------------------
        def DT5_bottom_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k=='DT':
                return m.FoutDT5_bottom_component[n, j, k] ==  m.FoutDT4_top_component[n, j, 'DT'] - m.Acetone_coproduct[n, j, 'DT'] 
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FoutDT5_bottom_component[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.BottomDT5outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT5_bottom_outflow_rule)

        #DistillationColumn-3
        # -------------------------------
        # Top column-3
        #-------------------------------
        def DT6_top_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k=='DT':
                return m.Ethanol_coproduct [n, j, k] ==  m.FoutDT5_bottom_component[n, j, 'DT'] * m.TopDT6 [n]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.Ethanol_coproduct [n, j, k] == 0 
            else:
                return Constraint.Skip
        m.TopDT6outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT6_top_outflow_rule)
        # -------------------------------
        # Bottom column-3
        # -------------------------------
        def DT6_bottom_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k in ['DT','Cooler','Decant']:
                return m.FoutDT6_bottom_component[n, j, k] ==  m.FoutDT5_bottom_component[n, j, 'DT'] - m.Ethanol_coproduct [n, j, 'DT'] 
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FoutDT6_bottom_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT6outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT6_bottom_outflow_rule)
        
        # Decant
        # -------------------------------
        # Bottom 
        #-------------------------------
        def Decant1_bottom_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k=='Decant':
                return m.FoutDecant1_bottom_component[n, j, k] ==  m.FoutDT6_bottom_component  [n,j,'Decant'] * m.BottomDecant1 [n]
            elif n in m.Components and j in  m.Biofuels  and k in m.Equipment:
                return m.FoutDecant1_bottom_component[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.BottomDecant1outflow = Constraint(m.Components,  m.Biofuels, m.Equipment, rule=Decant1_bottom_outflow_rule)
        # -------------------------------
        # Top 
        # -------------------------------
        def Decant1_top_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k in ['Decant','DT']:
                return m.FoutDecant1_top_component [n, j, k] ==  m.FoutDT6_bottom_component [n,j,'Decant'] - m.FoutDecant1_bottom_component[n, j,'Decant'] 
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FoutDecant1_top_component [n, j, k] == 0 
            else:
                return Constraint.Skip
        m.TopDecant1outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=Decant1_top_outflow_rule)

        #DistillationColumn-4
        # -------------------------------
        # Bottom column-4
        #-------------------------------
        def Butanol_product_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k=='DT':
                return m.Butanol_product [n, j, k] == m.FoutDecant1_top_component[n, j, 'DT']  * m.BottomDT7 [n]
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.Butanol_product [n, j, k] == 0 
            else:
                return Constraint.Skip
        m.ButanolProductoutflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=Butanol_product_outflow_rule)
        # -------------------------------
        # Top column-4
        # -------------------------------
        def DT7_top_outflow_rule(m, n, j, k):
            if n in ['glucose','Water','bioethanol','ButyricAcid','Butanol','AceticAcid','Acetone'] and j == 'ButanolProcess' and k=='DT':
                return m.FoutDT7_top_component[n, j, k] ==  m.FoutDecant1_top_component[n, j, 'DT']  - m.Butanol_product [n, j, 'DT']
            elif n in m.Components and j in m.Biofuels and k in m.Equipment:
                return m.FoutDT7_top_component[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.TopDT7outflow = Constraint(m.Components, m.Biofuels, m.Equipment, rule=DT7_top_outflow_rule)
        
        # -------------------------------
        # Waste
        # -------------------------------
        def total_Butanol_waste_rule(m, n,j):
            if n in ['AceticAcid','ButyricAcid','Butanol','Water','bioethanol','glucose'] and j =='ButanolProcess':
                return m.totalwaste_Butanol [n,j] == m.FoutDT4_bottom_component[n, 'ButanolProcess', 'DT'] + m.FoutDecant1_bottom_component[n, 'ButanolProcess', 'Decant'] + m.FoutDT7_top_component[n, 'ButanolProcess', 'DT']
            elif n in m.Components and j in m.Biofuels:
                return m.totalwaste_Butanol [n,j] == 0 
            else:
                return Constraint.Skip
        m.total_Butanol_waste_constraint = Constraint(m.Components, m.Biofuels, rule=total_Butanol_waste_rule)

# ======================================================
# Lactic Acid Process Model
# ======================================================
class LacticAcidModel:
    """LacticAcid process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach LacticAcid constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Flow balance pretreatment constraints (generalized for the same equipment)
        # -------------------------------- 
        def flow_lacticacid1_balance_rule(m, n, j, k):
            if n in ['glucose','Water'] and j =='LacticAcidProcess' and k in ['Pump', 'Cooler', 'Fermenter']:
                return m.FinLacticAcid1_component [n,j,k] ==  m.Finglucose_biochemical_component [n,'LacticAcidProcess']
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                  return  m.FinLacticAcid1_component[n,j,k] == 0 
            else:
                  return Constraint.Skip
        m.flow_lacticacid1_balance_constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flow_lacticacid1_balance_rule)
        
        # Conversion and reaction constraints in Lactic Acid
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def fermenter4_initial_moles_rule(m, n, j, k):
            if n in ['Water','glucose', 'LacticAcid'] and j == 'LacticAcidProcess' and k == 'Fermenter':
                return m.InitialMolesFermenter4[ n,j,k] == m.FinLacticAcid1_component [ n, j,'Fermenter'] / m.MolecularWeightFermenter4[n]
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                return m.InitialMolesFermenter4[ n,j,k] == 0
            else:
                return Constraint.Skip
        m.Fermenter4InitialMolesConstraint = Constraint(m.Components, m.Biochemicals, m.Equipment,  rule=fermenter4_initial_moles_rule)
        #-------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_fermenter4_constraint_rule(m, n,  j, k):
            if n == 'LacticAcid' and j =='LacticAcidProcess' and k=='Fermenter':
                return m.MolesReactedFermenter4[ n,  j, k] == m.StoichiometricCoeffFermenter4[n] * m.ConversionFactorFermenter4 * m.InitialMolesFermenter4['glucose', j, 'Fermenter'] 
            elif n == 'glucose'and j =='LacticAcidProcess' and k=='Fermenter':
                return m.MolesReactedFermenter4[ n, j, k] == -m.StoichiometricCoeffFermenter4[n] * m.ConversionFactorFermenter4 * m.InitialMolesFermenter4['glucose', j,'Fermenter'] 
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return  m.MolesReactedFermenter4[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionFermenter4Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=reaction_fermenter4_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_fermenter4_moles_rule(m, n,  j, k):
            if n == 'glucose'and j =='LacticAcidProcess' and k=='Fermenter':
                return m.FinalMolesFermenter4[ n,  j, k] ==  m.InitialMolesFermenter4[ n, j,k]  - m.MolesReactedFermenter4[ n,  j, k]
            elif n in ['LacticAcid','Water']  and j =='LacticAcidProcess' and k=='Fermenter':
                return m.FinalMolesFermenter4[ n, j, k] == m.InitialMolesFermenter4[ n, j,k]  + m.MolesReactedFermenter4[ n,  j, k]
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                return m.FinalMolesFermenter4[ n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesFermenter4Constraint = Constraint(m.Components,  m.Biochemicals, m.Equipment, rule=final_fermenter4_moles_rule)
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_fermenter4_mass_rule(m,  n,  j, k):
            if n in ['Water','glucose','LacticAcid'] and j =='LacticAcidProcess' and k in ['Fermenter','Pump', 'Heater','DT']:
                return m.FinalMassFermenter4[n, j, k] == m.FinalMolesFermenter4[ n,  j, 'Fermenter'] * m.MolecularWeightFermenter4[n]
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                return m.FinalMassFermenter4[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassFermenter4Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule= final_fermenter4_mass_rule)
        
        #DistillationColumn-1
        # -------------------------------
        # Top column-1
        #-------------------------------
        def DT8_top_outflow_rule(m, n, j, k):
            if n in ['Water','glucose','LacticAcid']  and  j =='LacticAcidProcess' and k == 'DT':
                return m.FoutDT8_top_component [ n,  j, k]  ==  m.FinalMassFermenter4 [ n, j, 'DT']  * m.RecoveryTopDT8 [n]
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                return m.FoutDT8_top_component [ n,  j, k]  == 0
            else:
                return Constraint.Skip
        m.TopDT8outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT8_top_outflow_rule)
        # -------------------------------
        # Bottom column-1
        # -------------------------------
        def DT8_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','glucose','LacticAcid']  and j == 'LacticAcidProcess' and k in ['DT','Pump']:
                return m.FoutDT8_bottom_component[n, j, k]   ==  m.FinalMassFermenter4 [ n,  j, 'DT'] - m.FoutDT8_top_component [ n,  j, 'DT']
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT8_bottom_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT8outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT8_bottom_outflow_rule)
        
        # -------------------------------
        # Methaol consumption 
        # -------------------------------
        def total_methanol_needed_rule(m, n,j):
            if n=='Methanol' and j == 'LacticAcidProcess' :
                return m.total_methanol_needed[n,j] == sum(m.FoutDT8_bottom_component[ n,  j, 'DT'] for n in m.Components) * m.MethanolRatio
            elif n in m.Components  and j in m.Biochemicals:
                return m.total_methanol_needed[n,j] == 0
            else:
                return Constraint.Skip
        m.total_methanol_needed_constraint = Constraint(m.Components,  m.Biochemicals,  rule=total_methanol_needed_rule)
        
        ## -------------------------------
        # Flow balance pretreatment constraints (generalized for the same equipment)
        # -------------------------------- 
        def flow_lacticacid3_balance_rule(m, n, j, k):
            if n in ['Water','glucose','Methanol','LacticAcid'] and j =='LacticAcidProcess' and k in ['Heater','Reactor1']:
                return m.FinLacticAcid3_component [n,j,k] == m.FoutDT8_bottom_component [ n,j,'Pump'] + m.total_methanol_needed[n,'LacticAcidProcess']
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                  return  m.FinLacticAcid3_component[n,j,k] == 0 
            else:
                  return Constraint.Skip
        m.flow_lacticacid3_balance_constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flow_lacticacid3_balance_rule)
        
        # Conversion and reaction constraints in Lactic Acid
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def reactor1_initial_moles_rule(m, n, j, k):
            if n in ['Water','glucose','Methanol','LacticAcid']  and j =='LacticAcidProcess' and k=='Reactor1':
                return m.InitialMolesReactor1[ n,j,k] == m.FinLacticAcid3_component  [ n, j, 'Reactor1'] / m.MolecularWeightReactor1[n]
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                return m.InitialMolesReactor1[ n,j,k] == 0 
            else:
                return Constraint.Skip
        m.reactor1InitialMolesConstraint = Constraint(m.Components, m.Biochemicals, m.Equipment,  rule=reactor1_initial_moles_rule)
        #-------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_reactor1_constraint_rule(m, n,  j, k):
            if n in ['Water','MethylLactate'] and j =='LacticAcidProcess' and k=='Reactor1':
                return m.MolesReactedReactor1[ n,  j, k] == m.StoichiometricCoeffReactor1[n] * m.ConversionFactorReactor1 * m.InitialMolesReactor1['LacticAcid',  j, 'Reactor1'] 
            elif n in ['LacticAcid','Methanol'] and j =='LacticAcidProcess' and k=='Reactor1':
                return  m.MolesReactedReactor1[ n,  j, k] == -m.StoichiometricCoeffReactor1[n] * m.ConversionFactorReactor1 * m.InitialMolesReactor1['LacticAcid',  j, 'Reactor1'] 
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return   m.MolesReactedReactor1[ n,  j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionReactor1Constraint = Constraint(m.Components,m.Biochemicals, m.Equipment,  rule=reaction_reactor1_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_reactor1_moles_rule(m, n,  j, k):
            if n in ['LacticAcid','Methanol'] and j =='LacticAcidProcess' and k=='Reactor1':
                return m.FinalMolesReactor1[ n,  j, k] ==  m.InitialMolesReactor1[ n, j,k]  - m.MolesReactedReactor1[ n,  j, k]
            if n in ['Water','MethylLactate','glucose'] and j =='LacticAcidProcess' and k=='Reactor1':
                return m.FinalMolesReactor1[ n, j, k] == m.InitialMolesReactor1[ n, j,k]  + m.MolesReactedReactor1[ n,  j, k]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FinalMolesReactor1[ n,  j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesReactor1Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=final_reactor1_moles_rule)
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_reactor1_mass_rule(m,  n,  j, k):
            if n in ['Water','MethylLactate','glucose','LacticAcid','Methanol'] and j =='LacticAcidProcess' and k in ['Reactor1','Heater','DT']:
                return m.FinalMassReactor1[n, j, k] == m.FinalMolesReactor1[ n,  j, 'Reactor1'] * m.MolecularWeightReactor1[n]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FinalMassReactor1[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassReactor1Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule= final_reactor1_mass_rule)
        
        #DistillationColumn-2
        # -------------------------------
        # Bottom column-2
        #-------------------------------
        def DT9_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','glucose','LacticAcid','Methanol'] and j == 'LacticAcidProcess' and k=='DT':
                return m.FoutDT9_bottom_component [ n,  j, k]  ==  m.FinalMassReactor1 [ n,j,'DT'] * m.RecoveryBottomDT9 [n]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT9_bottom_component [ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT9outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT9_bottom_outflow_rule)
        # -------------------------------
        # Top column-2
        # -------------------------------
        def DT9_top_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','glucose','LacticAcid','Methanol'] and j == 'LacticAcidProcess' and k=='DT':
                return m.FoutDT9_top_component[n, j, k]  ==  m.FinalMassReactor1 [ n,j,'DT'] - m.FoutDT9_bottom_component [ n,  j, 'DT']
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT9_top_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT9outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT9_top_outflow_rule)
        
        #DistillationColumn-3
        # -------------------------------
        # Topcolumn-3
        #-------------------------------
        def DT10_top_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','glucose','LacticAcid','Methanol']   and j == 'LacticAcidProcess' and k=='DT':
                return m.FoutDT10_top_component [ n,  j, k]  ==  m.FoutDT9_top_component[n,j,'DT'] * m.RecoveryTopDT10 [n]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT10_top_component [ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT10outflow = Constraint(m.Components, m.Biochemicals, m.Equipment,  rule=DT10_top_outflow_rule)
        # -------------------------------
        # Bottom column-3
        #-------------------------------
        def DT10_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','glucose','LacticAcid','Methanol']   and j == 'LacticAcidProcess' and k in ['DT','Pump']:
                return m.FoutDT10_bottom_component[n, j, k]  ==  m.FoutDT9_top_component[n,j,'DT'] - m.FoutDT10_top_component [ n,  j, 'DT']
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT10_bottom_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT10outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT10_bottom_outflow_rule)
        
        # -------------------------------
        # Water consumption 
        # -------------------------------
        def pump9_composition_inflow_rule(m, n, j, k):
            if n in ['Water']  and j == 'LacticAcidProcess' and k == 'Pump':
                return m.Finpump9_component[n, j, k] == sum(m.FoutDT10_bottom_component[n, j, 'Pump'] for n in m.Components) * m.WaterRatio
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.Finpump9_component[n, j, k] == 0
            else:
                return Constraint.Skip
        m.pump9_composition_inflow = Constraint(m.Components, m.Biochemicals, m.Equipment,  rule=pump9_composition_inflow_rule)
        
        ## -------------------------------
        # Flow balance pretreatment constraints (generalized for the same equipment)
        # -------------------------------- 
        def flow_lacticacid4_balance_rule(m, n, j, k):
            if n in ['MethylLactate','LacticAcid','Water'] and j =='LacticAcidProcess' and k in ['Cooler','Reactor1']:
                return m.FinLacticAcid4_component [n,j,k] ==  m.FoutDT10_bottom_component [n, j, 'Pump'] + m.Finpump9_component[n,j,'Pump']
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                  return  m.FinLacticAcid4_component[n,j,k] == 0 
            else:
                  return Constraint.Skip
        m.flow_lacticacid4_balance_constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flow_lacticacid4_balance_rule)
        
        # Conversion and reaction constraints in Lactic Acid
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def reactor2_initial_moles_rule(m, n, j, k):
            if n in ['Water','MethylLactate','LacticAcid']  and j =='LacticAcidProcess' and k=='Reactor1':
                return m.InitialMolesReactor2[ n,j,k] == m.FinLacticAcid4_component [ n, j, 'Reactor1'] / m.MolecularWeightReactor2[n]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.InitialMolesReactor2[ n,j,k] == 0 
            else:
                return Constraint.Skip
        m.reactor2InitialMolesConstraint = Constraint(m.Components, m.Biochemicals, m.Equipment,  rule=reactor2_initial_moles_rule)
        #-------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_reactor2_constraint_rule(m, n,  j, k):
            if n in ['Methanol','LacticAcid'] and j =='LacticAcidProcess' and k=='Reactor1':
                return m.MolesReactedReactor2[ n,  j, k] == m.StoichiometricCoeffReactor2[n] * m.ConversionFactorReactor2 * m.InitialMolesReactor2['MethylLactate',  j, 'Reactor1'] 
            elif n in ['Water','MethylLactate'] and j =='LacticAcidProcess' and k=='Reactor1':
                return  m.MolesReactedReactor2[ n,  j, k] == -m.StoichiometricCoeffReactor2[n] * m.ConversionFactorReactor2 * m.InitialMolesReactor2['MethylLactate',  j,'Reactor1'] 
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return   m.MolesReactedReactor2[ n,  j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionReactor2Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment,   rule=reaction_reactor2_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_reactor2_moles_rule(m, n,  j, k):
            if n in ['Water','MethylLactate'] and j =='LacticAcidProcess' and k=='Reactor1':
                return m.FinalMolesReactor2[ n,  j, k] ==  m.InitialMolesReactor2[ n, 'LacticAcidProcess','Reactor1']  - m.MolesReactedReactor2[ n,  'LacticAcidProcess', 'Reactor1']
            elif n in ['Methanol','LacticAcid'] and j =='LacticAcidProcess' and k=='Reactor1':
                return m.FinalMolesReactor2[ n, j, k] == m.InitialMolesReactor2[ n, 'LacticAcidProcess','Reactor1']  + m.MolesReactedReactor2[ n,  'LacticAcidProcess', 'Reactor1']
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FinalMolesReactor2[ n,  j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesReactor2Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=final_reactor2_moles_rule)
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_reactor2_mass_rule(m,  n,  j, k):
            if n in ['Water','MethylLactate','Methanol','LacticAcid'] and j =='LacticAcidProcess' and k in ['Reactor1','Heater','DT']:
                return m.FinalMassReactor2[n, j, k] == m.FinalMolesReactor2[ n,  j, 'Reactor1'] * m.MolecularWeightReactor2[n]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FinalMassReactor2[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassReactor2Constraint = Constraint(m.Components,m.Biochemicals, m.Equipment,  rule= final_reactor2_mass_rule)
        
        #DistillationColumn-4
        # -------------------------------
        # Topcolumn-4
        #-------------------------------
        def DT11_top_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','Methanol','LacticAcid']   and j == 'LacticAcidProcess' and k=='DT':
                return m.FoutDT11_top_component [ n,  j, k]  ==  m.FinalMassReactor2 [ n,  j, 'DT'] * m.RecoveryTopDT11 [n]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT11_top_component [ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT11outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT11_top_outflow_rule)
        # -------------------------------
        # Bottom column-4
        #-------------------------------
        def DT11_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','Methanol','LacticAcid'] and j == 'LacticAcidProcess' and k=='DT':
                return m.FoutDT11_bottom_component[n, j, k]  == m.FinalMassReactor2 [ n,  j, 'DT'] -  m.FoutDT11_top_component [ n,  j, 'DT'] 
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT11_bottom_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT11outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT11_bottom_outflow_rule)
        
        #DistillationColumn-5
        # -------------------------------
        # Topcolumn-5
        #-------------------------------
        def DT12_top_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','Methanol','LacticAcid'] and j == 'LacticAcidProcess' and k=='DT':
                return m.FoutDT12_top_component [ n,  j, k]  ==  m.FoutDT11_top_component [ n,  j, 'DT'] * m.RecoveryTopDT12 [n]
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                return m.FoutDT12_top_component [ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT12outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT12_top_outflow_rule)
        # -------------------------------
        # Bottom column-5
        #-------------------------------
        def DT12_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','Methanol','LacticAcid'] and j == 'LacticAcidProcess' and k=='DT':
                return m.FoutDT12_bottom_component[n, j, k]  ==  m.FoutDT11_top_component [ n,  j, 'DT'] - m.FoutDT12_top_component [ n,  j, 'DT'] 
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT12_bottom_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT12outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=DT12_bottom_outflow_rule)
        
        #DistillationColumn-6
        # -------------------------------
        # Topcolumn-6
        #-------------------------------
        def DT13_top_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','Methanol','LacticAcid']   and j == 'LacticAcidProcess' and k=='DT':
                return m.FoutDT13_top_component [ n,  j, k]  ==  m.FoutDT11_bottom_component[n, j, 'DT'] * m.RecoveryTopDT13 [n]
            elif n in m.Components  and j in  m.Biochemicals and k in m.Equipment:
                return m.FoutDT13_top_component [ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT13outflow = Constraint(m.Components,m.Biochemicals, m.Equipment, rule=DT13_top_outflow_rule)
        # -------------------------------
        # Bottom column-6
        #-------------------------------
        def DT13_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','MethylLactate','Methanol','LacticAcid']   and j == 'LacticAcidProcess' and k=='DT':
                return m.LacticAcidProduct[n, j, k]  ==  m.FoutDT11_bottom_component[n, j, 'DT'] - m.FoutDT13_top_component [ n,  j, 'DT']
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.LacticAcidProduct[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT13outflow = Constraint(m.Components,m.Biochemicals, m.Equipment, rule=DT13_bottom_outflow_rule)
        
        # -------------------------------
        # Waste to AD
        #-------------------------------
        def Lactic_waste_rule(m,n,j):
            if n in ['Water','LacticAcid','glucose','MethylLactate','Methanol'] and j =='LacticAcidProcess':
                return m.Lactic_waste [n,j] == m.FoutDT9_bottom_component [ n,'LacticAcidProcess', 'DT'] + m.FoutDT8_top_component [ n,'LacticAcidProcess', 'DT']
            elif n in m.Components  and j in m.Biochemicals:
                return m.Lactic_waste  [ n,  j]  == 0 
            else:
                return Constraint.Skip
        m.Lactic_waste_constraint = Constraint(m.Components, m.Biochemicals, rule=Lactic_waste_rule)

# ======================================================
# Succinic Acid Process Model
# ======================================================
class SuccinicAcidModel:
    """SuccinicAcid process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Succinic Acid constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model

        ## -------------------------------
        # Flow balance pretreatment constraints (generalized for the same equipment)
        # -------------------------------- 
        def flow_succinicacid1_balance_rule(m, n, j, k):
            if n in ['glucose','Water'] and j =='SuccinicAcidProcess' and k in ['Pump', 'Cooler', 'Fermenter']:
                return m.FinSuccinicAcid1_component [n,j,k] ==  m.Finglucose_biochemical_component[ n,'SuccinicAcidProcess']
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                  return  m.FinSuccinicAcid1_component[n,j,k] == 0 
            else:
                  return Constraint.Skip
        m.flow_succinicacid1_balance_constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flow_succinicacid1_balance_rule)
        
        ## -------------------------------
        # CO2 consumption
        # -------------------------------- 
        def CO2_inflow_SA_rule(m, n, j):
            if n =='CO2' and j == 'SuccinicAcidProcess':
                return m.CO2_stream_Succinic[n, j] == m.FinSuccinicAcid1_component ['glucose','SuccinicAcidProcess' ,'Fermenter']   * m.CO2ConsumptionSA
            elif n in m.Components and j in m.Biochemicals:
                return m.CO2_stream_Succinic [n, j] == 0
            else:
                return Constraint.Skip
        m.CO2inflowSA = Constraint(m.Components, m.Biochemicals, rule=CO2_inflow_SA_rule)
        
        # Conversion and reaction constraints in Lactic Acid
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def fermenter5_initial_moles_rule(m, n, j, k):
            if n in ['Water','glucose'] and j == 'SuccinicAcidProcess' and k == 'Fermenter':
                return m.InitialMolesFermenter5[ n,j,k] == m.FinSuccinicAcid1_component [ n, j, 'Fermenter'] / m.MolecularWeightFermenter5[n]
            elif n =='CO2' and j == 'SuccinicAcidProcess' and k == 'Fermenter':
                return m.InitialMolesFermenter5[ n,j,k] == m.CO2_stream_Succinic[n, j] / m.MolecularWeightFermenter5[n] 
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.InitialMolesFermenter5[ n,j,k] == 0
            else:
                return Constraint.Skip
        m.Fermenter5InitialMolesConstraint = Constraint(m.Components,m.Biochemicals, m.Equipment,  rule=fermenter5_initial_moles_rule)
        #-------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_fermenter5_constraint_rule(m, n,  j, k):
            if n in ['SuccinicAcid','Water'] and j =='SuccinicAcidProcess' and k=='Fermenter':
                return m.MolesReactedFermenter5[ n,  j, k] == m.StoichiometricCoeffFermenter5[n] * m.ConversionFactorFermenter5 * m.InitialMolesFermenter5['CO2',  j, 'Fermenter'] 
            elif n in ['glucose','CO2'] and j =='SuccinicAcidProcess' and k=='Fermenter':
                return m.MolesReactedFermenter5[ n, j, k] == -m.StoichiometricCoeffFermenter5[n] * m.ConversionFactorFermenter5 * m.InitialMolesFermenter5['CO2', j,'Fermenter'] 
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return  m.MolesReactedFermenter5[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionFermenter5Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=reaction_fermenter5_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_fermenter5_moles_rule(m, n,  j, k):
            if n in ['glucose','CO2'] and j =='SuccinicAcidProcess' and k=='Fermenter':
                return m.FinalMolesFermenter5[ n,  j, k] ==  m.InitialMolesFermenter5[ n, j,k]  - m.MolesReactedFermenter5[ n,  j, k]
            elif n in ['SuccinicAcid','Water']  and j =='SuccinicAcidProcess' and k=='Fermenter':
                return m.FinalMolesFermenter5[ n, j, k] == m.InitialMolesFermenter5[ n, j,k]  + m.MolesReactedFermenter5[ n,  j, k]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FinalMolesFermenter5[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.FinalMolesFermenter5Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=final_fermenter5_moles_rule)
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_fermenter5_mass_rule(m,  n,  j, k):
            if n in ['Water','glucose','SuccinicAcid'] and j =='SuccinicAcidProcess' and k in ['Fermenter','Evaporator']:
                return m.FinalMassFermenter5[n, j, k] == m.FinalMolesFermenter5[ n,  j, 'Fermenter'] * m.MolecularWeightFermenter5[n]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FinalMassFermenter5[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassFermenter5Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule= final_fermenter5_mass_rule)

        # Evaporator
        # -------------------------------
        # Top 
        #-------------------------------
        def Evaporator2_top_outflow_rule(m, n, j, k):
            if n == 'Water'  and j == 'SuccinicAcidProcess' and k=='Evaporator':
                return m.FoutEvaporator2_top_component [ n,  j, k]  ==  m.FinalMassFermenter5[n, j, 'Evaporator'] * m.TopEvaporator [n]
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutEvaporator2_top_component  [ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopEvaporator2outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=Evaporator2_top_outflow_rule)
        # -------------------------------
        # Bottom 
        # -------------------------------
        def Evaporator2_bottom_outflow_rule(m, n, j, k):
            if n in ['Water', 'glucose','SuccinicAcid'] and j == 'SuccinicAcidProcess' and k in ['Evaporator','Cooler','Crystallizer','Centrifugal']:
                return m.FoutEvaporator2_bottom_component[n, j, k] == m.FinalMassFermenter5[n, j, 'Evaporator'] - m.FoutEvaporator2_top_component [ n,  j, 'Evaporator']
            elif n in m.Components  and j in m.Biochemicals and k in m.Equipment:
                return m.FoutEvaporator2_bottom_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomEvaporator2outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=Evaporator2_bottom_outflow_rule)

        # Centrifugal
        # -------------------------------
        # Solid 
        #-------------------------------
        def SuccinicAcid_product_rule(m, n, j, k):
            if n == 'SuccinicAcid' and j =='SuccinicAcidProcess' and k =='Centrifugal':
                return m.SuccinicAcidProduct[n, j, k] == m.FoutEvaporator2_bottom_component[n, 'SuccinicAcidProcess','Centrifugal'] *0.98
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.SuccinicAcidProduct[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.SuccinicAcid_product_constraint = Constraint(m.Components,m.Biochemicals, m.Equipment,  rule=SuccinicAcid_product_rule)
        # -------------------------------
        # Liquid
        # -------------------------------
        def centrifugal6_liquid_outflow_rule(m, n, j, k):
            if n in ['Water', 'glucose','SuccinicAcid'] and j =='SuccinicAcidProcess'  and k =='Centrifugal':
                return m.FoutCentrifugal6_liquid_component [n, j, k] ==  m.FoutEvaporator2_bottom_component[n, 'SuccinicAcidProcess','Centrifugal'] - m.SuccinicAcidProduct[n, j,'Centrifugal']
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.FoutCentrifugal6_liquid_component [n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.centrifugal6_liquid_outflow_constraint = Constraint( m.Components, m.Biochemicals, m.Equipment, rule=centrifugal6_liquid_outflow_rule)

        # -------------------------------
        # Waste
        # -------------------------------
        def Waste_outflow_rule(m, n, j):
            if n in ['Water', 'glucose','SuccinicAcid'] and j == 'SuccinicAcidProcess' :
                return m.Succinic_waste[n, j] == m.FoutEvaporator2_top_component [ n,  j, 'Evaporator'] + m.FoutCentrifugal6_liquid_component [n, j, 'Centrifugal']
            elif n in m.Components  and j in m.Biochemicals :
                return m.Succinic_waste[n, j]  == 0 
            else:
                return Constraint.Skip
        m.Wasteoutflow = Constraint(m.Components, m.Biochemicals, rule=Waste_outflow_rule)
        
# ======================================================
# BDO Process Model
# ======================================================        
class BDOModel:
    """BDO process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach BDO constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model

        ## -------------------------------
        # Air consumption
        # -------------------------------- 
        def air_comp1_inflow_rule(m, n, j, k):
            if n in ['O2', 'N2'] and j == 'BDOProcess' and k == 'Comp':
                total_stream_cooler4 = sum(m.Finglucose_biochemical_component[ n,'BDOProcess'] for n in m.Components)
                return m.Fincomp1[n, j, k] == total_stream_cooler4 * m.AirConsumptionBDO[n,'BDOProcess', 'Comp']
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.Fincomp1[n, j, k] == 0
            else:
                return Constraint.Skip
        m.AirinflowComp1 = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=air_comp1_inflow_rule)
        ## -------------------------------
        # Flow balance pretreatment constraints (generalized for the same equipment)
        # -------------------------------- 
        def flow_bdo_balance_rule(m, n, j, k):
            if n in ['glucose','Water'] and j == 'BDOProcess' and k in ['Pump', 'Cooler','Fermenter']:
                return m.FinBDO_component[n,j,k] == m.Finglucose_biochemical_component[ n,'BDOProcess']
            elif n in ['O2','N2'] and j =='BDOProcess' and k in ['Fermenter']:
                return m.FinBDO_component[n,j,k] ==  m.Fincomp1[n, j, 'Comp']
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                  return  m.FinBDO_component[n,j,k] == 0 
            else:
                  return Constraint.Skip
        m.flow_bdo_balance_constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flow_bdo_balance_rule)
        
        # Conversion and reaction constraints in BDO
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def fermenter2_initial_moles_rule(m, n, j, k):
            if n in ['glucose','Water','O2','N2'] and j =='BDOProcess'  and k=='Fermenter':
                return m.InitialMolesFermenter2 [ n,j,k] ==  m.FinBDO_component[n,j, 'Fermenter'] / m.MolecularWeightFermenter2[n]
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.InitialMolesFermenter2 [ n,j,k] == 0
            else:
                return Constraint.Skip
        m.Fermenter2InitialMolesConstraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=fermenter2_initial_moles_rule)
        #-------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_fermenter2_constraint_rule(m, n,  j, k):
            if n in ['BDO','CO2','Water','N2'] and j =='BDOProcess' and k=='Fermenter':
                return m.MolesReactedFermenter2[ n,  j, k] == m.StoichiometricCoeffFermenter2[n] * m.ConversionFactorFermenter2 * m.InitialMolesFermenter2['glucose',  j, 'Fermenter'] 
            elif n in ['glucose','O2'] and j =='BDOProcess' and k=='Fermenter':
                return m.MolesReactedFermenter2[ n, j, k] == -m.StoichiometricCoeffFermenter2[n] * m.ConversionFactorFermenter2 * m.InitialMolesFermenter2[ 'glucose', j, 'Fermenter'] 
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return  m.MolesReactedFermenter2[ n, j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionFermenter2Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=reaction_fermenter2_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_fermenter2_moles_rule(m, n,  j, k):
            if n in ['glucose','O2'] and j =='BDOProcess' and k=='Fermenter':
                return m.FinalMolesFermenter2[ n,  j, k] ==  m.InitialMolesFermenter2[ n, j,k]  - m.MolesReactedFermenter2[ n,  j, k]
            elif n in ['BDO','CO2','Water','N2'] and j =='BDOProcess' and k=='Fermenter':
                return m.FinalMolesFermenter2[ n, j, k] == m.InitialMolesFermenter2[ n, j,k]  + m.MolesReactedFermenter2[ n,  j, k]
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.FinalMolesFermenter2[ n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesFermenter2Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=final_fermenter2_moles_rule)
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_fermenter2_mass_rule(m,  n,  j, k):
            if n in ['Water','O2','N2','CO2','BDO'] and j =='BDOProcess' and k in ['Fermenter','FlashDrum']:
                return m.FinalMassFermenter2[n, j, k] == m.FinalMolesFermenter2[ n,j,'Fermenter'] * m.MolecularWeightFermenter2[n]
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.FinalMassFermenter2[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassFermenter2Constraint = Constraint(m.Components, m.Biochemicals, m.Equipment, rule= final_fermenter2_mass_rule)

        # Flash Drum
        # -------------------------------
        # Top 
        #-------------------------------
        def flashdrum2_top_outfloe_rule(m, n,j,k):
            if n in ['Water','O2','N2','CO2','BDO'] and j == 'BDOProcess' and k=='FlashDrum':
                return m.Foutflashdrum2_gas_component[n, j, k] == m.FinalMassFermenter2[n, j,'FlashDrum'] * m.TopFlashdrum2[n]
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.Foutflashdrum2_gas_component[n, j, k] == 0
            else:
                Constraint.Skip
        m.Topflashdrum2outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flashdrum2_top_outfloe_rule)
        # -------------------------------
        # Bottom 
        # -------------------------------
        def flashdrum2_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','O2','N2','CO2','BDO'] and j == 'BDOProcess' and k in ['FlashDrum','DT']:
                return m.Foutflashdrum2_liquid_component[n, j, k] == m.FinalMassFermenter2[n, j,'FlashDrum'] - m.Foutflashdrum2_gas_component[n, j, 'FlashDrum']
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.Foutflashdrum2_liquid_component[n, j, k] == 0
            else:
                Constraint.Skip
        m.Bottomflashdrum2outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flashdrum2_bottom_outflow_rule)

        #DistillationColumn
        # -------------------------------
        # Top-gas column
        #-------------------------------
        def DT3_top_gas_outflow_rule(m, n, j, k):
            if n in ['Water','O2','N2','CO2','BDO']  and j == 'BDOProcess' and k in ['DT','FlashDrum']:
                return m.FoutDT3_top_gas_component[n, j, k] == m.Foutflashdrum2_liquid_component[n, j, 'DT'] * m.TopgasDT3[n]
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT3_top_gas_component[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.TopGasDT3outflow = Constraint(m.Components, m.Biochemicals, m.Equipment,  rule=DT3_top_gas_outflow_rule)
        # -------------------------------
        # Top-liquid column
        # -------------------------------
        def DT3_top_liquid_outflow_rule(m, n, j, k):
            if n in ['Water','O2','N2','CO2','BDO']  and j == 'BDOProcess' and k=='DT':
                return m.FoutDT3_top_liquid_component[n, j, k] == m.Foutflashdrum2_liquid_component[n, j, 'DT'] * m.TopliquidDT3[n]
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.FoutDT3_top_liquid_component[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.TopLiquidDT3outflow = Constraint(m.Components, m.Biochemicals, m.Equipment,  rule=DT3_top_liquid_outflow_rule)
        # -------------------------------
        # Bottom column
        # -------------------------------
        def BDO_product_outflow_rule(m, n, j, k):
            if n in ['Water','BDO']  and j == 'BDOProcess' and k=='DT':
                return m.BDO_product[n, j, k] == m.Foutflashdrum2_liquid_component[n, j, 'DT'] - m.FoutDT3_top_gas_component[n, j, 'DT'] - m.FoutDT3_top_liquid_component[n, j, 'DT']
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.BDO_product[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.BDOProductoutflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=BDO_product_outflow_rule)

        # Flash Drum
        # -------------------------------
        # Top 
        #-------------------------------
        def flashdrum3_top_outflow_rule(m, n, j, k):
            if n in ['CO2','O2','N2'] and j == 'BDOProcess' and k=='FlashDrum':
                return m.Foutflashdrum3_gas_component[n, j, k] == m.FoutDT3_top_gas_component[n, j, 'FlashDrum'] * m.TopFlashdrum3[n]
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.Foutflashdrum3_gas_component[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.Topflashdrum3outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flashdrum3_top_outflow_rule)
        # -------------------------------
        # Bottom 
        # -------------------------------
        def flashdrum3_bottom_outflow_rule(m, n, j, k):
            if n in ['BDO','Water'] and j == 'BDOProcess' and k=='FlashDrum':
                return m.Foutflashdrum3_liquid_component[n, j, k]  == m.FoutDT3_top_gas_component[n, j, 'FlashDrum'] - m.Foutflashdrum3_gas_component[n, j,'FlashDrum'] 
            elif n in m.Components and j in m.Biochemicals and k in m.Equipment:
                return m.Foutflashdrum3_liquid_component[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.Bottomflashdrum3outflow = Constraint(m.Components, m.Biochemicals, m.Equipment, rule=flashdrum3_bottom_outflow_rule)

        # -------------------------------
        # Waste
        # -------------------------------
        def total_BDO_waste_rule(m, n,j):
            if n in ['Water','O2','N2','CO2','BDO'] and j == 'BDOProcess':
                return m.totalwaste_BDO [n,j] == m.FoutDT3_top_liquid_component[n, j,'DT'] + m.Foutflashdrum3_liquid_component[n, j, 'FlashDrum']
            elif n in m.Components and j in m.Biochemicals :
                return m.totalwaste_BDO [n, j]  == 0 
            else:
                return Constraint.Skip
        m.total_BDO_waste_constraint = Constraint(m.Components, m.Biochemicals, rule=total_BDO_waste_rule)

        # -------------------------------
        # CO2
        # -------------------------------
        def CO2_total_stream_BDO_rule(m, n,j):
            return m.CO2_stream_BDO[n,j] == m.Foutflashdrum2_gas_component[n, j, 'FlashDrum'] + m.Foutflashdrum3_gas_component[n, j, 'FlashDrum']
        m.CO2_total_stream_BDO_constraint = Constraint(m.Components, m.Biochemicals, rule=CO2_total_stream_BDO_rule)
      
# ======================================================
# Biodiesel Process Model
# ====================================================== 
class BiodieselModel:
    """Biodiesel process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Biodiesel constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Hexane
        # --------------------------------        
        def hexane_inflow_rule(m, n, j):
            if n =='Hexane' and j == 'BiodieselProcess':
                return m.FHexane[n, j] ==  sum(m.FCentrifugal1_Solid[n, 'enzymatic-hydrolysis', 'Centrifugal']   for n in m.Components)* m.ChemicalConsumptionNonFermentation['Hexane','BiodieselProcess']
            elif n in m.Components and j in  m.NonGlucoseUpgrading:
                return m.FHexane[n, j] == 0
            else:
                return Constraint.Skip
        m.hexane_inflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, rule=hexane_inflow_rule)
        ## -------------------------------
        # Lipid extraction
        # --------------------------------
        def biodiesel1_inflow_rule(m, n, j, k):
            if n in ['Carbohydrate','Protein','Lipid'] and j == 'BiodieselProcess' and k in ['Extractor','Centrifugal']:
                return m.FBiodiesel1 [n, j, k] == m.FCentrifugal1_Solid [n, 'enzymatic-hydrolysis', 'Centrifugal'] 
            elif n == 'Hexane' and j == 'BiodieselProcess' and k in ['Extractor','Centrifugal']:
                return m.FBiodiesel1 [n, j, k] ==  m.FHexane[n, j]
            elif n in m.Components and j in  m.NonGlucoseUpgrading and k in m.Equipment: 
                return m.FBiodiesel1 [n, j, k] == 0
            else:
                return Constraint.Skip
        m.biodiesel1_inflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=biodiesel1_inflow_rule)
        
        # Centrifugal
        # -------------------------------
        # Centrifugal solid outflow
        # -------------------------------
        def centrifugal2_solid_outflow_rule(m, n, j, k):
            if n in ['Carbohydrate','Protein'] and j =='BiodieselProcess' and k == 'Centrifugal':
                return m.FCentrifugal2_Solid[n, j, k] == m.FBiodiesel1 [n, j, 'Centrifugal']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FCentrifugal2_Solid[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.centrifugal2_solid_outflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=centrifugal2_solid_outflow_rule)
        # -------------------------------
        # Centrifugal liquid outflow
        # -------------------------------
        def centrifugal2_liquid_outflow_rule(m, n, j, k):
            if n in ['Hexane','Lipid'] and j =='BiodieselProcess' and k in ['Centrifugal','Evaporator']:
                return m.FCentrifugal2_Liquid[n, j, k] == m.FBiodiesel1 [n, j, 'Centrifugal'] - m.FCentrifugal2_Solid[n, j, 'Centrifugal']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FCentrifugal2_Liquid[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.centrifugal2_liquid_outflow_constraint = Constraint( m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=centrifugal2_liquid_outflow_rule)

        # Evaporator
        # -------------------------------
        # Top evaporator
        # -------------------------------
        def evaporator1_gas_outflow_rule(m, n, j, k):
            if n == 'Hexane' and j =='BiodieselProcess' and k == 'Evaporator':
                return m.FEvaporator1_gas [n, j, k] == m.FCentrifugal2_Liquid [n, j,'Evaporator']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FEvaporator1_gas [n, j, k] == 0 
            else:
                return Constraint.Skip
        m.evaporator1_gas_outflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=evaporator1_gas_outflow_rule)
        # -------------------------------
        # Bottom evaporator
        # -------------------------------
        def evaporator1_liquid_outflow_rule(m, n, j, k):
            if n == 'Lipid' and j =='BiodieselProcess' and k in ['Evaporator','Pump']:
                return m.FEvaporator1_liquid [n, j, k] ==  m.FCentrifugal2_Liquid [n, j,'Evaporator']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FEvaporator1_liquid [n, j, k] == 0 
            else:
                return Constraint.Skip
        m.evaporator1_liquid_outflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=evaporator1_liquid_outflow_rule)

        # -------------------------------
        # Methanol and NaOH stream
        # -------------------------------
        def Chemical_inflow_rule(m, n, j,k):
            if n in ['Methanol','NaOH'] and j == 'BiodieselProcess' and k in ['Pump', 'Heater']: 
                return m.ChemicalBiodieselStream[n, j,k] ==  sum(m.FEvaporator1_liquid[n, j, 'Pump'] for n in m.Components)* m.ChemicalConsumptionNonFermentation[n,'BiodieselProcess']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.ChemicalBiodieselStream[n, j,k] == 0
            else:
                return Constraint.Skip
        m.Chemical_inflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=Chemical_inflow_rule)
        
        # Conversion and reaction constraints in Transesterification
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def TranesterReactor_initial_moles_rule(m, n, j, k):
            if n in ['Lipid','Methanol','NaOH']  and  j =='BiodieselProcess' and k == 'TranesterReactor':
                return m.InitialMolesTranesterReactor[ n,j,k] == (m.FEvaporator1_liquid [n, j, 'Pump'] + m.ChemicalBiodieselStream[n, j, 'Heater'] ) / m.MolecularWeightTranesterReactor[n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.InitialMolesTranesterReactor[ n,j,k] == 0 
            else:
                return Constraint.Skip
        m.TranesterReactorInitialMolesConstraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=TranesterReactor_initial_moles_rule)
        # -------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_TranesterReactor_constraint_rule(m, n,  j, k):
            if n in ['FAME','Glycerol'] and j =='BiodieselProcess'and k == 'TranesterReactor':
                return m.MolesReactedTranesterReactor[ n,  j, k] == m.StoichiometricCoeffTranesterReactor[n] * m.ConversionFactorTranesterReactor * m.InitialMolesTranesterReactor['Lipid',  j, 'TranesterReactor'] 
            elif n in ['Lipid','Methanol'] and j=='BiodieselProcess' and k == 'TranesterReactor':
                return  m.MolesReactedTranesterReactor[ n,  j, k] == -m.StoichiometricCoeffTranesterReactor[n] * m.ConversionFactorTranesterReactor * m.InitialMolesTranesterReactor[ 'Lipid',  j, 'TranesterReactor'] 
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return   m.MolesReactedTranesterReactor[ n,  j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionTranesterReactorConstraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=reaction_TranesterReactor_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_TranesterReactor_moles_rule(m, n,  j, k):
            if n in ['Lipid','Methanol'] and j =='BiodieselProcess'and k == 'TranesterReactor':
                return m.FinalMolesTranesterReactor[ n,  j, k] ==  m.InitialMolesTranesterReactor[ n, j,k]  - m.MolesReactedTranesterReactor[ n,  j, k]
            if n in ['FAME','Glycerol','NaOH'] and j =='BiodieselProcess'and k == 'TranesterReactor':
                return m.FinalMolesTranesterReactor[ n, j, k] == m.InitialMolesTranesterReactor[ n, j,k]  + m.MolesReactedTranesterReactor[ n,  j, k]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FinalMolesTranesterReactor[ n,  j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesTranesterReactorConstraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=final_TranesterReactor_moles_rule)       
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_TranesterReactor_mass_rule(m,  n,  j, k):
            if n in ['Lipid','Methanol','NaOH','FAME','Glycerol'] and j =='BiodieselProcess' and k in ['TranesterReactor','DT']:
                return m.FinalMassTranesterReactor[n, j, k] == m.FinalMolesTranesterReactor[ n,  j,'TranesterReactor'] * m.MolecularWeightTranesterReactor[n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FinalMassTranesterReactor[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassTranesterReactorConstraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule= final_TranesterReactor_mass_rule)

        #DistillationColumn-1
        # -------------------------------
        # Top column-1
        # -------------------------------
        def DT14_top_outflow_rule(m, n, j, k):
            if n in ['Lipid','Methanol','NaOH','FAME','Glycerol'] and  j =='BiodieselProcess' and k=='DT':
                return m.FDT14_top [ n,  j, k]  ==  m.FinalMassTranesterReactor[n, 'BiodieselProcess', 'DT']  * m.RecoveryTopDT14 [n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FDT14_top [ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT14outflow = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=DT14_top_outflow_rule)
        # -------------------------------
        # Bottom column-1
        # -------------------------------
        def flow_biodiesel4_balance_rule(m, n, j, k):
            if n in ['Lipid','Methanol','NaOH','FAME','Glycerol'] and  j =='BiodieselProcess' and k in ['DT','Pump','Cooler']:
                return m.FDT14_bottom[n,j,k] == m.FinalMassTranesterReactor[n, 'BiodieselProcess', 'DT']  - m.FDT14_top [ n,  j, 'DT']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                  return  m.FDT14_bottom[n,j,k] == 0   
            else:
                  return Constraint.Skip
        m.flow_biodiesel4_balance_rule = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=flow_biodiesel4_balance_rule)

        # -------------------------------
        # Water stream
        # -------------------------------
        def water_biodiesel_inflow_rule(m, n, j):
            if n =='Water' and j == 'BiodieselProcess' :
                return m.WaterStreamBiodiesel [n, j] ==  sum(m.FDT14_bottom[ n,  j, 'Cooler'] for n in m.Components)* m.ChemicalConsumptionNonFermentation['Water','BiodieselProcess']
            elif n in m.Components and j in m.NonGlucoseUpgrading:
                return m.WaterStreamBiodiesel [n, j] == 0
            else:
                return Constraint.Skip
        m.water_biodiesel_inflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading,  rule=water_biodiesel_inflow_rule)

        # Washer
        # -------------------------------
        # Inlet for washer
        # -------------------------------
        def washer_composition_inflow_rule(m, n, j, k):
            if n in ['Methanol','Lipid','NaOH','FAME','Glycerol','Water']  and j =='BiodieselProcess'  and k=='Washer':
                return m.FWasher [ n,  j, k] == m.FDT14_bottom[ n,  j, 'Cooler'] + m.WaterStreamBiodiesel [n, j]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FWasher [ n,  j, k] == 0 
            else:
                return Constraint.Skip
        m.washercomposition_inflow = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=washer_composition_inflow_rule)
        # -------------------------------
        # Top washer
        # -------------------------------
        def washer_top_outflow_rule(m, n, j, k):
            if n in ['Water','Lipid','Methanol','NaOH','FAME','Glycerol'] and j =='BiodieselProcess' and k in ['Washer','DT']:
                return m.FWasher_top [ n,  j, k] == m.FWasher[ n,  j, 'Washer'] * m.RecoveryTopWasher[n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FWasher_top [ n,  j, k] == 0 
            else:
                return Constraint.Skip
        m.washeroutflow = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=washer_top_outflow_rule)
        # -------------------------------
        # Bottom washer
        # -------------------------------
        def washer_bottom_outflow_rule(m, n, j,  k):
            return m.FWasher_bottom[n, j, k] == m.FWasher[ n,  j, 'Washer'] - m.FWasher_top [ n,  j, 'Washer']
        m.Bottomwasheroutflow = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=washer_bottom_outflow_rule)

        #DistillationColumn-2
        # -------------------------------
        # Top column-2
        # -------------------------------
        def biodiesel_product_outflow_rule(m, n, j, k):
            if n in ['FAME','Water'] and j =='BiodieselProcess' and k=='DT':
                return m.Biodiesel_product [ n,  j, k]  ==  m.FWasher_top [ n,  j, 'DT'] * m.RecoveryBiodieselProduct [n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.Biodiesel_product [ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.BiodieselProductflow = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=biodiesel_product_outflow_rule)
        # -------------------------------
        # Bottom column-2
        # -------------------------------
        def DT15_bottom_outflow_rule(m, n, j, k):
            if n in ['Lipid','FAME','Water'] and j =='BiodieselProcess' and k=='DT':
                return m.FDT15_bottom[n, j, k] == m.FWasher_top[ n,  j, 'DT'] - m.Biodiesel_product [ n,  j, 'DT']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return  m.FDT15_bottom[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT15outflow = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=DT15_bottom_outflow_rule)

        # -------------------------------
        # H3PO4 stream
        # -------------------------------
        def H3PO4_biodiesel_inflow_rule(m, n, j, k):
            if n =='H3PO4' and j == 'BiodieselProcess' and k == 'Neutralizer':
                return m.H3PO4Stream [n, j, k] ==  sum(m.FWasher_bottom[n, j, 'Washer'] for n in m.Components)* m.ChemicalConsumptionNonFermentation['H3PO4','BiodieselProcess']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.H3PO4Stream [n, j, k] == 0
            else:
                return Constraint.Skip
        m.H3PO4_biodiesel_inflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=H3PO4_biodiesel_inflow_rule)
 
        # Conversion and reaction constraints in Neutralization
        # -------------------------------
        # Initial moles (mass to moles)
        # -------------------------------
        def Neutralizer_initial_moles_rule(m, n, j, k):
            if n in ['NaOH','Methanol','Water','H3PO4','Na3PO4','Glycerol']  and  j == 'BiodieselProcess' and k == 'Neutralizer':
                return m.InitialMolesNeutralizer[ n,j,k] == (m.FWasher_bottom[n, j, 'Washer'] + m.H3PO4Stream [n, j, 'Neutralizer']) / m.MolecularWeightNeutralizer[n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.InitialMolesNeutralizer[ n,j,k] == 0 
            else:
                return Constraint.Skip
        m.NeutralizerInitialMolesConstraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=Neutralizer_initial_moles_rule)
        # -------------------------------
        # Reaction constraints
        # -------------------------------
        def reaction_Neutralizer_constraint_rule(m, n,  j, k):
            if n in ['Water','Na3PO4'] and j =='BiodieselProcess' and k == 'Neutralizer':
                return m.MolesReactedNeutralizer[ n,  j, k] == m.StoichiometricCoeffNeutralizer[n] * m.ConversionFactorNeutralizer * m.InitialMolesNeutralizer['NaOH',  j, 'Neutralizer'] 
            elif n in ['NaOH','H3PO4'] and  j =='BiodieselProcess' and k == 'Neutralizer':
                return  m.MolesReactedNeutralizer[ n,  j, k] == -m.StoichiometricCoeffNeutralizer[n] * m.ConversionFactorNeutralizer * m.InitialMolesNeutralizer['NaOH',  j,'Neutralizer'] 
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return   m.MolesReactedNeutralizer[ n,  j, k] == 0
            else:
                return Constraint.Skip
        m.ReactionNeutralizerConstraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=reaction_Neutralizer_constraint_rule)
        # -------------------------------
        # Final moles after reaction
        # -------------------------------
        def final_Neutralizer_moles_rule(m, n,  j, k):
            if n in ['NaOH','H3PO4'] and j =='BiodieselProcess' and k == 'Neutralizer':
                return m.FinalMolesNeutralizer[ n,  j, k] ==  m.InitialMolesNeutralizer[ n, j,k]  - m.MolesReactedNeutralizer[ n,  j, k]
            elif n in ['Water','Na3PO4','Methanol','Glycerol'] and j =='BiodieselProcess' and k == 'Neutralizer':
                return m.FinalMolesNeutralizer[ n, j, k] == m.InitialMolesNeutralizer[ n, j,k]  + m.MolesReactedNeutralizer[ n,  j, k]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FinalMolesNeutralizer[ n,  j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMolesNeutralizerConstraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=final_Neutralizer_moles_rule)     
        #-------------------------------
        # Final mass (moles to mass)
        # -------------------------------
        def final_Neutralizer_mass_rule(m,  n,  j, k):
            if n in ['Methanol','Water','H3PO4','Na3PO4','Glycerol'] and j =='BiodieselProcess' and k in ['Neutralizer','Centrifugal']:
                return m.FinalMassNeutralizer[n, j, k] == m.FinalMolesNeutralizer[ n,  j, 'Neutralizer'] * m.MolecularWeightNeutralizer[n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FinalMassNeutralizer[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.FinalMassNeutralizerConstraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule= final_Neutralizer_mass_rule)
        
        # Centrifugal
        # -------------------------------
        # Centrifugal solid outflow
        # -------------------------------
        def centrifugal3_solid_outflow_rule(m, n, j, k):
            if n in ['H3PO4','Na3PO4'] and j == 'BiodieselProcess' and k == 'Centrifugal':
                return m.FCentrifugal3_Solid[n, j, k] == m.FinalMassNeutralizer[ n,  j, 'Centrifugal'] 
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FCentrifugal3_Solid[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.centrifugal3_solid_outflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=centrifugal3_solid_outflow_rule)
        # -------------------------------
        # Centrifugal liquid outflow
        # -------------------------------
        def centrifugal3_liquid_outflow_rule(m, n, j, k):
            if n in ['Methanol','Water','Glycerol'] and j == 'BiodieselProcess' and k in ['Centrifugal','DT']:
                return m.FCentrifugal3_Liquid[n, j, k] ==m.FinalMassNeutralizer[ n,  j,'Centrifugal']  - m.FCentrifugal3_Solid[n, j, 'Centrifugal']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FCentrifugal3_Liquid[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.centrifugal3_liquid_outflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=centrifugal3_liquid_outflow_rule)
        
        #DistillationColumn-3
        # -------------------------------
        # Top column-3
        # -------------------------------
        def DT16_top_outflow_rule(m, n, j, k):
            if n in ['Methanol','Water'] and j == 'BiodieselProcess' and k=='DT':
                return m.FDT16_top [ n,  j, k]  ==  m.FCentrifugal3_Liquid[n, j, 'DT'] * m.RecoveryTopDT16 [n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FDT16_top[ n,  j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT16outflow = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=DT16_top_outflow_rule)
        # -------------------------------
        # Bottom column-3
        # -------------------------------
        def glycerol__outflow_rule(m, n, j, k):
            if n in ['Glycerol','Water'] and j == 'BiodieselProcess' and k=='DT':
                return m.Glycerol_coproduct[n, j, k] == m.FCentrifugal3_Liquid[n, j, 'DT'] - m.FDT16_top [ n, j, 'DT']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.Glycerol_coproduct [n, j, k] == 0 
            else:
                return Constraint.Skip
        m.glycerolcoproduct = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=glycerol__outflow_rule)
        
        # -------------------------------
        # Biodiesel waste stream
        # -------------------------------
        def total_biodiesel_waste_rule(m, n,j):
            if n in ['Water','Lipid','FAME'] and j == 'BiodieselProcess':
                return m.totalwaste_biodiesel [n,j] == m.FDT15_bottom[n,'BiodieselProcess', 'DT'] 
            elif n in m.Components and j in m.NonGlucoseUpgrading :
                return m.totalwaste_biodiesel [n,j]  == 0 
            else:
                return Constraint.Skip
        m.total_biodiesel_waste_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, rule=total_biodiesel_waste_rule)
        
# ======================================================
# Protein Extraction Model
# ====================================================== 
class ProteinExtractionModel:
    """Protein extraction constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach protein extraction constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # NaOH stream
        # --------------------------------        
        def chemical_protein_inflow_rule(m, n, j,k):
            if n in ['NaOH','Water'] and j == 'ProteinExtraction' and k =='Pump':
                return m.ChemicalConsumptionProtein [n, j,k] ==  sum(m.FCentrifugal2_Solid[n, 'BiodieselProcess', 'Centrifugal'] for n in m.Components)* m.ChemicalConsumptionNonFermentation[n,'ProteinExtraction']
            elif n in m.Components and j in  m.NonGlucoseUpgrading and k in m.Equipment:
                return m.ChemicalConsumptionProtein [n, j,k] == 0
            else:
                return Constraint.Skip
        m.chemical_protein_inflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=chemical_protein_inflow_rule)
        
        ## -------------------------------
        # Protein extraction
        # --------------------------------        
        def flow_protein_balance_rule(m, n, j, k):
            if n in ['Water','NaOH','Carbohydrate','Protein'] and j =='ProteinExtraction' and k in ['Extractor','Centrifugal']:
                return m.FProtein[n,j,k]  == m.FCentrifugal2_Solid[n, 'BiodieselProcess', 'Centrifugal'] + m.ChemicalConsumptionProtein [n, 'ProteinExtraction', 'Pump']
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                  return  m.FProtein[n,j,k] == 0   
            else:
                  return Constraint.Skip
        m.flow_protein_balance_rule = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment, rule=flow_protein_balance_rule)
        
        # Centrifugal
        # -------------------------------
        # Centrifugal solid outflow
        # -------------------------------
        def centrifugal4_solid_outflow_rule(m, n, j, k):
            if n == 'Carbohydrate' and j == 'ProteinExtraction'  and k == 'Centrifugal':
                return m.FCentrifugal4_Solid[n, j, k] == m.FProtein[n,j,'Centrifugal'] 
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FCentrifugal4_Solid[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.centrifugal4_solid_outflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=centrifugal4_solid_outflow_rule)
        # -------------------------------
        # Centrifugal liquid outflow
        # -------------------------------
        def centrifugal4_liquid_outflow_rule(m, n, j, k):
            if n in ['Protein','NaOH','Water'] and j == 'ProteinExtraction'  and k in ['Centrifugal','Filtration']:
                return m.FCentrifugal4_Liquid[n, j, k] ==  m.FProtein[n,j,'Centrifugal'] - m.FCentrifugal4_Solid[n, j,'Centrifugal'] 
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FCentrifugal4_Liquid[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.centrifugal4_liquid_outflow_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,  rule=centrifugal4_liquid_outflow_rule)
       
        # Filtration
        # -------------------------------
        # Filtration waste
        # -------------------------------
        def Filtration_waste_outflow_rule(m, n, j, k):
            if n in ['NaOH','Protein'] and j == 'ProteinExtraction' and k == 'Filtration':
                return m.FFiltration_Waste[n, j, k] == m.FCentrifugal4_Liquid[n, j, 'Filtration'] * m.RecoveryFiltration[n]
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.FFiltration_Waste[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.Filtration_waste_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,   rule=Filtration_waste_outflow_rule)
        # -------------------------------
        # Protein product
        # -------------------------------
        def Protein_product_rule(m, n, j, k):
            if n in ['NaOH','Protein'] and j == 'ProteinExtraction' and k == 'Filtration':
                return m.ProteinProduct[n, j, k] == m.FCentrifugal4_Liquid[n, j, 'Filtration']  - m.FFiltration_Waste[n, j, 'Filtration'] 
            elif n in m.Components and j in m.NonGlucoseUpgrading and k in m.Equipment:
                return m.ProteinProduct[n, j, k]== 0 
            else:
                return Constraint.Skip
        m.Protein_product_constraint = Constraint(m.Components, m.NonGlucoseUpgrading, m.Equipment,   rule=Protein_product_rule)

# ======================================================
# Biorefinery Model
# ======================================================
class BiorefineryModel:
    """Unified class that groups Biorefinery models."""

    def __init__(self, model):
        """Attach all process constraints to one existing AbstractModel."""
        self.model = model
        self.Pretreatment = EnzymaticHydrolysisModel(model)
        self.Bioethanol = BioethanolModel(model)  
        self.LacticAcid = LacticAcidModel(model)
        self.SuccinicAcid = SuccinicAcidModel(model)
        self.BDO = BDOModel(model)
        self.Butanol = ButanolModel(model)  
        self.Biodiesel = BiodieselModel(model)
        self.Protein = ProteinExtractionModel(model)
                                         

    def get_models(self):
        """Return all sub-models (for inspection or solving separately)."""
        return {
            'Pretreatment': self.Pretreatment.model,
            'Bioethanol': self.Bioethanol.model,
            'LacticAcid': self.LacticAcid.model,
            'SuccinicAcid': self.SuccinicAcid.model,
            'BDO': self.BDO.model,
            'Butanol': self.Butanol.model,
            'Biodiesel': self.Biodiesel.Model,
            'Protein': self.Protein.Model
        }    
        
        
        
        




     
        

 
