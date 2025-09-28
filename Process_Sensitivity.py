import pandas as pd
import numpy as np

# Define parameter ranges
carbon_modes = ['reference', 'moderate', 'strict']
material_cost_multipliers = [-0.3, -0.25, -0.2, -0.15, -0.1, -0.05, 0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
phaseout_factors = [0.5, 0.7, 1.0, 1.3, 1.5]
elasticity_multipliers = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]

# Read base data
data_output = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="output")
data_carbonprice = pd.read_excel('data_cost.xlsx', sheet_name="Carbon Price(CNY per tCO2)")
data_capacity = pd.read_excel('data_capacity.xlsx')
years = np.arange(2025, 2061).tolist()
year_short = np.arange(2025, 2061, 5)

data_output.index = data_output['Year']
y = np.array(data_output.loc[2025:2060, 'production']*10)
y1 = np.array(data_output.loc[2025:2060, 'EAF']*10)
y2 = y - y1

power_factor = np.arange(30, -1, -1) / 30
results_list = []

def phaseout_capacity(capacity, cost, year, phaseout_demand):
    total_capacity = np.sum(capacity[year-1])
    if total_capacity > 0:
        reduction_ratio = phaseout_demand / total_capacity
        capacity[year] = capacity[year-1] * (1 - reduction_ratio)
    else:
        capacity[year] = capacity[year-1]

# Main sensitivity analysis loops
total_iterations = len(carbon_modes) * len(material_cost_multipliers) * len(phaseout_factors) * len(elasticity_multipliers)
current_iteration = 0

