#Carbon capture
from pyomo.environ import *

class CarbonCaptureModel:
    """Carbon capture process constraints (no sets, params, or vars)."""

    def __init__(self, model):
        """Attach Carbon capture constraints to an existing model."""
        self.model = model
        self._add_constraints()

    def _add_constraints(self):
        m = self.model
        
        ## -------------------------------
        # Gas stream
        # --------------------------------        
        def flow_CCU1_balance_rule(m, n, j, k):
            if n in ['CO2','O2','N2','Water','CH4','NH3'] and j =='CCU' and k == 'Cooler':
                return m.FCCU1[n,j,k] ==   (m.Fluegas [n, 'Incineration', 'Cyclone'] + m.FoutStage1_CO2[n,'AnaerobicDigestion','Membrane'] + m.FoutStage2_CO2[n, 'AnaerobicDigestion','Membrane'] + 
                                           m.CO2_stream_Butanol[n, 'ButanolProcess', 'PSA'] +
                                           m.CO2_stream_BDO[n,'BDOProcess'] +
                                           m.Fflashdrum1_gas[ n, 'BioethanolProcess', 'FlashDrum'])
            elif n in m.Components and j in m.CarbonCapture and k in m.Equipment:
                  return  m.FCCU1[n,j,k] == 0   
            else:
                  return Constraint.Skip
        m.flow_CCU1_balance_rule = Constraint(m.Components, m.CarbonCapture, m.Equipment, rule=flow_CCU1_balance_rule)

        ## -------------------------------
        # Solvent stream
        # --------------------------------
        def total_chemical_absorber2_needed_rule(m, n,j):
            if n=='Water' and j == 'CCU' :
                return m.total_chemical_absorber2_needed[n,j] == sum(m.FCCU1[n,'CCU', 'Cooler'] for n in m.Components) * 3.08 * m.SolventCCU['Water'] 
            elif n in ['PZ','MDEA'] and j == 'CCU':
                return m.total_chemical_absorber2_needed[n, j] ==  sum(m.FCCU1[n,'CCU', 'Cooler'] for n in m.Components) * 3.08 * m.SolventCCU[n]  
            elif n in m.Components  and j in  m.CarbonCapture:
                return m.total_chemical_absorber2_needed[n,j] == 0
            else:
                return Constraint.Skip
        m.total_chemical_absorber2_needed_constraint = Constraint(m.Components, m.CarbonCapture, rule=total_chemical_absorber2_needed_rule)

        ## -------------------------------
        # Flow to absorber
        # --------------------------------
        def Absorber2_composition_inflow_rule(m, n, j, k):
            if n in ['CO2','O2','N2','Water','PZ','MDEA','CH4','NH3']  and j == 'CCU' and k == 'Absorber':
                return m.FinAbsorber2[ n, j, k] == m.FCCU1[n,'CCU','Cooler'] + m.total_chemical_absorber2_needed[n,'CCU']
            elif n in m.Components and j in  m.CarbonCapture and k in m.Equipment:
                return m.FinAbsorber2[ n,j, k] == 0 
            else:
                return Constraint.Skip
        m.Absorber2composition_inflow = Constraint(m.Components, m.CarbonCapture, m.Equipment,  rule=Absorber2_composition_inflow_rule)
        # -------------------------------
        # Top absorber
        # --------------------------------
        def Absorber2_top_outflow_rule(m, n, j, k):
            if n in ['CO2','O2','N2','Water','CH4','NH3'] and j == 'CCU' and k == 'Absorber':
                  return m.FoutAbsorber2_top[ n,  j, k]  ==  m.FinAbsorber2[ n,  j, 'Absorber'] * m.RecoveryTopAbsorber2 [n]
            elif n in m.Components and j in  m.CarbonCapture and k in m.Equipment:
                  return m.FoutAbsorber2_top [ n,  j, k]  == 0 
            else:
                  return Constraint.Skip
        m.Absorber2Topflow = Constraint(m.Components, m.CarbonCapture, m.Equipment, rule=Absorber2_top_outflow_rule)
        ## -------------------------------
        # Bottom absorber
        # --------------------------------
        def Absorber2_bottom_outflow_rule(m, n, j, k):
            if n in ['CO2','Water','PZ','MDEA'] and j == 'CCU' and k in ['Absorber','Pump','HE','DT']:
                return m.FoutAbsorber2_bottom[n, j, k] == m.FinAbsorber2[ n,j, 'Absorber']  - m.FoutAbsorber2_top[ n,j, 'Absorber']
            elif n in m.Components and j in  m.CarbonCapture and k in m.Equipment:
                return m.FoutAbsorber2_bottom[n, j, k] == 0 
            else:
                return Constraint.Skip
        m.BottomAbsorber2outflow = Constraint(m.Components, m.CarbonCapture, m.Equipment, rule=Absorber2_bottom_outflow_rule)

        # -------------------------------
        #Distillation 
        #--------------------------------
        #Top Distillation 
        #--------------------------------
        def DT18_top_outflow_rule(m, n, j, k):
            if n in ['CO2','Water']  and j == 'CCU' and k == 'DT':
                return m.FoutDT18_CO2[n, j, k] == m.FoutAbsorber2_bottom[ n,'CCU', 'DT']*m.TopDT18[n]
            elif n in m.Components and j in m.CarbonCapture and k in m.Equipment:
                return m.FoutDT18_CO2[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.TopDT18outflow = Constraint(m.Components, m.CarbonCapture, m.Equipment,  rule=DT18_top_outflow_rule)
        #--------------------------------
        # Bottom Distillation 
        # --------------------------------
        def DT18_bottom_outflow_rule(m, n, j, k):
            if n in ['Water','PZ','MDEA']  and j == 'CCU' and k in ['DT','Cooler']:
                return m.FoutDT18_liquid[n, j, k] == m.FoutAbsorber2_bottom[ n,j,k] - m.FoutDT18_CO2[n,j,k]
            elif n in m.Components and j in m.CarbonCapture and k in m.Equipment:
                return m.FoutDT18_liquid[n, j, k]  == 0 
            else:
                return Constraint.Skip
        m.BottomDT18outflow = Constraint(m.Components, m.CarbonCapture, m.Equipment, rule=DT18_bottom_outflow_rule)
        
        # --------------------------------
        # CO2 compression 
        # --------------------------------
        def CO2_diversion_rule(m, n, j,k ):
            if n == 'CO2' and j =='CCU' and k in ['Comp','Cooler','FlashDrum']:
                return m.CO2_compression[n,j,k] == m.FoutDT18_CO2[ n,'CCU', 'DT'] - m.CO2_stream_Succinic['CO2', 'SuccinicAcidProcess']
            elif n == 'Water' and j =='CCU' and k in ['Comp','Cooler','FlashDrum']:
                return m.CO2_compression[n,j,k] ==  m.FoutDT18_CO2[ n,'CCU', 'DT'] 
            elif n in m.Components and j in m.CarbonCapture and k in m.Equipment:
                  return  m.CO2_compression[n,j,k] == 0   
            else:
                  return Constraint.Skip
        m.CO2_diversion_constraint = Constraint(m.Components, m.CarbonCapture,m.Equipment, rule=CO2_diversion_rule)


 



