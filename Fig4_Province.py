# Fig4 code
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# read data
output_data = pd.read_excel('outputs/output_basic.xlsx', sheet_name=None)

# read initial capacity from original data file
data_capacity_2024 = pd.read_excel('data_capacity.xlsx')
provinces = data_capacity_2024['Province'].values
initial_eaf = data_capacity_2024['EAF Capacity'] * 0.5
initial_bf = data_capacity_2024['BOF Capacity'] * 0.85

# set parameters
carbon_modes = ['reference', 'moderate', 'strict']

# calculate capacity ratios - including total capacity ratio
capacity_ratio_new = np.zeros((len(provinces), len(carbon_modes) * 4))  # 4 columns: EAF, CCS, H2, Total

for i, carbon_mode in enumerate(carbon_modes):
    capacity_data = output_data[f'{carbon_mode}_capacity']
    
    # get final capacity by technology
    eaf_final = capacity_data['EAF'].values
    ccs_final = capacity_data['CCS'].values  
    h2_final = capacity_data['H2'].values
    total_final = eaf_final + ccs_final + h2_final
    
    # calculate technology shares - each province's share within each technology
    eaf_total = np.sum(eaf_final)
    ccs_total = np.sum(ccs_final)
    h2_total = np.sum(h2_final)
    national_total = np.sum(total_final)
    
    capacity_ratio_new[:, i*4] = eaf_final / eaf_total * 100            # EAF share
    capacity_ratio_new[:, i*4+1] = ccs_final / ccs_total * 100          # CCS share
    capacity_ratio_new[:, i*4+2] = h2_final / h2_total * 100            # H2 share
    capacity_ratio_new[:, i*4+3] = total_final / national_total * 100   # Total share

# calculate 2024 initial capacity ratios
bar_eaf = initial_eaf / 25000  # normalized for bar chart
bar_bf = initial_bf / 25000

# create figure
plt.rcParams['font.family'] = 'Arial'
plt.figure(figsize=(24, 12))

# create x labels
x_label = ['EAF', 'CCS', 'H2', 'Total'] * 3

colors = ['#F0F0FF', "#B8F5CD", "#FFE066"]
cmap = LinearSegmentedColormap.from_list("custom_green", colors, N=256)
heatmap = sns.heatmap(capacity_ratio_new, 
                     cbar=True, vmin=1, vmax=7, 
                     cmap=cmap, 
                     cbar_kws={"location": "left", "aspect": 60, "pad": 0.08}, 
                     fmt=".2f", annot=True, annot_kws={"size": 9}, 
                     xticklabels=x_label, 
                     yticklabels=provinces, 
                     linewidths=0.5)

plt.tick_params(axis='both', which='both', length=0)
colorbar = heatmap.collections[0].colorbar
colorbar.set_ticks([i for i in range(1, 8)])
colorbar.set_ticklabels(['<1%'] + [f'{i}%' for i in range(2, 7)] + ['>7%'])
colorbar.set_label("Crude Steel Production Ratio (%)", fontsize=12, weight='bold')
colorbar.outline.set_linewidth(1)


# add separator lines
plt.vlines([4, 8], 0, len(provinces), color='black', linestyle='-', linewidth=2)

# add scenario labels
plt.text(2, len(provinces)+1, 'reference', fontsize=12, weight='bold', ha='center', va='center')
plt.text(6, len(provinces)+1, 'moderate', fontsize=12, weight='bold', ha='center', va='center')
plt.text(10, len(provinces)+1, 'strict', fontsize=12, weight='bold', ha='center', va='center')


# plot 2024 capacity bars directly on the right
plt.barh(np.arange(len(provinces))+0.5, bar_eaf, left=12.2, color="steelblue", edgecolor="black", alpha=0.7, label='Scrap-EAF')
plt.barh(np.arange(len(provinces))+0.5, bar_bf, left=12.2+bar_eaf, color="orange", edgecolor="black", alpha=0.7, label='BF-BOF')

# add separator line
plt.vlines(12.2, 0, len(provinces), color='black', linestyle='-', linewidth=1)
plt.hlines(len(provinces), 12.2, 22.2, color='black', linestyle='-', linewidth=2)

# set limits and ticks
plt.xlim(0, 24)
x_tick_positions = np.concatenate((np.arange(12)+0.5, np.arange(0, 11, 2)+12.2))
x_tick_labels = x_label + ['0', '50', '100', '150', '200', '250']
plt.xticks(x_tick_positions, x_tick_labels)
plt.yticks(np.arange(len(provinces))+0.5, provinces, weight='bold')

# add title for 2024 capacity
plt.text(17.2, len(provinces)+1, 'Provincial Crude Steel Capacity in 2024(Mt per year)', 
         ha='center', va='center', fontsize=12, weight='bold')

# add legend
plt.legend(loc='lower right', frameon=False, fontsize=12)

# Output 2060 provincial ratios and capacities as text
for i, mode in enumerate(carbon_modes):
    capacity_data = output_data[f'{mode}_capacity']
    eaf_final = capacity_data['EAF'].values / 1000  # Convert to Mt
    ccs_final = capacity_data['CCS'].values / 1000  # Convert to Mt
    h2_final = capacity_data['H2'].values / 1000    # Convert to Mt
    total_final = eaf_final + ccs_final + h2_final
    
    print(f"\n{mode.capitalize()} scenario 2060 provincial ratios and capacities:")
    print("Province, EAF%(Mt), CCS%(Mt), H2%(Mt), Total%(Mt)")
    for j, province in enumerate(provinces):
        ratios = capacity_ratio_new[j, i*4:(i+1)*4]
        print(f"{province}, {ratios[0]:.1f}%({eaf_final[j]:.1f}Mt), {ratios[1]:.1f}%({ccs_final[j]:.1f}Mt), {ratios[2]:.1f}%({h2_final[j]:.1f}Mt), {ratios[3]:.1f}%({total_final[j]:.1f}Mt)")

# save figure
plt.savefig('figs/Fig4.png', dpi=600, bbox_inches='tight')
plt.show()