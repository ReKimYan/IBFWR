#Economicmodel
from pyomo.environ import *

class MOOModel:
    """MOO constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach grinding constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Products
        # --------------------------------  
        # 1. Bioethanol
        def Bioethanol_outflow_rule(m):
            return m.TotalBioethanol  == sum(m.BioethanolProduct [n, 'BioethanolProcess', 'Cooler'] for n in m.Components )
        m.Bioethanoloutflow = Constraint(rule=Bioethanol_outflow_rule)
        
        # 2. Lactic Acid
        def LA_outflow_rule(m):
            return m.TotalLA  == sum(m.LacticAcidProduct[n, 'LacticAcidProcess', 'DT'] for n in m.Components )
        m.LAoutflow = Constraint(rule=LA_outflow_rule)
        
        # 3. BDO
        def BDO_outflow_rule(m):
            return m.TotalBDO  == sum(m.BDO_product [n, 'BDOProcess', 'DT'] for n in m.Components )
        m.BDOoutflow = Constraint(rule=BDO_outflow_rule)
        
        # 4. SA
        def SA_outflow_rule(m):
            return m.TotalSA  == sum(m.SuccinicAcidProduct [ n,'SuccinicAcidProcess','Centrifugal'] for n in m.Components)
        m.SAoutflow = Constraint(rule=SA_outflow_rule)
        
        # 5. Butanol
        def Butanol_outflow_rule(m):
            return m.TotalButanol  == sum(m.Butanol_product [n, 'ButanolProcess', 'DT'] for n in m.Components )
        m.Butanoloutflow = Constraint(rule=Butanol_outflow_rule)
        
        # 6. Biodiesel
        def Biodiesel_outflow_rule(m):
            return m.TotalBiodiesel == sum(m.Biodiesel_product [n,'BiodieselProcess','DT'] for n in m.Components)
        m.Biodieseloutflow = Constraint(rule=Biodiesel_outflow_rule)
        
        # 7. Protein
        def Protein_outflow_rule(m):
            return m.TotalProtein == sum(m.ProteinProduct[n,'ProteinExtraction','Filtration'] for n in m.Components)
        m.Proteinoutflow = Constraint(rule=Protein_outflow_rule)
        
        # 8. BioCNG
        def BioCNG_outflow_rule(m):
            return m.TotalBioCNG  ==  sum(m.BioCNG_product[n,'AnaerobicDigestion'] for n in m.Components)
        m.BioCNGoutflow = Constraint(rule=BioCNG_outflow_rule)
        
        # 9. CO2
        def CO2_outflow_rule(m):
            return m.TotalCO2 == sum(m.CO2_compression[n,'CCU','Cooler'] for n in m.Components)
        m.CO2outflow = Constraint(rule=CO2_outflow_rule)
        
        # ## -------------------------------
        # # Co-products
        # # --------------------------------  
        # 1. Total glycerol
        def Glycerol_outflow_rule(m):
            return m.TotalGlycerol == sum(m.Glycerol_coproduct[n, 'BiodieselProcess', 'DT'] for n in m.Components)
        m.Glyceroloutflow = Constraint(rule=Glycerol_outflow_rule)
        
        # 2. Total fertilizer
        def Fertilizer_outflow_rule(m):
            return m.TotalFertilizer  == sum(m.Fertilizer_coproduct[n,'AnaerobicDigestion','Centrifugal'] for n in m.Components)
        m.Fertilizeroutflow = Constraint(rule=Fertilizer_outflow_rule)
        
        # 3. Acetone
        def Acetone_outflow_rule(m):
            return m.TotalAcetoneCoproduct  == sum(m.Acetone_coproduct [n,'ButanolProcess','DT']for n in m.Components)
        m.Acetoneoutflow = Constraint(rule=Acetone_outflow_rule)

        # 4. Bioethanol 
        def Ethanol_outflow_rule(m):
            return m.EthanolCoproduct  == sum(m.Ethanol_coproduct [n,'ButanolProcess','DT']for n in m.Components) 
        m.Ethanoloutflow = Constraint(rule=Ethanol_outflow_rule)
        
        # 5. Hydrogen
        def H2_outflow_rule(m):
            return m.TotalH2Coproduct   == sum(m.H2_coproduct[n, 'ButanolProcess', 'PSA'] for n in m.Components) 
        m.H2outflow = Constraint(rule=H2_outflow_rule)
        
        # ## -------------------------------
        # # Waste recovery
        # # --------------------------------
        # 1. Organic waste 
        def Organicwaste_outflow_rule(m):
            return m.Organicwaste   == sum(m.FWaste[n,'AnaerobicDigestion','Cooler'] for n in m.Components) 
        m.Organicwasteoutflow = Constraint(rule=Organicwaste_outflow_rule)
        
        # 2. Solid waste
        def Solidwaste_outflow_rule(m):
            return m.SolidWaste  == sum(m.FCentrifugal4_Solid[n,'ProteinExtraction', 'Centrifugal'] for n in m.Components) 
        m.Solidwasteoutflow = Constraint(rule=Solidwaste_outflow_rule)
        
        # 3. Fluegas 
        def Fluegas_outflow_rule(m):
            return m.FlueGasStream  == sum(m.Fluegas [n,'Incineration', 'Cyclone'] for n in m.Components) 
        m.Fluegasoutflow = Constraint(rule=Fluegas_outflow_rule)
	
    	# 4. Offgas 
        def Offgas_outflow_rule(m):
            return m.OffgasStream  == sum(m.FoutStage1_CO2[n,'AnaerobicDigestion','Membrane'] + m.FoutStage2_CO2[n, 'AnaerobicDigestion','Membrane'] for n in m.Components) 
        m.Offgasoutflow = Constraint(rule=Offgas_outflow_rule)

        
        # --------------------------------  
        # Gate fee
        # --------------------------------
        def Gate_Fee_Composting_rule (m):
            return m.GateFeeComposting == m.Finfeedstock['Composting']  *84.48
        m.GateFeeComposting_constraint = Constraint (rule=Gate_Fee_Composting_rule)
        
        def Gate_Fee_AD_rule (m):
            return m.GateFeeAD == m.Finfeedstock['AnaerobicDigestion'] * 34.32
        m.GateFeeAD_constraint = Constraint (rule=Gate_Fee_AD_rule)
        
        def Gate_Fee_Incineration_rule (m):
            return m.GateFeeIncineration == m.Finfeedstock['Incineration'] * 154.44
        m.GateFeeIncineration_constraint = Constraint (rule=Gate_Fee_Incineration_rule)
        
        # --------------------------------  
        # the GGSS (Green Gas Support Scheme)
        # --------------------------------
        def GGSS_incentive_rule(m):
            # Calculate total annual energy production in MWh
            total_production_MWh = m.TotalBioCNG * 50000 * 0.0002777778 

            # Define tiered incentives with piecewise linear constraints
            # Introduce intermediate variables for each tier's production
            m.tier1_production = Var(within=NonNegativeReals)
            m.tier2_production = Var(within=NonNegativeReals)
            m.tier3_production = Var(within=NonNegativeReals)
            
            # Constraint for tier production limits based on total production
            m.tier1_limit = Constraint(expr=m.tier1_production <= 60000)
            m.tier2_limit = Constraint(expr=m.tier2_production <= 40000)
            m.tier3_limit = Constraint(expr=m.tier3_production <= 150000)

            # Ensure the total production is distributed across tiers correctly
            m.production_distribution = Constraint(
                expr=total_production_MWh == m.tier1_production + m.tier2_production + m.tier3_production
            )

            # Define the incentives for each tier
            tier1_incentive = m.tier1_production * 6.69 * 1.26 / 100  # Tier 1 rate
            tier2_incentive = m.tier2_production * 4.16 * 1.26 / 100  # Tier 2 rate
            tier3_incentive = m.tier3_production * 3.88 * 1.26 / 100  # Tier 3 rate

            # Calculate total incentive as the sum of incentives from each tier
            incentive = tier1_incentive + tier2_incentive + tier3_incentive

            # Set the model's GGSS_biomethane revenue variable
            return m.GGSS_biomethane == incentive
        # Applying the incentive rule constraint
        m.Biogas_incentive_constraint = Constraint(rule=GGSS_incentive_rule)
        
        # --------------------------------  
        #Revenue
        # --------------------------------
        def total_product_revenue_rule(m): 
            return m.total_product_revenue == (m.TotalBioethanol  * m.ProductSellingPrice['bioethanol'] + m.TotalLA * m.ProductSellingPrice ['LacticAcid'] +   m.TotalSA * m.ProductSellingPrice['SuccinicAcid'] + 
                                               m.TotalBDO * m.ProductSellingPrice ['BDO'] + m.TotalBiodiesel * m.ProductSellingPrice['FAME'] + m.TotalGlycerol * m.ProductSellingPrice['Glycerol'] + 
                                               m.TotalButanol * m.ProductSellingPrice['Butanol']+m.TotalAcetoneCoproduct * m.ProductSellingPrice['Acetone'] + m.TotalH2Coproduct * m.ProductSellingPrice ['H2'] + 
                                               m.EthanolCoproduct * m.ProductSellingPrice['bioethanol'] + m.TotalProtein * m.ProductSellingPrice['Protein'] + m.Compost_product * m.ProductSellingPrice['compost'] +
                                               m.GateFeeComposting + m.Feed_product * m.ProductSellingPrice ['Feed'] + m.TotalBioCNG* m.ProductSellingPrice ['CH4'] + m.GateFeeAD + m.TotalFertilizer* m.ProductSellingPrice ['compost'] +
                                               m.GGSS_biomethane + m.ElectricityGenerated * m.ProductSellingPrice['electricity']+ m.GateFeeIncineration + m.TotalCO2  * m.ProductSellingPrice['CO2']) * 300 
        m.total_product_revenue_constraint = Constraint(rule=total_product_revenue_rule)
        
        
        #--------------------------------  
        #Cash flow
        # --------------------------------
        # 1. Depreciation Rule
        def depreciation_rule(m, year):
            if year in m.DepreciationYears:  # Only apply MACRS depreciation from year 4 to 13
                return m.depreciation[year] == m.fixed_capital_investment * m.macrs_percentage[year]
            else:
                return m.depreciation[year] == 0
        m.depreciation_constraint = Constraint(m.OperationalYears, rule=depreciation_rule)
        # 2.Gross Profit Calculation
        def gross_profit_rule(m, year):
            return m.gross_profit[year] == m.total_product_revenue - m.total_operating_cost
        m.gross_profit_constraint = Constraint(m.OperationalYears, rule=gross_profit_rule)
        # 3.Profit Before Tax Calculation
        def profit_before_tax_rule(m, year):
            return m.profit_before_tax[year] == m.gross_profit[year] - m.depreciation[year]
        m.profit_before_tax_constraint = Constraint(m.OperationalYears, rule=profit_before_tax_rule)
        # 4.Tax Indicator Constraints
        def tax_indicator_rule_upper(m, year):
            return m.profit_before_tax[year] <= m.tax_indicator[year] * m.large_number
        m.tax_indicator_constraint_1 = Constraint(m.OperationalYears, rule=tax_indicator_rule_upper)

        def tax_indicator_rule_lower(m, year):
            return m.profit_before_tax[year] >= m.tax_indicator[year] * m.small_number
        m.tax_indicator_constraint_2 = Constraint(m.OperationalYears, rule=tax_indicator_rule_lower)
        # 5.Income Tax Calculation
        def income_tax_rule(m, year):
            return m.income_tax[year] == m.profit_before_tax[year] * m.federal_tax_rate * m.tax_indicator[year]
        m.income_tax_constraint = Constraint(m.OperationalYears, rule=income_tax_rule)
        # 6.Net Profit Calculation (corrected)
        def net_profit_rule(m, year):
            return m.net_profit[year] == m.profit_before_tax[year] - m.income_tax[year]
        m.net_profit_constraint = Constraint(m.OperationalYears, rule=net_profit_rule)
        # 7.Net Cash Flow Calculation
        def net_cash_flow_rule(m, year):
            if year in m.ConstructionYears:
                # During construction years, cash flow is negative due to investments
                return m.net_cash_flow[year] == -(m.total_capital_investment* m.investment_percentage[year])
            elif year in m.OperationalYears:
                # During operational years, cash flow equals net profit
                return m.net_cash_flow[year] == m.net_profit[year] + m.depreciation[year]
        m.net_cash_flow_constraint = Constraint(m.ConstructionYears | m.OperationalYears, rule=net_cash_flow_rule)
        # 8. Discounted Cash Flow Calculation
        def discounted_cash_flow_rule(m, year):
            # exponent = year index (1,2,3,...,33)
            t = year
            return m.discounted_cash_flow[year] == m.net_cash_flow[year] / ((1 + m.discount_rate)**t)

        m.discounted_cash_flow_constraint = Constraint(m.ConstructionYears | m.OperationalYears,rule=discounted_cash_flow_rule)
        # 9.NPV Calculation
        def npv_rule(m):
            return m.npv == sum(m.discounted_cash_flow[year] for year in  m.ConstructionYears | m.OperationalYears)
        m.npv_constraint = Constraint(rule=npv_rule)

        # # Ensure that investment percentages sum to 1
        # assert sum(investment_distribution.values()) == 1, "Investment distribution percentages must sum to 1."

        #--------------------------------  
        # Job generation constraint
        # --------------------------------
        def job_generation_rule(m, p):
            return m.JobGeneration[p] == m.total_capital_investment* m.JobGenerationMultiplier[p]/1e6
        m.JobGeneration_constraint = Constraint(m.SocialImpact, rule=job_generation_rule)
        
        #--------------------------------  
        # Social Impact (SI) aggregation
        # --------------------------------
        def SI_rule(m):
            return m.SIA == sum(m.JobGeneration[p] for p in m.SocialImpact)
        m.SI_constraint = Constraint(rule=SI_rule)
        
        ## -------------------------------
        # Energy emission
        # -------------------------------- 
        # 1. Electricity 
        def GWP_electricity_rule(m):
            return m.GWPelectricity == m.Utin_electricity_total_consumption ['electricity'] * m.GWPutility['electricity'] 
        m.GWP_electricity_constraint = Constraint(rule=GWP_electricity_rule)      
        # 2. Cooling-water
        def GWP_coolingwater_rule(m):
            return m.GWPcoolingwater == m.Utin_coolingwater_total_consumption ['cooling-water']* m.GWPutility['cooling-water']
        m.GWP_coolingwater_constraint = Constraint (rule=GWP_coolingwater_rule)       
        # 3. Heating 
        def GWP_heating_rule(m):
            return m.GWPheat ==  m.Utin_heat_total_consumption ['heat'] * m.GWPutility['heat']
        m.GWP_heating_constraint = Constraint (rule=GWP_heating_rule)       
        # 4. Chilling
        def GWP_chilling_rule(m):
            return m.GWPchilling ==  m.GWPutility['chilling'] *  m.Utin_chilling_Succinic['chilling'] 
        m.GWP_chilling_constraint = Constraint (rule=GWP_chilling_rule)
        
        ## -------------------------------
        # Chemical use and direct emission
        # --------------------------------
        # 1. Chemical
        def GWP_chemical_rule(m):
            return m.GWPchemicalLCA == (sum(m.Chemical_pretreatment_consumption [c,'enzymatic-hydrolysis',k] * m.GWPchemical[c] for c in m.Chemicals for k in m.Equipment)+
                                            sum(m.Total_Chemical_Bioethanol_Consumption[c, 'BioethanolProcess', 'Fermenter'] * m.GWPchemical[c] for c in m.Chemicals)+
                                            sum(m.Total_Chemical_BDO_Consumption [c, 'BDOProcess', 'Fermenter'] * m.GWPchemical[c] for c in m.Chemicals)+
                                            sum(m.Total_Chemical_Butanol_Consumption[c, 'ButanolProcess', 'Fermenter'] * m.GWPchemical[c] for c in m.Chemicals)+
                                            sum(m.Total_Chemical_Succinic_Consumption[c, 'SuccinicAcidProcess', 'Fermenter'] * m.GWPchemical[c] for c in m.Chemicals)+
                                            sum(m.Total_Chemical_Lactic_Consumption[c, 'LacticAcidProcess','Fermenter'] * m.GWPchemical[c] for c in m.Chemicals) +
                                            sum(m.Chemical_Biodiesel_Consumption[n, 'BiodieselProcess'] * m.GWPchemicalNonFermentation[n] for n in m.GWPchemicalNonFermentation)+
                                            sum(m.Chemical_Protein_Consumption[n, 'ProteinExtraction'] * m.GWPchemicalNonFermentation['NaOH'] for n in m.GWPchemicalNonFermentation)+
                                            sum(m.Chemical_composting_Consumption[n,'Composting']*m.GWPchemicalComposting[n] for n in m.GWPchemicalComposting))
        m.GWP_chemical_constraint = Constraint (rule=GWP_chemical_rule)
        # 2. Direct emission
        def GWP_DirectEmission_rule(m):
            return m.GWPEmissionDirect == (m.Compost_product * m.EmissionComposting['CH4', 'Composting'] * m.GWPDirectEmission['CH4'] + 
                                           sum(m.Feed_product * m.EmissionAnimalFeed[e,'AnimalFeed'] * m.GWPDirectEmission[e] for e in m.Emissions) + 
                                           m.FoutAbsorber2_top['CH4','CCU', 'Absorber'] * m.GWPDirectEmission['CH4'] + 
                                           m.FoutAbsorber2_top['CO2','CCU', 'Absorber'] * m.GWPDirectEmission['CO2'])
        m.GWP_DirectEmission_constraint = Constraint (rule=GWP_DirectEmission_rule)
        
        ## -------------------------------
        # Credit
        # --------------------------------
        def GWP_credit_rule(m):
            return m.GWPcredit == (m.TotalBioethanol * m.GWPProduct['bioethanol'] + m.TotalBDO * m.GWPProduct['BDO'] + m.TotalButanol *  m.GWPProduct['Butanol'] +
                                   m.TotalAcetoneCoproduct * m.GWPProduct['Acetone'] + m.TotalH2Coproduct * m.GWPProduct['H2'] + m.EthanolCoproduct * m.GWPProduct['bioethanol'] +
                                   + m.TotalSA * m.GWPProduct['SuccinicAcid'] + m.TotalLA * m.GWPProduct['LacticAcid'] + m.TotalBiodiesel * m.GWPProduct['FAME']+ 
                                   m.TotalGlycerol * m.GWPProduct['Glycerol'] + m.TotalProtein * m.GWPProduct['Protein'] + m.TotalBioCNG * m.GWPProduct['CH4']+ 
                                   m.TotalFertilizer  * m.GWPProduct['compost'] + m.ElectricityGenerated * m.GWPProduct['electricity'] + m.Compost_product * m.GWPProduct['compost'] +
                                   m.TotalCO2*m.GWPProduct['CO2'] + m.Feed_product * m.GWPProduct['Feed'] )
        m.GWP_credit_constraint = Constraint(rule=GWP_credit_rule)
        
        ## -------------------------------
        # GWP total
        # --------------------------------
        def GWP_total_rule(m):
            return m.GWPSavings ==m.GWPcredit-(m.GWPelectricity + m.GWPcoolingwater+m.GWPheat+m.GWPchilling+m.GWPchemicalLCA+m.GWPEmissionDirect )
        m.GWPtotal_constraint = Constraint(rule=GWP_total_rule)
        
        
        
        
        