for carbon_mode in carbon_modes:
    print(f"Processing carbon mode: {carbon_mode}")
    
    # Read carbon price data
    Price_carbon = np.interp(years, year_short, data_carbonprice[carbon_mode].values)
    
    # Read original cost data
    eaf_cost_original = pd.read_excel(f'outputs/output_cost_{carbon_mode}.xlsx', sheet_name=f"Scrap-EAF-{carbon_mode}")
    bf_cost_original = pd.read_excel(f'outputs/output_cost_{carbon_mode}.xlsx', sheet_name=f"BF-BOF-{carbon_mode}")
    h2_cost_original = pd.read_excel(f'outputs/output_cost_{carbon_mode}.xlsx', sheet_name=f"H2-DRI-EAF-{carbon_mode}")
    ccs_cost_original = pd.read_excel(f'outputs/output_cost_{carbon_mode}.xlsx', sheet_name=f"BF-BOF-CCS-{carbon_mode}")
    
    # Read material cost data
    eaf_material = pd.read_excel('outputs/output_cost_category.xlsx', sheet_name="Scrap-EAF")
    bf_material = pd.read_excel('outputs/output_cost_category.xlsx', sheet_name="BF-BOF")
    h2_material = pd.read_excel('outputs/output_cost_category.xlsx', sheet_name="H2-DRI-EAF")
    ccs_material = pd.read_excel('outputs/output_cost_category.xlsx', sheet_name="BF-BOF-CCS")
    
    for material_multiplier in material_cost_multipliers:
        # Adjust costs with material cost changes
        eaf_cost = eaf_cost_original.copy()
        bf_cost = bf_cost_original.copy()
        h2_cost = h2_cost_original.copy()
        ccs_cost = ccs_cost_original.copy()
        
        for year in years:
            if year in eaf_material.columns:
                eaf_cost[year] = eaf_cost[year] + material_multiplier * eaf_material['Material_Cost']
                bf_cost[year] = bf_cost[year] + material_multiplier * bf_material['Material_Cost']
                h2_cost[year] = h2_cost[year] + material_multiplier * h2_material['Material_Cost']
                ccs_cost[year] = ccs_cost[year] + material_multiplier * ccs_material['Material_Cost']
        
        for phaseout_factor in phaseout_factors:
            for elasticity_multiplier in elasticity_multipliers:
                current_iteration += 1
                print(f"Progress: {current_iteration}/{total_iterations}")
                
                # Set elasticity parameters
                gamma_tech = -3 * elasticity_multiplier
                gamma_province = -6 * elasticity_multiplier
                
                provinces = eaf_cost['Province']
                
                # Initialize production ratio dataframes
                eaf_production_ratio = pd.DataFrame(columns=['Province'] + years)
                bf_production_ratio = pd.DataFrame(columns=['Province'] + years)
                h2_production_ratio = pd.DataFrame(columns=['Province'] + years)
                ccs_production_ratio = pd.DataFrame(columns=['Province'] + years)
                
                eaf_production_ratio['Province'] = provinces
                bf_production_ratio['Province'] = provinces
                h2_production_ratio['Province'] = provinces
                ccs_production_ratio['Province'] = provinces
                
                # Calculate production ratios
                for year in years:
                    cost_weights = (eaf_cost[year] / 1000) ** gamma_province
                    eaf_production_ratio[year] = cost_weights / np.sum(cost_weights)
                    
                    cost_weights = (bf_cost[year] / 1000) ** gamma_province
                    bf_production_ratio[year] = cost_weights / np.sum(cost_weights)
                    
                    cost_weights = (h2_cost[year] / 1000) ** gamma_province
                    h2_production_ratio[year] = cost_weights / np.sum(cost_weights)
                    
                    cost_weights = (ccs_cost[year] / 1000) ** gamma_province
                    ccs_production_ratio[year] = cost_weights / np.sum(cost_weights)
                
                # Initialize result dataframes
                annual_production = pd.DataFrame({'Year': years})
                annual_cost = pd.DataFrame({'Year': years})
                annual_emission = pd.DataFrame({'Year': years})
                
                # Calculate capacity allocation
                ratio = np.power(power_factor, phaseout_factor)
                y3 = y2[5:] * ratio
                y4 = y2[5:] - y3
                y4 = np.concatenate([np.zeros(5), y4])
                y_newly_build = np.diff(y4, prepend=0)
                
                # Initialize capacity data
                eaf_capacity = pd.DataFrame(columns=['Province', 2024] + years)
                bf_capacity = pd.DataFrame(columns=['Province', 2024] + years)
                h2_capacity = pd.DataFrame(columns=['Province', 2024] + years)
                ccs_capacity = pd.DataFrame(columns=['Province', 2024] + years)
                
                eaf_capacity['Province'] = provinces
                bf_capacity['Province'] = provinces
                h2_capacity['Province'] = provinces
                ccs_capacity['Province'] = provinces
                
                eaf_capacity[2024] = data_capacity['EAF Capacity'] * 0.5
                bf_capacity[2024] = data_capacity['BOF Capacity'] * 0.85
                h2_capacity[2024] = 0
                ccs_capacity[2024] = 0
                
                eaf_demand = y1
                bf_demand = np.concatenate([y2[:5], y3])
                
                # Annual calculation loop
                for year in years:
                    eaf_year = eaf_demand[year-2025] - np.sum(eaf_capacity.loc[:, year-1])
                    bf_year = bf_demand[year-2025] - np.sum(bf_capacity.loc[:, year-1])
                    
                    h2_avg_cost = np.sum(h2_production_ratio[year] * h2_cost[year])
                    ccs_avg_cost = np.sum(ccs_production_ratio[year] * ccs_cost[year])
                    
                    h2_weight = (h2_avg_cost / 1000) ** gamma_tech
                    ccs_weight = (ccs_avg_cost / 1000) ** gamma_tech
                    h2_ratio = h2_weight / (h2_weight + ccs_weight)
                    
                    if y_newly_build[year-2025] < 0:
                        h2_year = (1 - h2_ratio) * y_newly_build[year-2025]
                        ccs_year = h2_ratio * y_newly_build[year-2025]
                        phaseout_capacity(h2_capacity, h2_cost, year, -h2_year)
                        phaseout_capacity(ccs_capacity, ccs_cost, year, -ccs_year)
                    else:
                        h2_year = h2_ratio * y_newly_build[year-2025]
                        ccs_year = (1 - h2_ratio) * y_newly_build[year-2025]
                        h2_capacity[year] = h2_capacity[year-1] + h2_year * h2_production_ratio[year]
                        ccs_capacity[year] = ccs_capacity[year-1] + ccs_year * ccs_production_ratio[year]
                    
                    if eaf_year >= 0:
                        eaf_capacity[year] = eaf_capacity[year-1] + eaf_year * eaf_production_ratio[year]
                    else:
                        phaseout_capacity(eaf_capacity, eaf_cost, year, -eaf_year)
                    
                    if bf_year >= 0:
                        bf_capacity[year] = bf_capacity[year-1] + bf_year * bf_production_ratio[year]
                    else:
                        phaseout_capacity(bf_capacity, bf_cost, year, -bf_year)
                    
                    annual_production.loc[year-2025, 'EAF'] = np.sum(eaf_capacity[year])
                    annual_production.loc[year-2025, 'BF'] = np.sum(bf_capacity[year])
                    annual_production.loc[year-2025, 'H2'] = np.sum(h2_capacity[year])
                    annual_production.loc[year-2025, 'CCS'] = np.sum(ccs_capacity[year])
                    
                    annual_cost.loc[year-2025, 'EAF'] = np.sum(eaf_capacity[year] * eaf_cost[year])
                    annual_cost.loc[year-2025, 'BF'] = np.sum(bf_capacity[year] * bf_cost[year])
                    annual_cost.loc[year-2025, 'H2'] = np.sum(h2_capacity[year] * h2_cost[year])
                    annual_cost.loc[year-2025, 'CCS'] = np.sum(ccs_capacity[year] * ccs_cost[year])
                    
                    annual_emission.loc[year-2025, 'EAF'] = eaf_demand[year-2025] * 0.08
                    annual_emission.loc[year-2025, 'BF'] = bf_demand[year-2025] * 2.0
                    annual_emission.loc[year-2025, 'H2'] = np.sum(h2_capacity[year]) * 0.1
                    annual_emission.loc[year-2025, 'CCS'] = np.sum(ccs_capacity[year]) * 1.1
                
                # Extract results for target years
                target_years_index = [2030-2025, 2040-2025, 2050-2025, 2060-2025]
                
                total_cost_2030 = annual_cost.iloc[target_years_index[0], 1:].sum()
                total_cost_2040 = annual_cost.iloc[target_years_index[1], 1:].sum()
                total_cost_2050 = annual_cost.iloc[target_years_index[2], 1:].sum()
                total_cost_2060 = annual_cost.iloc[target_years_index[3], 1:].sum()
                
                total_emission_2030 = annual_emission.iloc[target_years_index[0], 1:].sum()
                total_emission_2040 = annual_emission.iloc[target_years_index[1], 1:].sum()
                total_emission_2050 = annual_emission.iloc[target_years_index[2], 1:].sum()
                total_emission_2060 = annual_emission.iloc[target_years_index[3], 1:].sum()
                
                # Store results
                result_row = {
                    'carbon_mode': carbon_mode,
                    'material_cost_multiplier': material_multiplier,
                    'phaseout_factor': phaseout_factor,
                    'elasticity_multiplier': elasticity_multiplier,
                    'H2_2030': annual_production.iloc[target_years_index[0]]['H2'],
                    'H2_2040': annual_production.iloc[target_years_index[1]]['H2'],
                    'H2_2050': annual_production.iloc[target_years_index[2]]['H2'],
                    'H2_2060': annual_production.iloc[target_years_index[3]]['H2'],
                    'CCS_2030': annual_production.iloc[target_years_index[0]]['CCS'],
                    'CCS_2040': annual_production.iloc[target_years_index[1]]['CCS'],
                    'CCS_2050': annual_production.iloc[target_years_index[2]]['CCS'],
                    'CCS_2060': annual_production.iloc[target_years_index[3]]['CCS'],
                    'Cost_2030': total_cost_2030,
                    'Cost_2040': total_cost_2040,
                    'Cost_2050': total_cost_2050,
                    'Cost_2060': total_cost_2060,
                    'Emission_2030': total_emission_2030,
                    'Emission_2040': total_emission_2040,
                    'Emission_2050': total_emission_2050,
                    'Emission_2060': total_emission_2060
                }
                
                results_list.append(result_row)

# Save results
results_df = pd.DataFrame(results_list)
results_df.to_excel('outputs/output_sensitivity.xlsx', index=False)