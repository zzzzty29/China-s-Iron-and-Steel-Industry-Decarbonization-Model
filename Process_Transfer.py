import pandas as pd
import numpy as np

#calculate
data_output = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="output")
years = np.arange(2025, 2061).tolist()
years1 = np.arange(2025, 2031, 5).tolist()
years2 = np.arange(2030, 2061, 5).tolist()

data_output.index = data_output['Year']
y = np.array(data_output.loc[2025:2060, 'production']*10) # total thousand ton
y1 = np.array(data_output.loc[2025:2060, 'EAF']*10) # EAF
y2 = y - y1 # BOF & other

year_short = np.arange(2025, 2061, 5)
carbon_modes = ['reference', 'moderate', 'strict']
phaseout_factor = 1
power_factor = np.arange(30, -1, -1) / 30
gamma_tech = -3
gamma_province = -6

def phaseout_capacity(capacity, cost, year, phaseout_demand):
    total_capacity = np.sum(capacity[year-1])
    reduction_ratio = phaseout_demand / total_capacity
    capacity[year] = capacity[year-1] * (1 - reduction_ratio)

for i in range(len(carbon_modes)):
    carbon_mode = carbon_modes[i]
    
    # with carbon price
    eaf_cost = pd.read_excel(f'outputs/output_cost_{carbon_mode}.xlsx', sheet_name=f"Scrap-EAF-{carbon_mode}")
    bf_cost = pd.read_excel(f'outputs/output_cost_{carbon_mode}.xlsx', sheet_name=f"BF-BOF-{carbon_mode}")
    h2_cost = pd.read_excel(f'outputs/output_cost_{carbon_mode}.xlsx', sheet_name=f"H2-DRI-EAF-{carbon_mode}")
    ccs_cost = pd.read_excel(f'outputs/output_cost_{carbon_mode}.xlsx', sheet_name=f"BF-BOF-CCS-{carbon_mode}")

    provinces = eaf_cost['Province']
    eaf_production_ratio = pd.DataFrame(columns=['Province'] + years)
    bf_production_ratio = pd.DataFrame(columns=['Province'] + years)
    h2_production_ratio = pd.DataFrame(columns=['Province'] + years)
    ccs_production_ratio = pd.DataFrame(columns=['Province'] + years)
    eaf_production_ratio['Province'] = provinces
    bf_production_ratio['Province'] = provinces
    h2_production_ratio['Province'] = provinces
    ccs_production_ratio['Province'] = provinces

    for year in years:
        cost_weights = (eaf_cost[year] / 1000) ** gamma_province
        eaf_production_ratio[year] = cost_weights / np.sum(cost_weights)
        
        cost_weights = (bf_cost[year] / 1000) ** gamma_province
        bf_production_ratio[year] = cost_weights / np.sum(cost_weights)
        
        cost_weights = (h2_cost[year] / 1000) ** gamma_province
        h2_production_ratio[year] = cost_weights / np.sum(cost_weights)
        
        cost_weights = (ccs_cost[year] / 1000) ** gamma_province
        ccs_production_ratio[year] = cost_weights / np.sum(cost_weights)

    annual_production = pd.DataFrame({'Year': years})
    annual_cost = pd.DataFrame({'Year': years}) 
    annual_emission = pd.DataFrame({'Year': years})
    capacity_final = pd.DataFrame({'Province': provinces})

    ratio = np.power(power_factor, phaseout_factor)
    y3 = y2[5:] * ratio # BOF
    y4 = y2[5:] - y3 # H2-DRI-EAF + BF-BOF-CCS
    y4 = np.concatenate([np.zeros(5), y4]) # add 0 for years before 2030
    y_newly_build = np.diff(y4, prepend=0) # calculate the annual change in H2-DRI-EAF + BF-BOF-CCS

    data_capacity = pd.read_excel('data_capacity.xlsx')
    eaf_capacity = pd.DataFrame(columns=['Province', 2024] + years)
    bf_capacity = pd.DataFrame(columns=['Province', 2024] + years)
    h2_capacity = pd.DataFrame(columns=['Province', 2024] + years)
    ccs_capacity = pd.DataFrame(columns=['Province', 2024] + years)
    eaf_capacity['Province'] = provinces
    bf_capacity['Province'] = provinces
    h2_capacity['Province'] = provinces
    ccs_capacity['Province'] = provinces
    eaf_capacity[2024] = data_capacity['EAF Capacity'] * 0.5 # 50% of the total capacity
    bf_capacity[2024] = data_capacity['BOF Capacity'] * 0.85 # 85% of the total capacity
    h2_capacity[2024] = 0
    ccs_capacity[2024] = 0

    eaf_demand = y1
    bf_demand = np.concatenate([y2[:5], y3])
    for year in years:
        eaf_year = eaf_demand[year-2025] - np.sum(eaf_capacity.loc[:, year-1])
        bf_year = bf_demand[year-2025] - np.sum(bf_capacity.loc[:, year-1])

        h2_avg_cost = np.sum(h2_production_ratio[year] * h2_cost[year])
        ccs_avg_cost = np.sum(ccs_production_ratio[year] * ccs_cost[year])

        h2_weight = (h2_avg_cost / 1000) ** gamma_tech
        ccs_weight = (ccs_avg_cost / 1000) ** gamma_tech
        h2_ratio = h2_weight / (h2_weight + ccs_weight)

        if y_newly_build[year-2025] < 0:
            h2_year = (1 - h2_ratio) * y_newly_build[year-2025]  # H2-DRI-EAF production in this year
            ccs_year = h2_ratio * y_newly_build[year-2025]  # BF-BOF-CCS production in this year
            phaseout_capacity(h2_capacity, h2_cost, year, -h2_year)  # phase out H2-DRI-EAF capacity
            phaseout_capacity(ccs_capacity, ccs_cost, year, -ccs_year)  # phase out BF-BOF-CCS capacity
        else:
            h2_year = h2_ratio * y_newly_build[year-2025]  # H2-DRI-EAF production in this year
            ccs_year = (1 - h2_ratio) * y_newly_build[year-2025]  # BF-BOF-CCS production in this year
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
  
    capacity_final['EAF'] = eaf_capacity.loc[:, 2060]
    capacity_final['BF'] = bf_capacity.loc[:, 2060] 
    capacity_final['H2'] = h2_capacity.loc[:, 2060]
    capacity_final['CCS'] = ccs_capacity.loc[:, 2060]

    if i == 0:
        output_sheets = {}
    
    output_sheets[f'{carbon_mode}_production'] = annual_production.copy()
    output_sheets[f'{carbon_mode}_cost'] = annual_cost.copy() 
    output_sheets[f'{carbon_mode}_emission'] = annual_emission.copy()
    output_sheets[f'{carbon_mode}_capacity'] = capacity_final.copy()

with pd.ExcelWriter('outputs/output_basic.xlsx') as writer:
    for sheet_name, data in output_sheets.items():
        data.to_excel(writer, sheet_name=sheet_name, index=False)