import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap


plt.figure(figsize=(20, 16))
plt.rcParams['font.family'] = 'Arial'
carbon_modes = ['reference', 'moderate', 'strict']

cost_all = pd.DataFrame()
intensity_all = pd.DataFrame()

for i in range(len(carbon_modes)):
    carbon_mode = carbon_modes[i]
    # electricity cost
    data_cost = pd.read_excel("data_electricity.xlsx", sheet_name=f'{carbon_mode}_cost')
    provinces = data_cost['Provinces']
    years = np.arange(2025, 2061, 5).tolist()
    data_cost = data_cost.set_index('Provinces').loc[provinces, years]
    cost_all = pd.concat([cost_all, data_cost], axis=1)
    cost_all[f'mask_{i}'] = np.nan  # add empty column for spacing

# plot
colors = ["#20F982", "#E8FB7E", "#F9CB00"]  # Green to Red
cmap = sns.blend_palette(colors, as_cmap=True, n_colors=256)
years_plt = (years + ['']) * 3  # Extend years for spacing


heatmap = sns.heatmap(cost_all, cbar=True, vmin=0.2, vmax=0.7, cmap=cmap, cbar_kws={"location": "left", "aspect": 40, "pad": 0.08}, fmt=".2f", annot=True, annot_kws={"size": 9}, xticklabels=years, yticklabels=provinces, linewidths=0.5)
plt.tick_params(axis='both', which='both', length=0)
plt.xticks(np.arange(len(years_plt))+0.5, years_plt)
plt.yticks(np.arange(len(provinces))+0.5, provinces, weight='bold')
plt.ylabel('')
plt.text(4, 32, 'Reference', fontsize=12, weight='bold',ha='center', va='center')
plt.text(13, 32, 'Moderate', fontsize=12, weight='bold', ha='center', va='center')
plt.text(22, 32, 'Strict', fontsize=12, weight='bold', ha='center', va='center')
colorbar = heatmap.collections[0].colorbar
colorbar.set_ticks([0.2 + i * 0.1 for i in range(6)])  # Set ticks for colorbar
colorbar.set_ticklabels([f'{0.2 + i * 0.1:.1f}' for i in range(6)])  # Set labels for colorbar
colorbar.set_label("Electricity Cost (CNY/kWh)", fontsize=12, weight='bold')
colorbar.outline.set_linewidth(1)



plt.savefig('figs/FigS3.png', dpi=600, bbox_inches='tight')
