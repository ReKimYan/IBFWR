from pyomo.environ import *

# ======================================================
# Operating Cost Model
# ======================================================
class OperatingCostModel:
    """OperatingCost constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Operating Cost constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        model = self.model
        
        # -------------------------------- 
        # Total utility cost 
        # --------------------------------
        def total_utility_cost_rule(model):
            return model.total_utility_cost == (model.Utin_electricity_total_consumption ['electricity'] * model.Utility_price['electricity'] +  model.Utin_heat_total_consumption ['heat'] * model.Utility_price['heat'] + 
                                                model.Utin_coolingwater_total_consumption ['cooling-water']*model.Utility_price['cooling-water'] + model.Utin_chilling_Succinic['chilling'] *model.Utility_price['chilling']) * 300
        model.total_utility_cost_constraint = Constraint(rule=total_utility_cost_rule)

        # -------------------------------- 
        # Chemical cost 
        # --------------------------------
        # 1. Feedstock cost 
        # --------------------------------
        def FW_cost_rule(model):
            return model.FW_cost == sum(model.FWsupply[f] * model.FWPrice [f] for f in model.FoodWasteCategory)
        model.FW_cost_constraints = Constraint(rule=FW_cost_rule)
        # --------------------------------
        # 2. Chemical cost of pretreatment
        # --------------------------------
        def chemical_cost_pretreatment_rule(model):
            return model.Chemical_cost_pretreatment == sum(model.Chemical_pretreatment_consumption [c,'enzymatic-hydrolysis',k] * model.raw_material_price[c] for c in model.raw_material_price for k in model.Equipment)
        model.Chemical_cost_pretreatment_constraint = Constraint(rule=chemical_cost_pretreatment_rule)
        # --------------------------------
        # 3. Chemical cost of bioethanol process
        # --------------------------------
        def chemical_cost_bioethanol_rule(model):
            return model.Chemical_cost_Bioethanol == sum(model.Total_Chemical_Bioethanol_Consumption[c, 'BioethanolProcess', 'Fermenter'] * model.chemical_fermentation_Price[c] for c in model.Chemicals)
        model.Chemical_cost_bioethanol_constraint = Constraint(rule=chemical_cost_bioethanol_rule)
        # --------------------------------
        # 4. Chemical cost of lactic acid process
        # -------------------------------- 
        def chemical_cost_lactic_rule(model):
            return model.Chemical_cost_Lactic == sum(model.Total_Chemical_Lactic_Consumption[c, 'LacticAcidProcess', 'Fermenter'] * model.chemical_fermentation_Price[c] for c in model.Chemicals)
        model.Chemical_cost_lactic_constraint = Constraint(rule=chemical_cost_lactic_rule)
        # --------------------------------
        # 5. Chemical cost of succinic acid process
        # -------------------------------- 
        def chemical_cost_succinic_rule(model):
            return model.Chemical_cost_Succinic == sum(model.Total_Chemical_Succinic_Consumption[c, 'SuccinicAcidProcess', 'Centrifugal'] * model.chemical_fermentation_Price[c] for c in model.Chemicals)
        model.Chemical_cost_succinic_constraint = Constraint(rule=chemical_cost_succinic_rule)
        # --------------------------------
        # 6. Chemical cost of BDO process
        # -------------------------------- 
        def chemical_cost_BDO_rule(model):
            return model.Chemical_cost_BDO== sum(model.Total_Chemical_BDO_Consumption[c, 'BDOProcess', 'Fermenter'] * model.chemical_fermentation_Price[c] for c in model.Chemicals)
        model.Chemical_cost_BDO_constraint = Constraint(rule=chemical_cost_BDO_rule)
        # --------------------------------
        # 7. Chemical cost of Butanol process
        # -------------------------------- 
        def chemical_cost_butanol_rule(model):
            return model.Chemical_cost_Butanol == sum(model.Total_Chemical_Butanol_Consumption[c, 'ButanolProcess', 'Fermenter'] * model.chemical_fermentation_Price[c] for c in model.Chemicals)
        model.Chemical_cost_butanol_constraint = Constraint(rule=chemical_cost_butanol_rule)
        # --------------------------------
        # 8. Chemical cost of Biodiesel process
        # -------------------------------- 
        def chemical_cost_biodiesel_rule(model):
            return model.Chemical_cost_Biodiesel == sum(model.Chemical_Biodiesel_Consumption[n,'BiodieselProcess'] * model.chemical_nonfermentation_Price[n] for n in model.chemical_nonfermentation_Price)
        model.Chemical_cost_biodiesel_constraint = Constraint(rule=chemical_cost_biodiesel_rule)
        # --------------------------------
        # 9. Chemical cost of Protein
        # -------------------------------- 
        def chemical_cost_protein_rule(model):
            return model.Chemical_cost_Protein == model.Chemical_Protein_Consumption['NaOH','ProteinExtraction'] * model.chemical_nonfermentation_Price['NaOH'] 
        model.Chemical_cost_protein_constraint = Constraint(rule=chemical_cost_protein_rule)
        # --------------------------------
        # 10. Chemical cost of Composting
        # --------------------------------
        def chemical_cost_composting_rule(model):
            return model.Chemical_cost_Composting == sum(model.Chemical_composting_Consumption[n,'Composting'] * model.chemical_composting_Price[n] for n in model.chemical_composting_Price)
        model.Chemical_cost_composting_constraint = Constraint(rule=chemical_cost_composting_rule)
        # --------------------------------
        # 10. Chemical cost of AnimalFeed cost
        # --------------------------------
        def chemical_cost_animalfeed_rule(model):
            return model.Chemical_cost_AnimalFeed == model.Chemical_AnimalFeed_Consumption['Water','AnimalFeed'] * model.chemical_AnimalFeed_Price['Water'] 
        model.Chemical_cost_animalfeed_constraint = Constraint(rule=chemical_cost_animalfeed_rule)
        # --------------------------------
        # 11. Total feedstock and chemical cost
        # --------------------------------
        def total_raw_material_cost_rule(model):
            return model.total_raw_material_cost == (model.FW_cost + model.Chemical_cost_pretreatment + model.Chemical_cost_Bioethanol + model.Chemical_cost_Lactic + model.Chemical_cost_Succinic + model.Chemical_cost_BDO + 
                                                     model.Chemical_cost_Butanol + model.Chemical_cost_Biodiesel + model.Chemical_cost_Protein + model.Chemical_cost_Composting + model.Chemical_cost_AnimalFeed) * 300
        model.total_raw_material_cost_constraint = Constraint(rule=total_raw_material_cost_rule)
        
        #-------------------------------- 
        #Collection, sorting and screening, and other cost 
        #--------------------------------
        def Collection_cost_rule(model):
             return model.total_collection_cost == sum(model.Fmill_component[n, 'grinding', 'Crusher'] for n in model.Macronutrients) * 200 * 300#$/tonne
        model.total_collection_cost_constraint = Constraint(rule=Collection_cost_rule)
        
        #def Sorting_cost_rule(model):
            #return model.total_sorting_cost == sum(model.Fmill_component[n, 'grinding', 'Crusher'] for n in model.Macronutrients) * 41 *300#$/tonne
        #model.total_sorting_cost_constraint = Constraint(rule=Sorting_cost_rule)
        
        #def Other_cost_rule(model):
           # return model.total_other_cost == sum(model.Fmill_component[n, 'grinding', 'Crusher'] for n in model.Macronutrients) * 41 *300 #$/tonne
       # model.total_other_cost_constraint = Constraint(rule=Other_cost_rule)
        
        # --------------------------------
        # Direct manufacturing cost
        # --------------------------------
        # 1. Operating labor 
        def operating_labor_rule(model):
            return model.operating_labor == 0.15*model.fixed_capital_investment
        model.operating_labor_constraint = Constraint(rule=operating_labor_rule)
        #2. Cost of manufacturing 
        def cost_of_manufacturing_rule(model):
            return model.cost_of_manufacturing == (0.28 * model.fixed_capital_investment + 2.73 * model.operating_labor + 1.23 * (model.total_utility_cost + model.total_raw_material_cost))
        model.cost_of_manufacturing_constraint = Constraint(rule=cost_of_manufacturing_rule)
        #3. Cost of supervisory and clerical labor 
        def supervisory_clerical_labor_rule(model):
            return model.supervisory_clerical_labor == 0.28*model.operating_labor
        model.supervisory_clerical_labor_constraint = Constraint(rule=supervisory_clerical_labor_rule)
        #3. Cost of maintenance and repair 
        def maintenance_repair_rule(model):
            return model.maintenance_repair == 0.06*model.fixed_capital_investment
        model.maintenance_repair_constraint = Constraint(rule=maintenance_repair_rule)
        #4. Operating supplies 
        def operating_supplies_rule(model):
            return model.operating_supplies == 0.009*model.fixed_capital_investment
        model.operating_supplies_constraint = Constraint(rule=operating_supplies_rule)
        #5. Laboratory charges 
        def laboratory_charges_rule(model):
            return model.laboratory_charges == 0.15*model.operating_labor
        model.laboratory_charges_constraint = Constraint(rule=laboratory_charges_rule)
        #6. Patents and royalties 
        def patents_royalties_rule(model):
            return model.patents_royalties == 0.03*model.cost_of_manufacturing
        model.patents_royalties_constraint = Constraint(rule=patents_royalties_rule)
        #10. Total direct manufacturing cost
        def direct_manufacturing_cost_rule(model):
            return model.direct_manufacturing_cost ==  model.total_raw_material_cost +  model.total_utility_cost + model.operating_labor + model.supervisory_clerical_labor + model.maintenance_repair + model.operating_supplies + model.laboratory_charges + model.patents_royalties
        model.direct_manufacturing_cost_constraint = Constraint(rule=direct_manufacturing_cost_rule)
        # --------------------------------
        # Fixed manufacturing cost 
        # --------------------------------  
        #1. Local taxes and insurance
        def local_taxes_insurance_rule(model):
            return model.local_taxes_insurance == 0.03 * model.fixed_capital_investment
        model.local_taxes_insurance_constraint = Constraint(rule=local_taxes_insurance_rule)
        #2. Plant overhead 
        def plant_overhead_rule(model):
            return model.plant_overhead ==0.708*model.operating_labor + 0.036*model.fixed_capital_investment
        model.plant_overhead_constraint = Constraint(rule=plant_overhead_rule)
        #3. Total fixed manufacturing cost 
        def fixed_manufacturing_cost_rule(model):
            return model.fixed_manufacturing_cost == model.local_taxes_insurance + model.plant_overhead
        model.fixed_manufacturing_cost_constraint = Constraint(rule=fixed_manufacturing_cost_rule)
        # --------------------------------
        # General manufacturing cost 
        # -------------------------------- 
        #1. Administration costs 
        def administration_cost_rule(model):
            return model.administration_cost == 0.177*model.operating_labor + 0.009*model.fixed_capital_investment
        model.administration_cost_constraint = Constraint(rule=administration_cost_rule)
        #2. Distribution and selling costs 
        def distribution_selling_cost_rule(model):
            return model.distribution_selling_cost == 0.11*model.cost_of_manufacturing
        model.distribution_selling_cost_constraint = Constraint(rule=distribution_selling_cost_rule)
        #3. Distribution and selling costs 
        def research_development_cost_rule(model):
            return model.research_development_cost == 0.05*model.cost_of_manufacturing
        model.research_development_cost_constraint = Constraint(rule=research_development_cost_rule)
        #4. Total general manufacturing cost  
        def general_manufacturing_cost_rule(model):
            return model.general_manufacturing_cost == model.administration_cost + model.distribution_selling_cost + model.research_development_cost
        model.general_manufacturing_cost_constraint = Constraint(rule=general_manufacturing_cost_rule)
        
        # --------------------------------
        #Total operating cost 
        # -------------------------------- 
        def total_operating_cost_rule(model,year):
            return model.total_operating_cost   ==  model.direct_manufacturing_cost + model.fixed_manufacturing_cost + model.general_manufacturing_cost
        model.total_operating_cost_constraint = Constraint( rule=total_operating_cost_rule)

# ======================================================
# Capital Investment Model
# ======================================================
class CapitalInvestmentModel:
    """Capital Investment constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Capital investment constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        model = self.model

        ## -------------------------------
        # Equipment cost of Grinding 
        # -------------------------------- 
        def crusher_equipment_cost_rule(model,  j, k):
            if j == 'grinding' and k == 'Crusher':
                return model.crusher_equipment_cost[j, k] == model.Base_equipment_cost['Crusher'] * ((sum(model.Fmill_component[n, 'grinding', 'Crusher'] for n in model.Macronutrients)) / (model.Base_reference_mass['Crusher']))** model.sizing_factor['Crusher']    
            elif j in model.Milling and k in model.Equipment:
                return model.crusher_equipment_cost[j, k]  == 0 
            else:
                return Constraint.Skip
        model.crusher_cost_grinding = Constraint(model.Milling, model.Equipment, rule=crusher_equipment_cost_rule)
        ## -------------------------------
        # Equipment cost of Pretreatment 
        # -------------------------------- 
        def equipment_pretreatment_cost_rule(model, j, k):
            if j=='enzymatic-hydrolysis' and k == 'Pump':
                return model.pretreatment_equipment_cost [j, k] == model.Base_equipment_cost['Pump'] * ((sum(model.Fpump1[n,'enzymatic-hydrolysis', 'Pump'] for n in model.Components)) / (model.Base_reference_mass['Pump']))** model.sizing_factor['Pump']
            elif j=='enzymatic-hydrolysis' and k in ['Heater','Autoclave','Cooler','Reactor']:
                return model.pretreatment_equipment_cost [j, k] == model.Base_equipment_cost[k] * ((sum(model.FPretreatment_component[ n,'enzymatic-hydrolysis', k] for n in model.Components for k in model.Equipment)) / (model.Base_reference_mass[k]))** model.sizing_factor[k]
            elif j=='enzymatic-hydrolysis' and k == 'Centrifugal':
                return model.pretreatment_equipment_cost [j, k] == model.Base_equipment_cost['Centrifugal'] * ((sum(model.FinalMass[ n,'enzymatic-hydrolysis', 'Centrifugal'] for n in model.Components)) / (model.Base_reference_mass['Centrifugal']))** model.sizing_factor['Centrifugal']
            elif j in model.FWManagementOption and k in model.Equipment:
                return model.pretreatment_equipment_cost  [j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_pretreatment_cost_constraints = Constraint(model.FWManagementOption,model.Equipment, rule=equipment_pretreatment_cost_rule)
        ## -------------------------------
        # Equipment cost of bioethanol
        # --------------------------------
        def equipment_bioethanol_cost_rule(model, j, k):
            if j=='BioethanolProcess' and k == 'Fermenter':
                return model.bioethanol_equipment_cost  [j, k] == model.Base_equipment_cost ['Fermenter'] * ((sum(model.FBioethanol1[ n,'BioethanolProcess', 'Fermenter'] for n in model.Components)) / (model.Base_reference_mass['Fermenter']))** model.sizing_factor['Fermenter']
            elif j=='BioethanolProcess' and k == 'FlashDrum':
                return  model.bioethanol_equipment_cost  [j, k] == model.Base_equipment_cost ['FlashDrum'] * ((sum(model.FinalMassFermenter1[ n,'BioethanolProcess', 'FlashDrum']for n in model.Components)) / (model.Base_reference_mass['FlashDrum']))** model.sizing_factor['FlashDrum']
            elif j == 'BioethanolProcess' and k == 'Pump':
                total_components1 = sum(model.FBioethanol1[n, 'BioethanolProcess', 'Pump'] +  model.Fflashdrum1_liquid[n, 'BioethanolProcess', 'Pump'] for n in model.Components)
                return model.bioethanol_equipment_cost[j, k] == model.Base_equipment_cost['Pump'] * (total_components1 / model.Base_reference_mass['Pump'])** model.sizing_factor['Pump']  
            elif j == 'BioethanolProcess' and k == 'Heater':
                total_components2 =  total_components2 = sum( model.Fflashdrum1_liquid[n, 'BioethanolProcess', 'Heater'] + model.FDT2_top[n, 'BioethanolProcess', 'Heater'] for n in model.Components)
                return model.bioethanol_equipment_cost[j, k] == model.Base_equipment_cost['Heater'] * (total_components2 / model.Base_reference_mass['Heater'])** model.sizing_factor['Heater']  
            elif j == 'BioethanolProcess' and k == 'DT':
                total_components3 = sum( model.Fflashdrum1_liquid[ n,  'BioethanolProcess', 'DT']+ model.FDT1_top [ n,  'BioethanolProcess', 'DT']for n in model.Components)
                return model.bioethanol_equipment_cost[j, k] == model.Base_equipment_cost['DT'] * (total_components3 / model.Base_reference_mass['DT'])** model.sizing_factor['DT']  
            elif j == 'BioethanolProcess' and k == 'Cooler':
                total_components4 = sum(model.FBioethanol1[ n, 'BioethanolProcess', 'Cooler'] + model.BioethanolProduct[ n,  'BioethanolProcess', 'Cooler'] for n in model.Components)
                return model.bioethanol_equipment_cost[j, k] == model.Base_equipment_cost['Cooler'] * (total_components4 / model.Base_reference_mass['Cooler']) ** model.sizing_factor['Cooler']  
            if j=='BioethanolProcess' and k == 'MS':
                return  model.bioethanol_equipment_cost  [j, k] == model.Base_equipment_cost ['MS'] * ((sum(model.FDT2_top[ n,  'BioethanolProcess', 'MS']for n in model.Components)) / (model.Base_reference_mass['MS']))**  model.sizing_factor['MS']
            elif j in model.Biofuels and k in model.Equipment:
                return model.bioethanol_equipment_cost  [j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_bioethanol_cost_constraints = Constraint(model.Biofuels, model.Equipment,  rule=equipment_bioethanol_cost_rule)
        ## -------------------------------
        # Equipment cost of Lactic Acid
        # --------------------------------
        def equipment_lactic_cost_rule(model, j, k):
            if j == 'LacticAcidProcess' and k == 'Pump':
                total_components8 = sum(model.FinLacticAcid1_component [n, 'LacticAcidProcess', 'Pump']  + model.FinalMassFermenter4[n,  'LacticAcidProcess', 'Pump'] + 
                                        model.FoutDT8_bottom_component [n,  'LacticAcidProcess', 'Pump'] + model.Finpump9_component [ n,  'LacticAcidProcess', 'Pump'] + model.FoutDT10_bottom_component[ n,  'LacticAcidProcess', 'Pump'] for n in model.Components)
                return model.Lactic_equipment_cost[j, k] == model.Base_equipment_cost['Pump'] * (total_components8 / model.Base_reference_mass['Pump'])** model.sizing_factor['Pump']  
            elif j == 'LacticAcidProcess' and k == 'Cooler':
                total_components9 = sum(model.FinLacticAcid1_component[ n, 'LacticAcidProcess', 'Cooler']   + model.FinLacticAcid4_component [ n,  'LacticAcidProcess', 'Cooler']for n in model.Components)
                return model.Lactic_equipment_cost[j, k] == model.Base_equipment_cost['Cooler'] * (total_components9 / model.Base_reference_mass['Cooler'])** model.sizing_factor['Cooler']  
            elif j=='LacticAcidProcess' and k == 'Fermenter':
                return model.Lactic_equipment_cost   [j, k] == model.Base_equipment_cost ['Fermenter']  * ((sum(model.FinLacticAcid1_component[n, 'LacticAcidProcess', 'Fermenter'] for n in model.Components)) / (model.Base_reference_mass['Fermenter']))**model.sizing_factor['Fermenter']
            elif j == 'LacticAcidProcess' and k == 'Heater':
                total_components10 = sum(model.FinalMassFermenter4[ n,  'LacticAcidProcess', 'Heater']  + model.FinLacticAcid3_component[ n,  'LacticAcidProcess', 'Heater'] + model.FinalMassReactor1[ n,  'LacticAcidProcess', 'Heater']+
                                        model.FinalMassReactor2[ n,  'LacticAcidProcess', 'Heater']for n in model.Components)
                return model.Lactic_equipment_cost[j, k] == model.Base_equipment_cost['Heater'] * (total_components10 / model.Base_reference_mass['Heater'])** model.sizing_factor['Heater']  
            elif j == 'LacticAcidProcess' and k == 'DT':
                total_components11 = sum(model.FinalMassFermenter4[ n,  'LacticAcidProcess', 'DT']  + model.FinalMassReactor1 [ n,  'LacticAcidProcess', 'DT']  + model.FoutDT9_top_component[ n,  'LacticAcidProcess', 'DT'] +
                                        model.FinalMassReactor2 [ n,  'LacticAcidProcess', 'DT'] + model.FoutDT11_top_component[ n,  'LacticAcidProcess', 'DT'] + model.FoutDT11_bottom_component[ n,  'LacticAcidProcess', 'DT'] for n in model.Components)
                return model.Lactic_equipment_cost[j, k] == model.Base_equipment_cost['DT'] * (total_components11 / model.Base_reference_mass['DT'])** model.sizing_factor['DT']  
            elif j == 'LacticAcidProcess' and k == 'Reactor1':
                total_components12 = sum(model.FinLacticAcid3_component[ n, 'LacticAcidProcess', 'Reactor1']   + model.FinLacticAcid4_component [ n, 'LacticAcidProcess', 'Reactor1']  for n in model.Components)
                return model.Lactic_equipment_cost[j, k] == model.Base_equipment_cost['Reactor1'] * (total_components12 / model.Base_reference_mass['Reactor1'])** model.sizing_factor['Reactor1']  
            elif j in model.Biochemicals and k in model.Equipment:
                return model.Lactic_equipment_cost[j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_lactic_cost_constraints = Constraint(model.Biochemicals, model.Equipment,  rule=equipment_lactic_cost_rule)
        ## -------------------------------
        # Equipment cost of Succinic Acid
        # --------------------------------
        def equipment_succinic_cost_rule(model, j, k):
            if j == 'SuccinicAcidProcess' and k == 'Cooler':
                total_components19 = sum(model.FinSuccinicAcid1_component[ n, 'SuccinicAcidProcess', 'Cooler']   + model.FoutEvaporator2_bottom_component[ n,  'SuccinicAcidProcess', 'Cooler']for n in model.Components)
                return model.Succinic_equipment_cost[j, k] == model.Base_equipment_cost['Cooler'] * (total_components19 / model.Base_reference_mass['Cooler'])** model.sizing_factor['Cooler'] 
            elif j=='SuccinicAcidProcess' and k == 'Pump':
                return model.Succinic_equipment_cost  [j, k] == model.Base_equipment_cost ['Pump'] * ((sum(model.FinSuccinicAcid1_component [n, 'SuccinicAcidProcess', 'Pump'] for n in model.Components)) / (model.Base_reference_mass['Pump']))** model.sizing_factor['Pump'] 
            elif j=='SuccinicAcidProcess' and k == 'Fermenter':
                return model.Succinic_equipment_cost  [j, k] == model.Base_equipment_cost ['Fermenter'] * ((sum(model.FinSuccinicAcid1_component [n, 'SuccinicAcidProcess', 'Fermenter'] for n in model.Components)) / (model.Base_reference_mass['Fermenter']))** model.sizing_factor['Fermenter']
            elif j=='SuccinicAcidProcess'  and k == 'Evaporator':
                return  model.Succinic_equipment_cost [j, k] == model.Base_equipment_cost [ 'Evaporator']  * ((sum(model.FinalMassFermenter5 [n, 'SuccinicAcidProcess', 'Evaporator'] for n in model.Components)) / (model.Base_reference_mass['Evaporator'])) ** model.sizing_factor['Evaporator']
            elif j=='SuccinicAcidProcess' and k == 'Crystallizer':
                return model.Succinic_equipment_cost  [j, k] == model.Base_equipment_cost ['Crystallizer'] * ((sum(model.FoutEvaporator2_bottom_component[n, 'SuccinicAcidProcess','Crystallizer'] for n in model.Components)) / (model.Base_reference_mass['Crystallizer']))** model.sizing_factor['Crystallizer']
            elif j=='SuccinicAcidProcess' and k == 'Separator':
                return model.Succinic_equipment_cost [j, k] == model.Base_equipment_cost['Separator'] * ((sum(model.FoutEvaporator2_bottom_component [ n,'SuccinicAcidProcess', 'Separator'] for n in model.Components)) / (model.Base_reference_mass['Separator']))** model.sizing_factor['Separator']
            elif j in model.Biochemicals and k in model.Equipment:
                return model.Succinic_equipment_cost[j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_succinic_cost_constraints = Constraint(model.Biochemicals, model.Equipment,  rule=equipment_succinic_cost_rule)
        ## -------------------------------
        # Equipment cost of BDO
        # --------------------------------
        def equipment_bdo_cost_rule(model, j, k):
            if j=='BDOProcess' and k in ['Pump','Cooler','Fermenter']:
                return model.BDO_equipment_cost  [j, k] == model.Base_equipment_cost [k] * ((sum(model.FinBDO_component[n, 'BDOProcess', k] for n in model.Components for k in model.Equipment)) / (model.Base_reference_mass[k]))** model.sizing_factor[k]
            elif j=='BDOProcess' and k == 'Comp':
                return model.BDO_equipment_cost  [j, k] == model.Base_equipment_cost ['Comp']  * ((sum(model.Fincomp1[n, 'BDOProcess', 'Comp'] for n in model.Components)) / (model.Base_reference_mass['Comp']))**  model.sizing_factor['Comp']
            elif j=='BDOProcess' and k == 'FlashDrum':
                total_components5 = sum( model.FinalMassFermenter2[n, 'BDOProcess','FlashDrum']  +  model.FoutDT3_top_gas_component[n, 'BDOProcess', 'FlashDrum'] for n in model.Components)
                return model.BDO_equipment_cost [j, k] == model.Base_equipment_cost['FlashDrum'] * (total_components5 / model.Base_reference_mass['FlashDrum'])** model.sizing_factor['FlashDrum']  
            elif j=='BDOProcess' and k == 'DT':
                return model.BDO_equipment_cost  [j, k] == model.Base_equipment_cost ['DT']  * ((sum(model.Foutflashdrum2_liquid_component[n, 'BDOProcess', 'DT'] for n in model.Components)) / (model.Base_reference_mass['DT']))**  model.sizing_factor['DT']
            elif j in model.Biochemicals and k in model.Equipment:
                return model.BDO_equipment_cost  [j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_bdo_cost_constraints = Constraint(model.Biochemicals, model.Equipment,  rule=equipment_bdo_cost_rule)
        ## -------------------------------
        # Equipment cost of Butanol
        # --------------------------------
        def equipment_butanol_cost_rule(model, j, k):
            if j == 'ButanolProcess' and k in ['Pump', 'Fermenter']:
                return model.Butanol_equipment_cost[j, k] == model.Base_equipment_cost[k] * ((sum(model.FinButanol_component[n, 'ButanolProcess', k] for n in model.Components for k in model.Equipment)) / (model.Base_reference_mass[k]))** model.sizing_factor[k]
            elif j == 'ButanolProcess' and k == 'FlashDrum':
                return model.Butanol_equipment_cost[j, k] == model.Base_equipment_cost['FlashDrum'] * ((sum(model.FinalMassFermenter3[ n,  'ButanolProcess', 'FlashDrum']  for n in model.Components)) /(model.Base_reference_mass['FlashDrum']))** model.sizing_factor['FlashDrum']
            elif j=='ButanolProcess' and k == 'PSA':
                return model.Butanol_equipment_cost  [j, k] == model.Base_equipment_cost ['PSA']  * ((sum(model.Foutflashdrum4_gas_component[n, 'ButanolProcess', 'PSA'] for n in  model.Components)) / (model.Base_reference_mass['PSA']))** model.sizing_factor['PSA']
            elif j == 'ButanolProcess' and k == 'DT':
                total_components6 = sum(model.Foutflashdrum4_liquid_component[n,'ButanolProcess','DT'] + model.FoutDT4_top_component [n, 'ButanolProcess', 'DT']  + 
                                    model.FoutDT5_bottom_component[n, 'ButanolProcess', 'DT']  +  model.FoutDecant1_top_component[n, 'ButanolProcess','DT']  for n in model.Components)
                return model.Butanol_equipment_cost[j, k] == model.Base_equipment_cost['DT'] * (total_components6 / model.Base_reference_mass['DT']) ** model.sizing_factor['DT']
            elif j == 'ButanolProcess' and k == 'Cooler':
                total_components7 = sum(model.FinButanol_component[n, 'ButanolProcess', 'Cooler'] + model.Foutflashdrum4_gas_component[n, 'ButanolProcess', 'Cooler'] for n in model.Components)
                return model.Butanol_equipment_cost [j, k] == model.Base_equipment_cost['Cooler'] * (total_components7 / model.Base_reference_mass['Cooler'])** model.sizing_factor['Cooler'] 
            elif j == 'ButanolProcess' and k == 'Decant':
                return model.Butanol_equipment_cost[j, k] == model.Base_equipment_cost['Decant'] * ((sum(model.FoutDT6_bottom_component[n, 'ButanolProcess', 'Decant'] for n in model.Components)) /(model.Base_reference_mass['Decant'])) ** model.sizing_factor['Decant']
            elif j in model.Biofuels  and k in model.Equipment:
                return model.Butanol_equipment_cost[j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_butanol_cost_constraints = Constraint(model.Biofuels , model.Equipment, rule=equipment_butanol_cost_rule)
        ## -------------------------------
        # Equipment cost of Biodiesel
        # --------------------------------
        def equipment_biodiesel_cost_rule(model, j, k):
            if j=='BiodieselProcess' and k == 'Extractor':
                return model.Biodiesel_equipment_cost  [j, k] == model.Base_equipment_cost ['Extractor'] * ((sum(model.FBiodiesel1[n, 'BiodieselProcess', 'Extractor'] for n in model.Components)) / (model.Base_reference_mass['Extractor']))** model.sizing_factor['Extractor']
            elif j=='BiodieselProcess'  and k == 'Centrifugal':
                total_components13 = sum( model.FBiodiesel1[n, j, 'Centrifugal']  +  model.FinalMassNeutralizer[ n,  j, 'Centrifugal'] for n in model.Components )
                return model.Biodiesel_equipment_cost  [j, k] == model.Base_equipment_cost ['Centrifugal'] * (total_components13 / (model.Base_reference_mass['Centrifugal']))** model.sizing_factor['Centrifugal']
            elif j=='BiodieselProcess'  and k == 'Evaporator':
                return model.Biodiesel_equipment_cost   [j, k] == model.Base_equipment_cost [ 'Evaporator']  * ((sum(model.FCentrifugal2_Liquid[n, 'BiodieselProcess', 'Evaporator'] for n in model.Components)) / (model.Base_reference_mass['Evaporator'])) ** model.sizing_factor['Evaporator']
            elif j=='BiodieselProcess' and k == 'Pump':
                total_components14 = sum(model.FEvaporator1_liquid [ n,  'BiodieselProcess', 'Pump'] + model.ChemicalBiodieselStream [ n,  'BiodieselProcess', 'Pump'] + model.FDT14_bottom[ n, 'BiodieselProcess', 'Pump'] for n in model.Components)
                return model.Biodiesel_equipment_cost  [j, k]  == model.Base_equipment_cost['Pump'] * (total_components14 / model.Base_reference_mass['Pump'])** model.sizing_factor['Pump']  
            elif j=='BiodieselProcess'  and k == 'Heater':
                return model.Biodiesel_equipment_cost  [j, k] == model.Base_equipment_cost ['Heater']  * ((sum(model.ChemicalBiodieselStream [ n,  'BiodieselProcess', 'Heater'] for n in model.Components)) / (model.Base_reference_mass['Heater'])) ** model.sizing_factor['Heater']
            elif j=='BiodieselProcess'  and k == 'TranesterReactor':
                return model.Biodiesel_equipment_cost  [j, k] == model.Base_equipment_cost  ['TranesterReactor']  * ((sum(model.FinalMassTranesterReactor[ n,  'BiodieselProcess', 'TranesterReactor'] for n in model.Components)) / (model.Base_reference_mass['TranesterReactor'])) ** model.sizing_factor['TranesterReactor']
            elif j=='BiodieselProcess' and k == 'DT':
                total_components15 = sum(model.FinalMassTranesterReactor[n, 'BiodieselProcess', 'DT'] + model.FWasher_top[ n,  j, 'Washer'] + 
                                    model.FCentrifugal3_Liquid[n, j, 'DT'] for n in model.Components)
                return model.Biodiesel_equipment_cost [j, k] == model.Base_equipment_cost['DT'] * (total_components15 / model.Base_reference_mass['DT']) ** model.sizing_factor['DT']
            elif j=='BiodieselProcess'  and k == 'Cooler':
                return model.Biodiesel_equipment_cost  [j, k] == model.Base_equipment_cost  ['Cooler']  * ((sum(model.FDT14_bottom[ n,  'BiodieselProcess', 'Cooler'] for n in model.Components)) / (model.Base_reference_mass['Cooler'])) ** model.sizing_factor['Cooler']
            elif j=='BiodieselProcess'  and k == 'Washer':
                return model.Biodiesel_equipment_cost  [j, k] == model.Base_equipment_cost ['Washer']  * ((sum(model.FWasher [ n,  'BiodieselProcess', 'Washer'] for n in model.Components)) / (model.Base_reference_mass['Washer'])) ** model.sizing_factor['Washer']
            elif j=='BiodieselProcess'  and k == 'Neutralizer':
                return model.Biodiesel_equipment_cost  [j, k] == model.Base_equipment_cost  ['Neutralizer']  * ((sum( model.FinalMassNeutralizer[ n,  'BiodieselProcess', 'Neutralizer'] for n in model.Components)) / (model.Base_reference_mass['Neutralizer']))** model.sizing_factor['Neutralizer']
            elif j in model.NonGlucoseUpgrading and k in model.Equipment:
                return model.Biodiesel_equipment_cost [j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_biodiesel_cost_constraints = Constraint(model.NonGlucoseUpgrading, model.Equipment,  rule=equipment_biodiesel_cost_rule)
        ## -------------------------------
        # Equipment cost of Protein
        # --------------------------------
        def equipment_protein_cost_rule(model, j, k):
            if j=='ProteinExtraction' and k == 'Pump':
                return model.Protein_equipment_cost  [j, k] == model.Base_equipment_cost ['Pump'] * ((sum(model.ChemicalConsumptionProtein [n, 'ProteinExtraction', 'Pump'] for n in model.Components)) / (model.Base_reference_mass['Pump']))** model.sizing_factor['Pump']
            elif j=='ProteinExtraction' and k == 'Extractor':
                return model.Protein_equipment_cost [j, k] == model.Base_equipment_cost ['Extractor'] * ((sum(model.FProtein[ n, 'ProteinExtraction', 'Extractor']   for n in model.Components)) / (model.Base_reference_mass['Extractor'])) ** model.sizing_factor['Extractor']
            elif j=='ProteinExtraction' and k == 'Centrifugal':
                return model.Protein_equipment_cost  [j, k] == model.Base_equipment_cost ['Centrifugal']  * ((sum(model.FProtein[n,'ProteinExtraction','Centrifugal']  for n in model.Components)) / (model.Base_reference_mass['Centrifugal'])) ** model.sizing_factor['Centrifugal']
            elif j=='ProteinExtraction' and k == 'Filtration':
                return model.Protein_equipment_cost  [j, k] == model.Base_equipment_cost  ['Filtration']  * ((sum(model.FCentrifugal4_Liquid[n, 'ProteinExtraction', 'Filtration'] for n in model.Components)) / (model.Base_reference_mass['Filtration']))** model.sizing_factor['Filtration']
            elif j in model.NonGlucoseUpgrading and k in model.Equipment:
                return model.Protein_equipment_cost [j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_protein_cost_constraints = Constraint(model.NonGlucoseUpgrading, model.Equipment,  rule=equipment_protein_cost_rule)
        ## -------------------------------
        # Equipment cost of Anaerobic digestion 
        # --------------------------------
        def equipment_biogas_cost_rule(model, j, k):
            if j=='AnaerobicDigestion' and k in ['Digester','Cooler']:
                return model.AD_equipment_cost  [j, k] == model.Base_equipment_cost [k] * ((sum(model.FAD[n,'AnaerobicDigestion',k] for n in model.Macronutrients for k in model.Equipment)) / (model.Base_reference_mass[k]))** model.sizing_factor[k]
            elif j=='AnaerobicDigestion'  and k == 'FlashDrum':
                return model.AD_equipment_cost    [j, k] == model.Base_equipment_cost ['FlashDrum']  * ((sum(model.FinalMassDigester[ n,'AnaerobicDigestion','FlashDrum'] for n in model.Components)) / (model.Base_reference_mass['FlashDrum']))** model.sizing_factor['FlashDrum']
            elif j=='AnaerobicDigestion'  and k == 'Centrifugal':
                return model.AD_equipment_cost  [j, k] == model.Base_equipment_cost ['Centrifugal']  * ((sum(model.Fflashdrum5_liquid[ n,  'AnaerobicDigestion', 'Centrifugal'] for n in model.Components)) / (model.Base_reference_mass['Centrifugal'])) ** model.sizing_factor['Centrifugal']
            elif j=='AnaerobicDigestion'   and k == 'Comp':
                return model.AD_equipment_cost [j, k] == model.Base_equipment_cost ['Comp']  * ((sum(model.Fflashdrum5_gas[n, 'AnaerobicDigestion', 'Comp'] for n in model.Components)) / (model.Base_reference_mass['Comp'])) ** model.sizing_factor['Comp']
            elif j=='AnaerobicDigestion'   and k == 'Membrane':
                return model.AD_equipment_cost [j, k] == model.Base_equipment_cost ['Membrane']  * ((sum(model.Fflashdrum5_gas[n, 'AnaerobicDigestion', 'Membrane'] for n in model.Components)) / (model.Base_reference_mass['Membrane'])) ** model.sizing_factor['Membrane']
            elif j=='AnaerobicDigestion'   and k == 'Membrane':
                return model.AD_equipment_cost [j, k] == model.Base_equipment_cost ['Membrane'] * ((sum(model.FoutStage1_top[ n, 'AnaerobicDigestion', 'Membrane'] for n in model.Components)) / (model.Base_reference_mass['Membrane'])) ** model.sizing_factor['Membrane'] 
            elif j in model.FWManagementOption and k in model.Equipment:
                return model.AD_equipment_cost  [j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_biogas_cost_constraints = Constraint(model.FWManagementOption, model.Equipment,  rule=equipment_biogas_cost_rule)       
        ## -------------------------------
        # Equipment cost of Incineration
        # --------------------------------
        def equipment_incineration_cost_rule(model, j, k):
            if j=='Incineration' and k == 'Comp':
                return model.Incineration_equipment_cost  [j, k] == model.Base_equipment_cost ['Comp'] * ((sum(model.FComp4 [n, 'Incineration', 'Comp'] for n in model.Components)) / (model.Base_reference_mass['Comp'])) ** model.sizing_factor['Comp']
            elif j== 'Incineration'  and k == 'Burner':
                return model.Incineration_equipment_cost   [j, k] == model.Base_equipment_cost ['Burner'] * ((sum(model.FinalMassBurner[ n, 'Incineration', 'Burner']   for n in model.Components)) / (model.Base_reference_mass['Burner']))** model.sizing_factor['Burner']
            elif j=='Incineration'   and k == 'Turbine':
                return model.Incineration_equipment_cost    [j, k] == model.Base_equipment_cost ['Turbine']  * ((sum(model.FinalMassBurner [n, 'Incineration', 'Turbine'] for n in model.Components)) / (model.Base_reference_mass['Turbine'])) ** model.sizing_factor['Turbine']
            elif j=='Incineration'  and k == 'Economizer':
                total_components17 = sum(model.FinalMassBurner[ n,  'Incineration', 'Economizer']  + model.FCooler[ n,  'Incineration', 'Economizer'] for n in model.Components)
                return model.Incineration_equipment_cost  [j, k] == model.Base_equipment_cost['Economizer'] * (total_components17 / model.Base_reference_mass['Economizer'])** model.sizing_factor['Economizer'] 
            elif j=='Incineration'  and k == 'Cooler':
                return model.Incineration_equipment_cost [j, k] == model.Base_equipment_cost  ['Cooler']  * ((sum(model.FCooler[ n,  'Incineration', 'Cooler'] for n in model.Components)) / (model.Base_reference_mass['Cooler'])) ** model.sizing_factor['Cooler']
            elif j=='Incineration'  and k == 'Pump':
                return model.Incineration_equipment_cost [j, k] == model.Base_equipment_cost  ['Pump']  * ((sum(model.FCooler[ n,  'Incineration', 'Pump'] for n in model.Components)) / (model.Base_reference_mass['Pump'])) ** model.sizing_factor['Pump']
            elif j in model.FWManagementOption and k in model.Equipment:
                return model.Incineration_equipment_cost  [j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_incineration_cost_constraints = Constraint(model.FWManagementOption, model.Equipment,  rule=equipment_incineration_cost_rule)
        ## -------------------------------
        # Equipment cost of Carbon Capture
        # --------------------------------
        def equipment_CCU_cost_rule(model, j, k):
            if j=='CCU'  and k =='Cooler':
                total_components18 = sum(model.FCCU1[ n,'CCU','Cooler'] + model.FoutDT18_liquid[n,'CCU','Cooler'] * 6  for n in model.Components)
                return model.CCU_equipment_cost [j, k] == model.Base_equipment_cost['Cooler'] * (total_components18 / model.Base_reference_mass['Cooler']) ** model.sizing_factor['Cooler']  
            elif j=='CCU'  and k == 'Absorber':
                return model.CCU_equipment_cost [j, k] == model.Base_equipment_cost ['Absorber'] * ((sum(model.FinAbsorber2[n, 'CCU', 'Absorber'] for n in model.Components)) / (model.Base_reference_mass['Absorber'])) ** model.sizing_factor['Absorber']
            elif j=='CCU'  and k == 'Pump':
                return model.CCU_equipment_cost [j, k] == model.Base_equipment_cost ['Pump'] * ((sum(model.FoutAbsorber2_bottom[ n, 'CCU', 'Pump'] for n in model.Components)) / (model.Base_reference_mass['Pump'])) ** model.sizing_factor['Pump']
            elif j=='CCU'  and k == 'HE':
                return model.CCU_equipment_cost [j, k]  == model.Base_equipment_cost ['HE']  * ((sum(model.FoutAbsorber2_bottom[ n, 'CCU', 'HE'] for n in model.Components)) / (model.Base_reference_mass['HE']))** model.sizing_factor['HE']
            elif j=='CCU'  and k == 'DT':
                return model.CCU_equipment_cost [j, k]  == model.Base_equipment_cost ['DT'] * ((sum(model.FoutAbsorber2_bottom[ n,  'CCU', 'DT'] for n in model.Components)) / (model.Base_reference_mass['DT']))** model.sizing_factor['DT'] 
            elif j=='CCU'  and k == 'Comp':
                return model.CCU_equipment_cost [j, k]  == model.Base_equipment_cost ['Comp'] * ((sum(model.CO2_compression[ n,  'CCU', 'Comp'] for n in model.Components)*6) / (model.Base_reference_mass['Comp']))** model.sizing_factor['Comp'] 
            elif j=='CCU'  and k == 'FlashDrum':
                return model.CCU_equipment_cost [j, k]  == model.Base_equipment_cost ['FlashDrum'] * ((sum(model.CO2_compression[ n,  'CCU', 'FlashDrum'] for n in model.Components)*6) / (model.Base_reference_mass['FlashDrum']))** model.sizing_factor['FlashDrum']  
            elif j in model.CarbonCapture and k in model.Equipment:
                return model.CCU_equipment_cost [j, k] == 0
            else:
                return Constraint.Skip
        model.equipment_CCU_cost_constraints = Constraint(model.CarbonCapture, model.Equipment,  rule=equipment_CCU_cost_rule)
        ## -------------------------------
        # Total equipment cost 
        # --------------------------------
        def equipment_total_cost_rule(model):
            return model.Equipment_total_cost ==  sum(model.crusher_equipment_cost['grinding', k] + model.pretreatment_equipment_cost ['enzymatic-hydrolysis', k] + model.bioethanol_equipment_cost ['BioethanolProcess', k] + 
                                                      model.Lactic_equipment_cost['LacticAcidProcess', k] + model.Succinic_equipment_cost ['SuccinicAcidProcess', k] + model.BDO_equipment_cost ['BDOProcess', k] + 
                                                      model.Butanol_equipment_cost  ['ButanolProcess', k] + model.Biodiesel_equipment_cost ['BiodieselProcess',k] + model.Protein_equipment_cost ['ProteinExtraction',k] + 
                                                      model.AD_equipment_cost['AnaerobicDigestion',k] + model.Incineration_equipment_cost ['Incineration', k] + model.CCU_equipment_cost ['CCU', k] for k in model.Equipment) 
        model.equipment_total_cost_constraint = Constraint(rule=equipment_total_cost_rule)
        ## -------------------------------
        # Capital investment
        # --------------------------------
        #1. Total plant direct cost 
        def total_plant_direct_cost_rule(model):
            return model.total_plant_direct_cost == (
                model.Equipment_total_cost +
                model.Equipment_total_cost * model.equipment_installation + 
                model.Equipment_total_cost * model.instrumentation_control_system + 
                model.Equipment_total_cost * model.process_piping + 
                model.Equipment_total_cost * model.electrical_equipment + 
                model.Equipment_total_cost * model.buildings + 
                model.Equipment_total_cost * model.site_development + 
                model.Equipment_total_cost * model.auxiliary_facilities)
        model.Total_plant_direct_cost_constraint = Constraint(rule=total_plant_direct_cost_rule)
        #2.Total plant indirect cost
        def total_plant_indirect_cost_rule(model):
            return model.total_plant_indirect_cost == model.Equipment_total_cost * (model.engineering + model.construction)
        model.total_plant_indirect_cost_constraint = Constraint(rule=total_plant_indirect_cost_rule)
        #3. Total plant cost
        def total_plant_cost_rule(model):
            return model.total_plant_cost == model.total_plant_direct_cost + model.total_plant_indirect_cost
        model.Total_plant_cost_constraint = Constraint(rule=total_plant_cost_rule)
        #5. Capital cost of composting 
        def capital_composting_rule(model):
            return model.CapitalInvestmentComposting == model.Finfeedstock['Composting'] * 128 #$/tFW
        model.Capital_cost_composting = Constraint(rule=capital_composting_rule)
        #Capital cost of AnimalFeed 
        def capital_AnimalFeed_rule(model):
            return model.CapitalInvestmentAnimalFeed == model.Finfeedstock['AnimalFeed'] * 14.58 #$/tFW
        model.Capital_cost_AnimalFeed  = Constraint(rule=capital_AnimalFeed_rule)
        #4. Fixed capital investment 
        def fixed_capital_investment_rule(model):
            return model.fixed_capital_investment == model.total_plant_cost * (1 + model.constractor_fee + model.contingency)
        model.fixed_capital_investment_constraint = Constraint(rule=fixed_capital_investment_rule)
        #6. Total capital investment 
        def total_capital_investment_rule(model):
            return model.total_capital_investment == model.fixed_capital_investment * (model.working_capital +model.land_use) + model.fixed_capital_investment + model.CapitalInvestmentComposting + model.CapitalInvestmentAnimalFeed 
        model.total_capital_investment_constraint = Constraint(rule=total_capital_investment_rule)

# ======================================================
# Cost Model
# ======================================================
class CostModel:
    """Unified class that groups Cost models."""

    def __init__(self, model):
        """Attach all process constraints to one existing AbstractModel."""
        self.model = model
        self.OperatingCost = OperatingCostModel(model)
        self.CapitalInvestment = CapitalInvestmentModel(model)                                               

    def get_models(self):
        """Return all sub-models (for inspection or solving separately)."""
        return {
            'OperaatingCost': self.OperatingCost.model,
            'CapitalInvestment': self.CapitalInvestment.Model
        }    

