from pyomo.environ import *

# ======================================================
# Utility Consumption Model
# ======================================================
class UtilityConsumptionModel:
    """Utility Consumption constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Utility Consumption constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        model = self.model
        
        ## -------------------------------
        # Electricity consumption 
        # -------------------------------- 
        #1. Grinding
        # -------------------------------- 
        def electricity_consumption_grinding_rule(model, u, j, k):
            if u == 'electricity' and j== 'grinding' and k == 'Crusher':
                return model.Utin_electricity_grinding[u, j, k] == sum(model.Fmill_component[n, j, 'Crusher'] for n in model.Macronutrients) * 1.73E-06 #kWh/tonne
            elif u in model.Utility  and j in model.Milling and k in model.Equipment:
                return model.Utin_electricity_grinding[u, j, k] == 0
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Grinding = Constraint(model.Utility, model.Milling, model.Equipment, rule=electricity_consumption_grinding_rule)
        # -------------------------------- 
        #2. Pretreatment
        # -------------------------------- 
        def electricity_consumption_EnzymaticHydrolysis_rule(model, u, j, k):
            if u == 'electricity' and j== 'enzymatic-hydrolysis' and k == 'Pump':
                return model.Utin_electricity_EnzymaticHydrolysis[u, j, k] == sum(model.Fpump1[n,'enzymatic-hydrolysis', 'Pump'] for n in model.Components) * 2.91E-04
            elif u == 'electricity' and j== 'enzymatic-hydrolysis' and k == 'Centrifugal':
                return model.Utin_electricity_EnzymaticHydrolysis[u, j, k] == sum(model.FinalMass [ n,'enzymatic-hydrolysis', 'Centrifugal']  for n in model.Components) * 2.02E-01
            elif u in model.Utility  and j in model.FWManagementOption and k in model.Equipment:
                return model.Utin_electricity_EnzymaticHydrolysis[u, j, k] == 0
            else:
                return Constraint.Skip
        model.Electricity_Consumption_EnzymaticHydrolysis = Constraint(model.Utility, model.FWManagementOption, model.Equipment,  rule=electricity_consumption_EnzymaticHydrolysis_rule)
        # -------------------------------- 
        #3. Bioethanol process
        # --------------------------------
        def electricity_consumption_Bioethanol_rule(model, u, j, k):
            if u == 'electricity' and j== 'BioethanolProcess' and k == 'Pump':
                return model.Utin_electricity_BioethanolProcess[u, j, k] == (sum(model.FBioethanol1 [ n, 'BioethanolProcess', 'Pump'] for n in model.Components) * 1.43E-04 + 
                                                                            sum(model.Fflashdrum1_liquid [ n, 'BioethanolProcess', 'Pump'] for n in model.Components) * 2.98E-04)  

            elif u in model.Utility  and j in model.Biofuels and k in model.Equipment:
                return  model.Utin_electricity_BioethanolProcess[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Bioethanol = Constraint(model.Utility, model.Biofuels, model.Equipment,    rule=electricity_consumption_Bioethanol_rule)
        ## -------------------------------- 
        #4. Lactic acid process
        # --------------------------------
        def electricity_consumption_Lactic_rule(model, u, j, k):
            if u == 'electricity' and j== 'LacticAcidProcess' and k == 'Pump':
                return model.Utin_electricity_LacticProcess[u, j, k] == (sum(model.FinLacticAcid1_component [n,  'LacticAcidProcess', 'Pump'] for n in model.Components) * 1.43E-04 +
                                                                        sum(model.FinalMassFermenter4[n,  'LacticAcidProcess', 'Pump'] for n in model.Components) * 1.45E-04 +
                                                                        sum(model.FoutDT8_bottom_component[n,  'LacticAcidProcess', 'Pump'] for n in model.Components) * 3.71E-03 + 
                                                                        sum(model.Finpump9_component[n,  'LacticAcidProcess', 'Pump'] for n in model.Components) * 1.46E-04 +
                                                                        sum(model.FoutDT10_bottom_component[n,  'LacticAcidProcess', 'Pump'] for n in model.Components) * 1.43E-04)
            elif  u in model.Utility and j in model.Biochemicals and k in model.Equipment:
                return  model.Utin_electricity_LacticProcess[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Lactic_constraint = Constraint(model.Utility, model.Biochemicals, model.Equipment,  rule=electricity_consumption_Lactic_rule) 
        ## -------------------------------- 
        #5. Succinic acid process
        # --------------------------------
        def electricity_consumption_Succinic_rule(model, u, j, k):
            if u == 'electricity' and j== 'SuccinicAcidProcess' and k =='Pump':
                return model.Utin_electricity_SuccinicProcess[u, j, k] == sum(model.FinSuccinicAcid1_component [n,'SuccinicAcidProcess','Pump'] for n in model.Components) * 5.70E-04
            elif u == 'electricity' and j== 'SuccinicAcidProcess' and k =='Centrifugal':
                return model.Utin_electricity_SuccinicProcess[u, j, k] == sum(model.FoutEvaporator2_bottom_component[n, 'SuccinicAcidProcess','Centrifugal'] for n in model.Components) * 0.384
            elif u in model.Utility  and j in model.Biochemicals and k in model.Equipment:
                return  model.Utin_electricity_SuccinicProcess[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Succinic = Constraint(model.Utility, model.Biochemicals, model.Equipment, rule=electricity_consumption_Succinic_rule)
        ## -------------------------------- 
        #6. BDO process
        # --------------------------------
        def electricity_consumption_BDO_rule(model, u, j, k):
            if u == 'electricity' and j== 'BDOProcess' and k == 'Pump':
                return model.Utin_electricity_BDOProcess[u, j, k] == sum(model.FinBDO_component [n,'BDOProcess', 'Pump'] for n in model.Components) * 1.43E-04
            elif u == 'electricity' and j== 'BDOProcess' and k == 'Comp':
                return model.Utin_electricity_BDOProcess[u, j, k] == sum(model.Fincomp1[n,'BDOProcess', 'Comp'] for n in model.Components) * 0.107
            elif  u in model.Utility and j in model.Biochemicals and k in model.Equipment:
                return  model.Utin_electricity_BDOProcess[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_BDO = Constraint(model.Utility, model.Biochemicals, model.Equipment,  rule=electricity_consumption_BDO_rule)
        ## -------------------------------- 
        #7. Butanol process
        # --------------------------------
        def electricity_consumption_Butanol_rule(model, u, j, k):
            if u == 'electricity' and j== 'ButanolProcess' and k == 'Pump':
                return model.Utin_electricity_ButanolProcess[u, j, k] == sum(model.FinButanol_component [n, j, 'Pump'] for n in model.Components) * 1.43E-04
            elif u in model.Utility  and j in model.Biofuels   and k in model.Equipment:
                return  model.Utin_electricity_ButanolProcess[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Butanol = Constraint(model.Utility, model.Biofuels , model.Equipment,  rule=electricity_consumption_Butanol_rule)      
        ## -------------------------------- 
        #8. Biodiesel process
        # --------------------------------
        def electricity_consumption_Biodiesel_rule(model, u, j, k):
            if u == 'electricity' and j== 'BiodieselProcess' and k == 'Centrifugal':
                return model.Utin_electricity_BiodieselProcess[u, j, k] == (sum(model.FBiodiesel1[n, j, 'Centrifugal'] for n in model.Components) * 0.060 + 
                                                                            sum(model.FinalMassNeutralizer[ n,  j, 'Neutralizer'] for n in model.Components) * 0.0026)
            elif u == 'electricity' and j== 'BiodieselProcess' and k == 'Pump':
                return model.Utin_electricity_BiodieselProcess[u, j, k] == (sum(model.FEvaporator1_liquid [ n,  'BiodieselProcess', 'Pump'] for n in model.Components) * 4.20E-03 +
                                                                            sum(model.ChemicalBiodieselStream [ n,  'BiodieselProcess', 'Pump'] for n in model.Components) * 7.80E-03 + 
                                                                            sum(model.FDT14_bottom [ n, 'BiodieselProcess', 'Pump'] for n in model.Components) * 1.59E-03) 
            elif u in model.Utility  and j in model.NonGlucoseUpgrading and k in model.Equipment:
                return  model.Utin_electricity_BiodieselProcess[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Biodiesel_constraint = Constraint(model.Utility, model.NonGlucoseUpgrading, model.Equipment,  rule=electricity_consumption_Biodiesel_rule)
        ## -------------------------------- 
        #9. Protein extraction
        # --------------------------------
        def electricity_consumption_Protein_rule(model, u, j, k):
            if u == 'electricity' and j== 'ProteinExtraction' and k == 'Pump':
                return model.Utin_electricity_Protein[u, j, k] == sum(model.ChemicalConsumptionProtein [n, j, 'Pump'] for n in model.Components) * 3.6414E-06
            elif u == 'electricity' and j== 'ProteinExtraction' and k == 'Centrifugal':
                return model.Utin_electricity_Protein[u, j, k] == sum(model.FProtein[n,j,'Centrifugal']  for n in model.Components) * 0.0018
            elif  u in model.Utility and j in model.NonGlucoseUpgrading and k in model.Equipment:
                return  model.Utin_electricity_Protein[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Protein_constraint = Constraint(model.Utility, model.NonGlucoseUpgrading , model.Equipment,  rule=electricity_consumption_Protein_rule)
        ## -------------------------------- 
        #13. Composting
        # --------------------------------
        def electricity_consumption_composting_rule(model, u, j):
            if u == 'electricity' and j== 'Composting':
                return model.Utin_electricity_Composting[u, j] == model.Finfeedstock['Composting'] * 93
            elif u in model.Utility  and j in model.FWManagementOption :
                return model.Utin_electricity_Composting[u, j] == 0
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Composting = Constraint(model.Utility, model.FWManagementOption,  rule=electricity_consumption_composting_rule)       
        ## -------------------------------- 
        #14. Animal feed
        # --------------------------------
        def electricity_consumption_AnimalFeed_rule(model,u,j):
            if u == 'electricity' and j== 'AnimalFeed' :
                return model.Utin_electricity_AnimalFeed [u,j] == model.Finfeedstock ['AnimalFeed'] * 0.0246
            elif  u in model.Utility and j in model.FWManagementOption:
                return  model.Utin_electricity_AnimalFeed [u,j] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_AnimalFeed = Constraint(model.Utility, model.FWManagementOption,  rule=electricity_consumption_AnimalFeed_rule)       
        ## -------------------------------- 
        #12. Anaerobic digestion
        # --------------------------------
        def electricity_consumption_Biogas_rule(model, u, j, k):
            if u == 'electricity' and j== 'AnaerobicDigestion' and k == 'Centrifugal':
                return model.Utin_electricity_AD[u, j, k] == sum(model.Fflashdrum5_liquid[n,'AnaerobicDigestion','Centrifugal'] for n in model.Components) * 0.253
            if u == 'electricity' and j== 'AnaerobicDigestion' and k == 'Comp':
                return model.Utin_electricity_AD[u, j, k] == sum(model.Fflashdrum5_gas[n, 'AnaerobicDigestion', 'Comp'] for n in model.Components) * 0.3
            elif  u in model.Utility and j in model.FWManagementOption and k in model.Equipment:
                return  model.Utin_electricity_AD[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Biogas_constraint = Constraint(model.Utility, model.FWManagementOption , model.Equipment,  rule=electricity_consumption_Biogas_rule)                
        ## -------------------------------- 
        #10. Incineration
        # --------------------------------
        def electricity_consumption_Incineration_rule(model, u, j, k):
            if u == 'electricity' and j== 'Incineration' and k == 'Comp':
                return model.Utin_electricity_Incineration[u, j, k] == sum(model.FComp4[n, 'Incineration', 'Comp'] for n in model.Components) * 0.2067
            elif u == 'electricity' and j== 'Incineration' and k == 'Pump':
                return model.Utin_electricity_Incineration[u, j, k] == sum(model.FCooler[n, 'Incineration', 'Pump'] for n in model.Components) * 0.086
            elif  u in model.Utility and j in model.FWManagementOption and k in model.Equipment:
                return  model.Utin_electricity_Incineration[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_Incineration_constraint = Constraint(model.Utility, model.FWManagementOption, model.Equipment,  rule=electricity_consumption_Incineration_rule)        
        ## -------------------------------- 
        #11. CCU
        # --------------------------------
        def electricity_consumption_CCU_rule(model, u, j, k):
            if u == 'electricity' and j== 'CCU' and k == 'Pump':
                return model.Utin_electricity_CCU[u, j, k] == sum(model.FoutAbsorber2_bottom[ n,'CCU', 'Pump'] for n in model.Components) * 3.47E-05
            if u == 'electricity' and j== 'CCU' and k == 'Comp':
                return model.Utin_electricity_CCU[u, j, k] == sum(model.CO2_compression[ n,'CCU', 'Comp'] for n in model.Components) * ( 0.0169 + 0.0188 + 0.0184 + 0.0156 + 0.0110 + 0.0070)
            elif  u in model.Utility and j in model.CarbonCapture and k in model.Equipment:
                return model.Utin_electricity_CCU[u, j, k] == 0 
            else:
                return Constraint.Skip
        model.Electricity_Consumption_CCU_constraint = Constraint(model.Utility, model.CarbonCapture, model.Equipment,  rule=electricity_consumption_CCU_rule)
        ## -------------------------------- 
        #14. Total electricity consumption
        # --------------------------------
        def electricity_total_consumption_rule(model, u):
            if u =='electricity' :
                return model.Utin_electricity_total_consumption [u] ==  sum(model.Utin_electricity_grinding['electricity','grinding', k] + model.Utin_electricity_EnzymaticHydrolysis['electricity', 'enzymatic-hydrolysis', k] +
                                                                            model.Utin_electricity_BioethanolProcess['electricity', 'BioethanolProcess', k] + model.Utin_electricity_LacticProcess['electricity', 'LacticAcidProcess', k] + 
                                                                            model.Utin_electricity_SuccinicProcess['electricity', 'SuccinicAcidProcess', k] + model.Utin_electricity_BDOProcess['electricity','BDOProcess',k] + model.Utin_electricity_ButanolProcess['electricity','ButanolProcess',k] +
                                                                            model.Utin_electricity_BiodieselProcess['electricity','BiodieselProcess',k] + model.Utin_electricity_Protein['electricity', 'ProteinExtraction' , k] + model.Utin_electricity_AD['electricity', 'AnaerobicDigestion', k] + 
                                                                            model.Utin_electricity_Incineration ['electricity','Incineration',k] + model.Utin_electricity_CCU['electricity','CCU',k] for k in model.Equipment) + sum(model.Utin_electricity_Composting [u,'Composting'] + model.Utin_electricity_AnimalFeed [u,'AnimalFeed'] for u in model.Utility)
            elif u in model.Utility:
                return model.Utin_electricity_total_consumption [u] == 0
            else:
                Constraint.Skip
        model.total_electricity_total_consumption = Constraint(model.Utility, rule=electricity_total_consumption_rule)
        
        ## -------------------------------
        # Heating consumption 
        # -------------------------------- 
        #1. Pretreatment
        # --------------------------------
        def heat_consumption_EnzymaticHydrolysis_rule(model, u, j, k):
            if u == 'heat' and j== 'enzymatic-hydrolysis' and k == 'Heater':
                return model.Utin_heat_EnzymaticHydrolysis [u, j, k] == sum(model.FPretreatment_component[ n, j, 'Heater'] for n in model.Components) * 1 #tonne of steam/tonne
            elif u in model.Utility  and j in model.FWManagementOption and k in model.Equipment:
                return model.Utin_heat_EnzymaticHydrolysis [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_EnzymaticHydrolysis = Constraint(model.Utility, model.FWManagementOption, model.Equipment,  rule=heat_consumption_EnzymaticHydrolysis_rule)        
        # -------------------------------- 
        #2. Bioethanol process
        # --------------------------------
        def heat_consumption_bioethanol_rule(model, u, j, k):
            if u == 'heat' and j== 'BioethanolProcess' and k == 'Heater':
                return model.Utin_heat_Bioethanol [u, j, k] ==  (sum(model.Fflashdrum1_liquid [ n, 'BioethanolProcess', 'Heater'] for n in model.Components) * 9.92E-02 +
                                                                sum(model.FDT2_top [ n, 'BioethanolProcess', 'Heater'] for n in model.Components) * 5.17E-01)
            elif u == 'heat' and j== 'BioethanolProcess' and k == 'DT':
                return model.Utin_heat_Bioethanol [u, j, k] == (sum(model.Fflashdrum1_liquid[ n,  'BioethanolProcess', 'DT'] for n in model.Components)  *  2.77E-01 +
                                                                sum(model.FDT1_top [ n,  'BioethanolProcess', 'DT'] for n in model.Components)  * 1.62)
            elif u =='heat' and j=='BioethanolProcess' and k=='FlashDrum':
                return model.Utin_heat_Bioethanol [u,j,k]  == sum(model.FinalMassFermenter1[ n,  'BioethanolProcess', 'FlashDrum'] for n in model.Components) * 4.49E-02
            elif u in model.Utility  and j in model.Biofuels and k in model.Equipment:
                return model.Utin_heat_Bioethanol[u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_bioethanol = Constraint(model.Utility, model.Biofuels, model.Equipment, rule=heat_consumption_bioethanol_rule)  
        # -------------------------------- 
        #3. Lactic acid process
        # --------------------------------
        def heat_consumption_Lactic_rule(model, u, j, k):
            if u == 'heat' and j== 'LacticAcidProcess' and k == 'Heater':
                return model.Utin_heat_Lactic  [u, j, k] == (sum(model.FinalMassFermenter4[ n, 'LacticAcidProcess', 'Heater'] for n in model.Components)  * 0.0923+
                                                            sum(model.FinLacticAcid3_component [ n, 'LacticAcidProcess', 'Heater'] for n in  model.Components)  * 0.1542 +
                                                            sum(model.FinalMassReactor1[ n,'LacticAcidProcess', 'Heater'] for n in  model.Components)  * 0.2481 +
                                                            sum(model.FinalMassReactor2[ n,'LacticAcidProcess', 'Heater'] for n in  model.Components)  * 0.0057)
            elif u == 'heat' and j== 'LacticAcidProcess' and k == 'DT ':
                return model.Utin_heat_Lactic  [u, j, k] == (sum(model.FinalMassFermenter4[ n, 'LacticAcidProcess', 'DT'] for n in  model.Components)  * 0.929 + 
                                                            sum(model.FinalMassReactor1[ n,  'LacticAcidProcess', 'DT'] for n in  model.Components)  * 0.093 + 
                                                            sum(model.FoutDT9_top_component[ n,  'LacticAcidProcess', 'DT'] for n in  model.Components)  * 0.535 +
                                                            sum(model.FinalMassReactor2 [ n,  'LacticAcidProcess', 'DT'] for n in  model.Components)  * 0.267+
                                                            sum(model.FoutDT11_top_component[ n,  'LacticAcidProcess', 'DT'] for n in  model.Components)  * 0.451 +
                                                            sum(model.FoutDT11_bottom_component[ n,  'LacticAcidProcess', 'DT'] for n in  model.Components)  * 0.5032)
            elif u == 'heat' and j== 'LacticAcidProcess' and k == 'Reactor1':
                return model.Utin_heat_Lactic  [u, j, k] == sum(model.FinLacticAcid3_component [ n,  j, 'Reactor1'] for n in  model.Components)  * 0.0402
            elif u in model.Utility and j in model.Biochemicals and k in model.Equipment:
                return model.Utin_heat_Lactic  [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_Lactic = Constraint(model.Utility, model.Biochemicals, model.Equipment, rule=heat_consumption_Lactic_rule)
        # -------------------------------- 
        #4. Succinic acid process
        # --------------------------------
        def heat_consumption_Succinic_rule(model, u, j, k):
            if u == 'heat' and j== 'SuccinicAcidProcess' and k == 'Evaporator':
                return model.Utin_heat_Succinic[u, j, k] == sum(model.FinalMassFermenter5 [n, 'SuccinicAcidProcess', 'Fermenter'] for n in model.Components)  * 0.8848
            elif u in model.Utility and j in model.Biochemicals and k in model.Equipment:
                return model.Utin_heat_Succinic[u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_Succinic = Constraint(model.Utility, model.Biochemicals, model.Equipment, rule=heat_consumption_Succinic_rule)
        # -------------------------------- 
        #5. BDO process
        # --------------------------------
        def heat_consumption_BDO_rule(model, u, j, k):
            if u == 'heat' and j== 'BDOProcess' and k == 'DT':
                return model.Utin_heat_BDO [u, j, k] == sum( model.Foutflashdrum2_liquid_component[n,'BDOProcess', 'DT']  for n in model.Components)  * 1.21
            elif u in model.Utility and j in model.Biochemicals and k in model.Equipment:
                return model.Utin_heat_BDO [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_BDO = Constraint(model.Utility, model.Biochemicals, model.Equipment, rule=heat_consumption_BDO_rule)
        # -------------------------------- 
        #6. Butanol process
        # --------------------------------
        def heat_consumption_Butanol_rule(model, u, j, k):
            if u == 'heat' and j== 'ButanolProcess' and k == 'DT':
                return model.Utin_heat_Butanol [u, j, k] == (sum(model.Foutflashdrum4_liquid_component[n,'ButanolProcess', 'DT']  for n in model.Components)  * 0.209 +
                                                            sum(model.FoutDT4_top_component [n, 'ButanolProcess', 'DT'] for n in  model.Components) * 0.171+
                                                            sum(model.FoutDT5_bottom_component[n, 'ButanolProcess', 'DT'] for n in  model.Components)  * 0.776+
                                                            sum(model.FoutDecant1_top_component[n, 'ButanolProcess', 'DT']  for n in  model.Components)  * 1.193)
            elif u=='heat' and j=='ButanolProcess' and k=='FlashDrum':
                return model.Utin_heat_Butanol [u,j,k] == sum(model.FinalMassFermenter3[ n,  'ButanolProcess', 'FlashDrum'] for n in model.Components) * 0.0327
            elif u in model.Utility  and j in model.Biofuels  and k in model.Equipment:
                return model.Utin_heat_Butanol [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_Butanol = Constraint(model.Utility, model.Biofuels , model.Equipment, rule=heat_consumption_Butanol_rule)
        # -------------------------------- 
        #7. Biodiesel process
        # --------------------------------
        def heat_consumption_Biodiesel_rule(model, u, j, k):
            if u == 'heat' and j== 'BiodieselProcess' and k == 'Evaporator':
                return model.Utin_heat_Biodiesel [u, j, k] == sum(model.FCentrifugal2_Liquid[n, 'BiodieselProcess', 'Evaporator']  for n in model.Components)  * 0.1015
            elif u == 'heat' and j== 'BiodieselProcess' and k == 'Heater':
                return model.Utin_heat_Biodiesel  [u, j, k] == sum(model.ChemicalBiodieselStream [ n,  'BiodieselProcess', 'Heater'] for n in  model.Components)  * 0.0557
            elif u == 'heat' and j== 'BiodieselProcess' and k == 'DT':
                return model.Utin_heat_Biodiesel  [u, j, k] == (sum(model.FinalMassTranesterReactor[n, 'BiodieselProcess', 'DT'] for n in  model.Components)  *0.2370 +
                                                                sum(model.FWasher_top[ n,  j, 'DT'] for n in  model.Components)  * 0.5769 +
                                                                sum( model.FCentrifugal3_Liquid[n, j, 'DT'] for n in  model.Components)  * 0.5932)
            elif u in model.Utility  and j in model.NonGlucoseUpgrading and k in model.Equipment:
                return model.Utin_heat_Biodiesel  [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_Biodiesel = Constraint(model.Utility, model.NonGlucoseUpgrading, model.Equipment, rule=heat_consumption_Biodiesel_rule)
        # -------------------------------- 
        #8. Composting
        # --------------------------------
        def heat_consumption_Composting_rule(model, u, j):
            if u == 'heat' and j== 'Composting':
                return model.Utin_heat_Composting [u, j] == model.Finfeedstock ['Composting'] * 0.03
            elif u in model.Utility  and j in model.FWManagementOption:
                return model.Utin_heat_Composting [u, j] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_Composting = Constraint(model.Utility, model.FWManagementOption,  rule=heat_consumption_Composting_rule)       
        # -------------------------------- 
        #10. Incineration
        # --------------------------------
        def heat_consumption_Incineration_rule(model, u, j, k):
            if u == 'heat' and j== 'Incineration' and k =='Economizer':
                return model.Utin_heat_Incineration [u, j,k ] == sum(model.FCooler [n, 'Incineration', 'Economizer'] for n in model.Components) * 0.151
            elif u in model.Utility  and j in model.FWManagementOption:
                return model.Utin_heat_Incineration [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_Incineration = Constraint(model.Utility, model.FWManagementOption, model.Equipment,  rule=heat_consumption_Incineration_rule)        
        # -------------------------------- 
        #8. Carbon capture
        # --------------------------------
        def heat_consumption_CCU_rule(model, u, j, k):
            if u == 'heat' and j== 'CCU' and k == 'DT':
                return model.Utin_heat_CCU [u, j, k] == sum(model.FoutAbsorber2_bottom[ n,'CCU','DT'] for n in model.Components)  * 0.0867
            elif u in model.Utility and j in model.CarbonCapture and k in model.Equipment:
                return model.Utin_heat_CCU  [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Heating_Consumption_CCU = Constraint(model.Utility, model.CarbonCapture, model.Equipment, rule=heat_consumption_CCU_rule)
        # -------------------------------- 
        #9. Total heating consumption
        # --------------------------------
        def heat_total_consumption_rule(model, u):
            if u=='heat':
                return model.Utin_heat_total_consumption [u] ==  sum(model.Utin_heat_EnzymaticHydrolysis ['heat', 'enzymatic-hydrolysis', k] + model.Utin_heat_Bioethanol ['heat','BioethanolProcess', k] +
                                                                     model.Utin_heat_Lactic['heat','LacticAcidProcess',k] + model.Utin_heat_Succinic['heat', 'SuccinicAcidProcess', k] + model.Utin_heat_BDO['heat','BDOProcess',k] + 
                                                                     model.Utin_heat_Butanol ['heat', 'ButanolProcess', k] + model.Utin_heat_Biodiesel ['heat','BiodieselProcess', k] + 
                                                                     model.Utin_heat_Incineration ['heat', 'Incineration', k] + model.Utin_heat_CCU ['heat', 'CCU', k] for k in model.Equipment) + sum(model.Utin_heat_Composting [u,'Composting'] for u in model.Utility) 
            elif u in model.Utility:
                return model.Utin_heat_total_consumption [u] == 0
            else:
                Constraint.Skip
        model.total_heat_total_consumption = Constraint(model.Utility, rule=heat_total_consumption_rule)
        
        ## -------------------------------
        # Cooling water consumption 
        # -------------------------------- 
        #1. Pretreatment
        # --------------------------------
        def coolingwater_consumption_EnzymaticHydrolysis_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'enzymatic-hydrolysis'  and k == 'Cooler':
                return model.Utin_coolingwater_EnzymaticHydrolysis[u, j, k] == sum(model.FPretreatment_component[n, j, 'Cooler'] for n in model.Components)  * 23.91 #tonne CW/tonne
            elif u == 'cooling-water' and j== 'enzymatic-hydrolysis'  and k == 'Reactor':
                return model.Utin_coolingwater_EnzymaticHydrolysis[u, j, k] == sum(model.FPretreatment_component[n, j, 'Reactor'] for n in model.Components) * 29.55  
            elif u in model.Utility and j in model.FWManagementOption and k in model.Equipment:
                return model.Utin_coolingwater_EnzymaticHydrolysis[u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_EnzymaticHydrolysis = Constraint(model.Utility, model.FWManagementOption , model.Equipment, rule=coolingwater_consumption_EnzymaticHydrolysis_rule)
        # -------------------------------- 
        #2. Bioethanol process
        # --------------------------------
        def coolingwater_consumption_bioethanol_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'BioethanolProcess' and k =='Cooler':
                return model.Utin_coolingwater_Bioethanol  [u, j, k] == (sum(model.FBioethanol1[ n, 'BioethanolProcess', 'Cooler'] for n in model.Components)  * 1.28 +
                                                                          sum(model.BioethanolProduct [ n, 'BioethanolProcess', 'Cooler'] for n in model.Components) * 12.74)
            elif u == 'cooling-water' and j== 'BioethanolProcess' and k =='DT':
                return model.Utin_coolingwater_Bioethanol  [u, j, k] == (sum(model.Fflashdrum1_liquid[ n,  'BioethanolProcess', 'DT']for n in model.Components) * 6.43 +
                                                                          sum(model.FDT1_top[ n,  'BioethanolProcess', 'DT'] for n in model.Components)  * 4.46)
            elif u=='cooling-water' and j=='BioethanolProcess' and k =='Fermenter':
                return model.Utin_coolingwater_Bioethanol [u,j,k] == sum(model.FBioethanol1[n,'BioethanolProcess','Fermenter'] for n in model.Components) * 0.07
            elif u in model.Utility and j in model.Biofuels and k in model.Equipment:
                return model.Utin_coolingwater_Bioethanol [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_bioethanol = Constraint(model.Utility, model.Biofuels, model.Equipment, rule=coolingwater_consumption_bioethanol_rule)
        # -------------------------------- 
        #3. Lactic acid process
        # --------------------------------
        def coolingwater_consumption_Lactic_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'LacticAcidProcess' and k == 'Cooler':
                return model.Utin_coolingwater_Lactic [u, j, k] == (sum(model.FinLacticAcid1_component [ n, 'LacticAcidProcess', 'Cooler'] for n in model.Components)  * 0.4601+
                                                                    sum(model.FinLacticAcid4_component[ n,  'LacticAcidProcess', 'Cooler'] for n in model.Components)  * 0.8266)
            elif u == 'cooling-water' and j== 'LacticAcidProcess' and k == 'DT':
                return model.Utin_coolingwater_Lactic  [u, j, k] == (sum(model.FinalMassFermenter4[ n, 'LacticAcidProcess', 'DT'] for n in model.Components)  * 23.293+
                                                                      sum(model.FinalMassReactor1[ n, 'LacticAcidProcess', 'DT'] for n in  model.Components)  * 10.412+
                                                                      sum(model.FoutDT9_top_component[ n, 'LacticAcidProcess', 'DT'] for n in model.Components)  * 13.471+
                                                                      sum(model.FinalMassReactor2[ n,'LacticAcidProcess', 'DT'] for n in  model.Components)  * 11.310+
                                                                      sum(model.FoutDT11_top_component[ n,'LacticAcidProcess', 'DT'] for n in model.Components)  * 11.297+
                                                                      sum(model.FoutDT11_bottom_component[ n,'LacticAcidProcess', 'DT'] for n in  model.Components)  * 5.743)
            elif u == 'cooling-water' and j== 'LacticAcidProcess' and k == 'Reactor1':
                return model.Utin_coolingwater_Lactic  [u, j, k] == sum(model.FinLacticAcid3_component[ n,'LacticAcidProcess', 'Reactor1'] for n in  model.Components)  * 2.43
            elif u=='cooling-water' and j=='LacticAcidProcess' and k =='Fermenter':
                return model.Utin_coolingwater_Lactic [u,j,k] == sum(model.FinLacticAcid1_component [ n,'LacticAcidProcess', 'Fermenter'] for n in model.Components) * 0.91
            elif u in model.Utility and j in model.Biochemicals and k in model.Equipment:
                return model.Utin_coolingwater_Lactic [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_Lactic = Constraint(model.Utility, model.Biochemicals, model.Equipment, rule=coolingwater_consumption_Lactic_rule)
        # -------------------------------- 
        #4. Succinic acid process
        # --------------------------------
        def coolingwater_consumption_Succinic_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'SuccinicAcidProcess' and k =='Cooler':
                return model.Utin_coolingwater_Succinic[u, j, k] == sum(model.FinSuccinicAcid1_component[ n,'SuccinicAcidProcess','Cooler'] for n in model.Components)* 1.06               
            elif u=='cooling-water' and j=='SuccinicAcidProcess' and k =='Fermenter':
                return model.Utin_coolingwater_Succinic[u,j,k] == sum(model.FinSuccinicAcid1_component [n, 'SuccinicAcidProcess', 'Fermenter'] for n in model.Components) * 2.25
            elif u in model.Utility and j in model.Biochemicals  and k in model.Equipment:
                return model.Utin_coolingwater_Succinic[u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_Succinic = Constraint(model.Utility, model.Biochemicals, model.Equipment, rule=coolingwater_consumption_Succinic_rule)
        # -------------------------------- 
        #5. BDO process
        # --------------------------------
        def coolingwater_consumption_BDO_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'BDOProcess' and k == 'Cooler':
                return model.Utin_coolingwater_BDO  [u, j, k] == sum(model.FinBDO_component [ n, 'BDOProcess', 'Cooler']  for n in model.Components)  * 1.28
            elif u == 'cooling-water' and j== 'BDOProcess' and k == 'DT':
                return model.Utin_coolingwater_BDO  [u, j, k] == sum( model.Foutflashdrum2_liquid_component[n,'BDOProcess', 'DT'] for n in model.Components)  * 23.14
            elif u=='cooling-water' and j=='BDOProcess' and k=='Fermenter':
                return model.Utin_coolingwater_BDO [u,j,k] == sum(model.FinBDO_component[n,'BDOProcess','Fermenter'] for n in model.Components) * 3.89
            elif u in model.Utility and j in model.Biochemicals and k in model.Equipment:
                return model.Utin_coolingwater_BDO [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_BDO = Constraint(model.Utility, model.Biochemicals, model.Equipment, rule=coolingwater_consumption_BDO_rule)
        # -------------------------------- 
        #5. Butanol process
        # --------------------------------
        def coolingwater_consumption_Butanol_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'ButanolProcess' and k == 'Cooler':
                return model.Utin_coolingwater_Butanol [u, j, k] == (sum(model.FinButanol_component [ n,  j, 'Cooler'] for n in model.Components)  * 1.28 +
                                                                    sum(model.Foutflashdrum4_gas_component[ n,  j, 'Cooler'] for n in model.Components)  * 1.74)
            elif u == 'cooling-water' and j== 'ButanolProcess' and k == 'DT':
                  return model.Utin_coolingwater_Butanol [u, j, k] == (sum(model.Foutflashdrum4_liquid_component[n,'ButanolProcess', 'DT']for n in model.Components)  * 2.33 +
                                                                      sum(model.FoutDT4_top_component [n, 'ButanolProcess', 'DT'] for n in  model.Components)  * 4.11 +
                                                                      sum(model.FoutDT5_bottom_component[n, 'ButanolProcess', 'DT'] for n in  model.Components)  * 19.67 +
                                                                      sum(model.FoutDecant1_top_component[n, 'ButanolProcess', 'DT'] for n in  model.Components)  * 28.43)
            elif u=='cooling-water' and j == 'ButanolProcess' and k=='Fermenter':
                return model.Utin_coolingwater_Butanol [u,j,k] == sum(model.FinButanol_component [ n,  j, 'Fermenter'] for n in model.Components) * 0.97
            elif u in model.Utility and j in model.Biofuels  and k in model.Equipment:
                return model.Utin_coolingwater_Butanol [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_Butanol = Constraint(model.Utility, model.Biofuels , model.Equipment, rule=coolingwater_consumption_Butanol_rule)
        # -------------------------------- 
        #5. Biodiesel process
        # --------------------------------
        def coolingwater_consumption_Biodiesel_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'BiodieselProcess' and k == 'DT':
                return model.Utin_coolingwater_Biodiesel [u, j, k] == (sum(model.FinalMassTranesterReactor[n, 'BiodieselProcess', 'DT']  for n in model.Components)  * 1.4738 +
                                                                      sum(model.FWasher_top [ n,  j, 'DT'] for n in  model.Components)  * 7.4973+
                                                                      sum( model.FCentrifugal3_Liquid[n, j, 'DT'] for n in  model.Components)  * 5.1595)
            elif u == 'cooling-water' and j== 'BiodieselProcess' and k == 'Cooler':
                return model.Utin_coolingwater_Biodiesel  [u, j, k] == sum(model.FDT14_bottom[ n,  'BiodieselProcess', 'Cooler'] for n in model.Components)  *  3.61
            elif u in model.Utility and j in model.NonGlucoseUpgrading and k in model.Equipment:
                return model.Utin_coolingwater_Biodiesel [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_Biodiesel = Constraint(model.Utility, model.NonGlucoseUpgrading, model.Equipment, rule=coolingwater_consumption_Biodiesel_rule)
        # -------------------------------- 
        #7. Incineration
        # --------------------------------
        def coolingwater_consumption_Incineration_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'Incineration'  and k == 'Cooler':
                return model.Utin_coolingwater_Incineration[u, j, k] == sum(model.FCooler [n, 'Incineration', 'Economizer'] for n in model.Components) * 29.30
            elif u in model.Utility and j in model.FWManagementOption and k in model.Equipment:
                return model.Utin_coolingwater_Incineration[u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_Incineration = Constraint(model.Utility, model.FWManagementOption , model.Equipment, rule=coolingwater_consumption_Incineration_rule)                
        # -------------------------------- 
        #6. Carbon capture
        # --------------------------------
        def coolingwater_consumption_CCU_rule(model, u, j, k):
            if u == 'cooling-water' and j== 'CCU' and k == 'Cooler':
                return model.Utin_coolingwater_CCU [u, j, k] == (sum(model.FCCU1 [ n, 'CCU', 'Cooler'] for n in model.Components)  * 18.2560 + 
                                                                sum(model.FoutDT18_liquid[ n, 'CCU', 'Cooler'] for n in  model.Components)  * 10.6999+
                                                                sum(model.CO2_compression[n,'CCU','Cooler']for n in model.Components)*(2.1854 + 3.4690 + 3.7169 + 3.9714 + 5.7728 + 6.2050))
            elif u == 'cooling-water' and j== 'CCU' and k == 'DT':
                return model.Utin_coolingwater_CCU  [u, j, k] == sum(model.FoutAbsorber2_bottom[ n,'CCU', 'DT'] for n in model.Components)  * 4.4023
            elif u in model.Utility and j in model.CarbonCapture and k in model.Equipment:
                return model.Utin_coolingwater_CCU [u, j, k] == 0
            else:
                return Constraint.Skip
        model.Coolingwater_Consumption_CCU = Constraint(model.Utility, model.CarbonCapture, model.Equipment, rule=coolingwater_consumption_CCU_rule)       
        # -------------------------------- 
        #10. Total cooling water consumption
        # --------------------------------
        def coolingwater_total_consumption_rule(model, u):
            if u == 'cooling-water':
                return model.Utin_coolingwater_total_consumption [u] ==  sum(model.Utin_coolingwater_EnzymaticHydrolysis['cooling-water','enzymatic-hydrolysis', k] + model.Utin_coolingwater_Bioethanol [ 'cooling-water','BioethanolProcess', k] +
                                                                             model.Utin_coolingwater_Lactic['cooling-water', 'LacticAcidProcess', k] + model.Utin_coolingwater_Succinic['cooling-water','SuccinicAcidProcess',k] + model.Utin_coolingwater_BDO ['cooling-water','BDOProcess',k] + 
                                                                             model.Utin_coolingwater_Butanol ['cooling-water','ButanolProcess', k] + model.Utin_coolingwater_Biodiesel  ['cooling-water','BiodieselProcess',k] + model.Utin_coolingwater_Incineration['cooling-water','Incineration',k] + 
                                                                             model.Utin_coolingwater_CCU['cooling-water','CCU',k] for k in model.Equipment) 
            elif u in model.Utility:
                return model.Utin_coolingwater_total_consumption [u] == 0 
            else:
                Constraint.Skip
        model.total_coolingwater_total_consumption = Constraint(model.Utility, rule=coolingwater_total_consumption_rule)
        
        # -------------------------------- 
        #1. Chilling consumption
        # --------------------------------
        def chilling_consumption_Succinic_rule(model,u):
            if u == 'chilling' :
                return model.Utin_chilling_Succinic[u] == sum(model.FoutEvaporator2_bottom_component[n, 'SuccinicAcidProcess','Cooler'] for n in model.Components)  * 0.22               
            elif u in model.Utility :
                return model.Utin_chilling_Succinic[u] == 0
            else:
                return Constraint.Skip
        model.Chilling_Consumption_Succinic = Constraint(model.Utility, rule=chilling_consumption_Succinic_rule)
        
# ======================================================
# Chemical Consumption Model
# ======================================================
class ChemicalConsumptionModel:
    """Chemical Consumption constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Chemical Consumption constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        model = self.model
        
        # --------------------------------
        # 1. Feedstock consumption
        # --------------------------------
        def FW_consumption_rule(model):
            return model.FWConsumption == sum(model.Fmill_component[n, 'grinding', 'Crusher'] for n in model.Macronutrients)
        model.FWConsumptionConstraint = Constraint(rule=FW_consumption_rule)        
        # --------------------------------
        # 2. Chemical consumption of pretreatment
        # --------------------------------
        def chemical_pretreatment_consumption_rule(model,c,j,k):
            if c =='Water' and j =='enzymatic-hydrolysis' and k == 'Pump':
                return model.Chemical_pretreatment_consumption [c,j,k] == model.Fpump1['Water', 'enzymatic-hydrolysis', 'Pump'] 
            elif c =='enzymes' and j =='enzymatic-hydrolysis' and k == 'Reactor':
                return model.Chemical_pretreatment_consumption [c,j,k] ==sum(model.FPretreatment_component[n, 'enzymatic-hydrolysis', 'Reactor'] for n in model.Components)  * model.ChemicalPretreatmentConsumption['enzymes','enzymatic-hydrolysis','Reactor']
            elif c in model.Chemicals and j in model.FWManagementOption and k in model.Equipment:
                return model.Chemical_pretreatment_consumption [c,j,k] == 0 
            else:
                Constraint.Skip
        model.chemical_pretreatment_consumption_constraint = Constraint(model.Chemicals,model.FWManagementOption ,model.Equipment,rule= chemical_pretreatment_consumption_rule)
        # --------------------------------
        # 3. Chemical consumption of bioethanol process
        # --------------------------------
        def total_chemical_bioethanol_consumption_rule(model, c, j, k):
            if c in ['Yeast', 'Peptone', 'AmmoniumSulphate', 'MagnesiumSulphate', 'PotassiumPhosphate'] and j == 'BioethanolProcess' and k == 'Fermenter':
                return model.Total_Chemical_Bioethanol_Consumption[c, j, k] == sum(model.BioethanolProduct[n,'BioethanolProcess' , 'Cooler'] for n in model.Components) * model.ChemicalBiofuelConsumption [c, 'BioethanolProcess', 'Fermenter'] 
            elif c in model.Chemicals and j in model.Biofuels and k in model.Equipment:
                return model.Total_Chemical_Bioethanol_Consumption[c, j, k] == 0
            else:
                return Constraint.Skip
        model.total_chemical_Bioethanol_consumption_constraint = Constraint(model.Chemicals, model.Biofuels, model.Equipment, rule=total_chemical_bioethanol_consumption_rule)
        # --------------------------------
        # 4. Chemical consumption of lactic acid process
        # --------------------------------
        def total_chemical_Lactic_consumption_rule(model, c, j, k):
            if c in ['Yeast','PotassiumPhosphate','AmmoniumSulphate','CalciumChloride','MagnesiumChloride','SodiumPhosphate'] and j == 'LacticAcidProcess' and k == 'Fermenter':
                return model.Total_Chemical_Lactic_Consumption[c, j, k] == sum(model.LacticAcidProduct[ n, 'LacticAcidProcess','DT'] for n in model.Components) * model.ChemicalBiochemicalConsumption[c,'LacticAcidProcess','Fermenter']
            elif c in model.Chemicals and j in model.Biochemicals and k in model.Equipment:
                return model.Total_Chemical_Lactic_Consumption[c, j, k] == 0
            else:
                return Constraint.Skip
        model.total_chemical_Lactic_consumption_constraint = Constraint(model.Chemicals, model.Biochemicals, model.Equipment, rule=total_chemical_Lactic_consumption_rule)
        # --------------------------------
        # 5. Chemical consumption of succinic acid process
        # --------------------------------
        def total_chemical_Succinic_consumption_rule(model, c, j, k):
            if c in ['HydrocloricAcid','MagnesiumCarbonate','SodiumHydroxide','NatriumChloride'] and j == 'SuccinicAcidProcess' and k == 'Fermenter':
                return model.Total_Chemical_Succinic_Consumption[c, j, k] == sum(model.SuccinicAcidProduct[n, 'SuccinicAcidProcess', 'Centrifugal'] for n in model.Components) *  model.ChemicalBiochemicalConsumption[c,'SuccinicAcidProcess','Fermenter']
            elif c in model.Chemicals and j in model.Biochemicals and k in model.Equipment:
                return model.Total_Chemical_Succinic_Consumption[c, j, k] == 0
            else:
                return Constraint.Skip
        model.total_chemical_Succinic_consumption_constraint = Constraint(model.Chemicals, model.Biochemicals, model.Equipment, rule=total_chemical_Succinic_consumption_rule)
        # --------------------------------
        # 6. Chemical consumption BDO process
        # --------------------------------
        def total_chemical_BDO_consumption_rule(model, c, j, k):
            if c in ['Yeast','Glucose','Peptone','PotassiumPhosphate','AceticAcid','MagnesiumSulphate ManganeseSulphate'] and j == 'BDOProcess' and k == 'Fermenter':
                return model.Total_Chemical_BDO_Consumption[c, j, k] == sum(model.BDO_product[n,'BDOProcess', 'DT'] for n in model.Components) * model.ChemicalBiochemicalConsumption [c,'BDOProcess', 'Fermenter'] 
            elif c in model.Chemicals and j in model.Biochemicals and k in model.Equipment:
                return model.Total_Chemical_BDO_Consumption[c, j, k] == 0
            else:
                return Constraint.Skip
        model.total_chemical_BDO_consumption_constraint = Constraint(model.Chemicals, model.Biochemicals, model.Equipment, rule=total_chemical_BDO_consumption_rule)
        # --------------------------------
        # 7. Chemical consumption of Butanol process
        # --------------------------------
        def total_chemical_Butanol_consumption_rule(model, c, j, k):
            if c in ['Yeast','PotassiumPhosphate','AmmoniumSulphate','SodiumChloride','MagnesiumSulphate',' ManganeseSulphate',' IronSulphate'] and j == 'ButanolProcess' and k == 'Fermenter':
                return model.Total_Chemical_Butanol_Consumption[c, j, k] == sum(model.Butanol_product[n,'ButanolProcess', 'DT'] for n in model.Components) * model.ChemicalBiofuelConsumption [c,'ButanolProcess','Fermenter'] 
            elif c in model.Chemicals and j in model.Biofuels  and k in model.Equipment:
                return model.Total_Chemical_Butanol_Consumption[c, j, k] == 0
            else:
                return Constraint.Skip
        model.total_chemical_Butanol_consumption_constraint = Constraint(model.Chemicals, model.Biofuels, model.Equipment, rule=total_chemical_Butanol_consumption_rule)        
        # --------------------------------
        # 8. Chemical consumption of Biodiesel process
        # --------------------------------
        def total_chemical_Biodiesel_Consumption_rule(model, n, j):
            if n == 'Methanol' and j == 'BiodieselProcess' :
                return model.Chemical_Biodiesel_Consumption[n, j] == model.ChemicalBiodieselStream['Methanol','BiodieselProcess','Pump'] 
            elif n == 'NaOH' and j == 'BiodieselProcess' :
                return model.Chemical_Biodiesel_Consumption[n, j] == model.ChemicalBiodieselStream['NaOH','BiodieselProcess','Pump'] 
            elif n == 'H3PO4' and j == 'BiodieselProcess' :
                return model.Chemical_Biodiesel_Consumption[n, j] == model.H3PO4Stream ['H3PO4','BiodieselProcess','Neutralizer'] 
            elif n in model.Components and j in model.NonGlucoseUpgrading:
                return model.Chemical_Biodiesel_Consumption[n, j] == 0
            else:
                return Constraint.Skip
        model.total_chemical_Biodiesel_Consumption_constraint = Constraint(model.Components, model.NonGlucoseUpgrading, rule=total_chemical_Biodiesel_Consumption_rule)
        # --------------------------------
        # 9. Chemical consumption of Protein
        # --------------------------------
        def total_chemical_Protein_Consumption_rule(model, n, j):
            if n == 'NaOH' and j == 'ProteinExtraction':
                return model.Chemical_Protein_Consumption[n, j] == model.ChemicalConsumptionProtein ['NaOH', 'ProteinExtraction','Pump']
            elif n == 'Water' and j == 'ProteinExtraction':
                return model.Chemical_Protein_Consumption[n, j] == model.ChemicalConsumptionProtein ['Water', 'ProteinExtraction','Pump'] 
            elif n in model.Components and j in model.NonGlucoseUpgrading:
                return model.Chemical_Protein_Consumption[n, j] == 0
            else:
                return Constraint.Skip
        model.total_chemical_Protein_Consumption_constraint = Constraint(model.Components, model.NonGlucoseUpgrading, rule=total_chemical_Protein_Consumption_rule)
        # --------------------------------
        # 10. Chemical consumption of Composting
        # --------------------------------
        def total_chemical_Composting_Consumption_rule(model, n, j):
            if n in ['H2SO4','NaOH'] and j == 'Composting':
                return model.Chemical_composting_Consumption [n, j] == model.Finfeedstock['Composting'] * model.ChemicalConsumptionComposting[n,'Composting'] 
            elif n in model.Components and j in model.FWManagementOption:
                return model.Chemical_composting_Consumption [n, j] == 0
            else:
                return Constraint.Skip
        model.total_chemical_Composting_Consumption_constraint = Constraint(model.Components, model.FWManagementOption, rule=total_chemical_Composting_Consumption_rule)        
        # --------------------------------
        # 11. Chemical consumption of AnimalFeed
        # --------------------------------
        def total_chemical_AnimalFeed_consumption_rule(model, n, j):
            if n == 'Water' and j == 'AnimalFeed':
                return model.Chemical_AnimalFeed_Consumption[n, j] == model.Finfeedstock ['AnimalFeed'] * model.ChemicalConsumptionAnimalFeed['Water','AnimalFeed'] 
            elif n in model.Components and j in model.FWManagementOption :
                return model.Chemical_AnimalFeed_Consumption[n, j] == 0
            else:
                return Constraint.Skip
        model.total_chemical_AnimalFeed_consumption_constraint = Constraint(model.Components, model.FWManagementOption, rule=total_chemical_AnimalFeed_consumption_rule)
        
# ======================================================
# Utility Chemical Consumption Model
# ======================================================
class UtilityChemicalConsumptionModel:
    """Unified class that groups Utility Chemical Consumption models."""

    def __init__(self, model):
        """Attach all process constraints to one existing AbstractModel."""
        self.model = model
        self.Utility = UtilityConsumptionModel(model)
        self.Chemical = ChemicalConsumptionModel(model)

    def get_models(self):
        """Return all sub-models (for inspection or solving separately)."""
        return {
            'Utility': self.Utility.model,
            'Chemical': self.Chemical.model
        }        
       