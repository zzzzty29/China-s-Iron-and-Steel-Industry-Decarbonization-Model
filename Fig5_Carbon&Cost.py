import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read data
output_data = {}
carbon_modes = ['reference', 'moderate', 'strict']

for carbon_mode in carbon_modes:
    output_data[f'{carbon_mode}_production'] = pd.read_excel('outputs/output_basic.xlsx', sheet_name=f'{carbon_mode}_production')
    output_data[f'{carbon_mode}_cost'] = pd.read_excel('outputs/output_basic.xlsx', sheet_name=f'{carbon_mode}_cost')
    output_data[f'{carbon_mode}_emission'] = pd.read_excel('outputs/output_basic.xlsx', sheet_name=f'{carbon_mode}_emission')

years = np.arange(2025, 2061)

# plot settings
plt.rcParams['font.family'] = 'Arial'
fig = plt.figure(figsize=(28, 12))
grid = plt.GridSpec(18, 30, wspace=0.3, hspace=0.3, top=0.94, bottom=0.08)

years_ticks = np.arange(25, 61, 5).tolist() * 3
years_ticks = [f"'{year}" for year in years_ticks]
years_positions = [x + 50 * j for j in range(3) for x in np.arange(0, 36, 5)]

colors_tech = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
colors_emission = ['#17becf', '#ff7f0e', '#2ca02c', '#d62728']

# plot a - production
ax = plt.subplot(grid[0:5, :])
for j, carbon_mode in enumerate(carbon_modes):
    production_df = output_data[f'{carbon_mode}_production']
    x_pos = np.arange(0, 36, 5) + 50 * j
    
    bar1 = plt.bar(x_pos, production_df['EAF'].iloc[::5]/1000, label='Scrap-EAF' if j==0 else "", 
                   color=colors_tech[0], alpha=0.8, width=3, linewidth=0.5, edgecolor='k')
    bar2 = plt.bar(x_pos, production_df['BF'].iloc[::5]/1000, label='BF-BOF' if j==0 else "", 
                   color=colors_tech[1], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=production_df['EAF'].iloc[::5]/1000)
    bar3 = plt.bar(x_pos, production_df['H2'].iloc[::5]/1000, label='H2-DRI-EAF' if j==0 else "", 
                   color=colors_tech[2], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=(production_df['EAF'].iloc[::5] + production_df['BF'].iloc[::5])/1000)
    bar4 = plt.bar(x_pos, production_df['CCS'].iloc[::5]/1000, label='BF-BOF-CCS' if j==0 else "", 
                   color=colors_tech[3], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=(production_df['EAF'].iloc[::5] + production_df['BF'].iloc[::5] + production_df['H2'].iloc[::5])/1000)
    
    plt.ylim(0, 1000)
    plt.text(17.5 + 50 * j, plt.ylim()[0] - (plt.ylim()[1] - plt.ylim()[0])*0.12, 'Year', fontsize=12, ha='center')
    plt.text(17.5 + 50 * j, plt.ylim()[0] - (plt.ylim()[1] - plt.ylim()[0])*0.18, f"{carbon_mode}", fontsize=12, fontweight='bold', ha='center')

plt.ylabel('Production (Million tons)', fontsize=12)
plt.xticks(years_positions, years_ticks, fontsize=10)
plt.xlim(-10, 145)
plt.text(-8, plt.ylim()[1]*1.02, "a.", fontsize=14, fontweight='bold')

production_handles = [bar1, bar2, bar3, bar4]
production_labels = ['Scrap-EAF', 'BF-BOF', 'H2-DRI-EAF', 'BF-BOF-CCS']

# plot b - cost
ax = plt.subplot(grid[6:11, :])
for j, carbon_mode in enumerate(carbon_modes):
    cost_df = output_data[f'{carbon_mode}_cost']
    x_pos = np.arange(0, 36, 5) + 50 * j
    
    bar1 = plt.bar(x_pos, cost_df['EAF'].iloc[::5]/1e9, label='Scrap-EAF' if j==0 else "", 
                   color=colors_tech[0], alpha=0.8, width=3, linewidth=0.5, edgecolor='k')
    bar2 = plt.bar(x_pos, cost_df['BF'].iloc[::5]/1e9, label='BF-BOF' if j==0 else "", 
                   color=colors_tech[1], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=cost_df['EAF'].iloc[::5]/1e9)
    bar3 = plt.bar(x_pos, cost_df['H2'].iloc[::5]/1e9, label='H2-DRI-EAF' if j==0 else "", 
                   color=colors_tech[2], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=(cost_df['EAF'].iloc[::5] + cost_df['BF'].iloc[::5])/1e9)
    bar4 = plt.bar(x_pos, cost_df['CCS'].iloc[::5]/1e9, label='BF-BOF-CCS' if j==0 else "", 
                   color=colors_tech[3], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=(cost_df['EAF'].iloc[::5] + cost_df['BF'].iloc[::5] + cost_df['H2'].iloc[::5])/1e9)
    
    plt.ylim(0, 4)
    plt.text(17.5 + 50 * j, plt.ylim()[0] - (plt.ylim()[1] - plt.ylim()[0])*0.12, 'Year', fontsize=12, ha='center')
    plt.text(17.5 + 50 * j, plt.ylim()[0] - (plt.ylim()[1] - plt.ylim()[0])*0.18, f"{carbon_mode}", fontsize=12, fontweight='bold', ha='center')

plt.ylabel('Total Production Cost (Billion CNY)', fontsize=12)
plt.xticks(years_positions, years_ticks, fontsize=10)
plt.xlim(-10, 145)
plt.text(-8, plt.ylim()[1]*1.02, "b.", fontsize=14, fontweight='bold')

cost_handles = [bar1, bar2, bar3, bar4]
cost_labels = ['Scrap-EAF', 'BF-BOF', 'H2-DRI-EAF', 'BF-BOF-CCS']

# plot c - emission
ax = plt.subplot(grid[12:17, :])
for j, carbon_mode in enumerate(carbon_modes):
    emission_df = output_data[f'{carbon_mode}_emission']
    x_pos = np.arange(0, 36, 5) + 50 * j
    
    bar1 = plt.bar(x_pos, emission_df['EAF'].iloc[::5]/1e6, label='Scrap-EAF' if j==0 else "", 
                   color=colors_tech[0], alpha=0.8, width=3, linewidth=0.5, edgecolor='k')
    bar2 = plt.bar(x_pos, emission_df['BF'].iloc[::5]/1e6, label='BF-BOF' if j==0 else "", 
                   color=colors_tech[1], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=emission_df['EAF'].iloc[::5]/1e6)
    bar3 = plt.bar(x_pos, emission_df['H2'].iloc[::5]/1e6, label='H2-DRI-EAF' if j==0 else "", 
                   color=colors_tech[2], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=(emission_df['EAF'].iloc[::5] + emission_df['BF'].iloc[::5])/1e6)
    bar4 = plt.bar(x_pos, emission_df['CCS'].iloc[::5]/1e6, label='BF-BOF-CCS' if j==0 else "", 
                   color=colors_tech[3], alpha=0.8, width=3, linewidth=0.5, edgecolor='k',
                   bottom=(emission_df['EAF'].iloc[::5] + emission_df['BF'].iloc[::5] + emission_df['H2'].iloc[::5])/1e6)
    
    plt.ylim(0, 2)
    plt.text(17.5 + 50 * j, plt.ylim()[0] - (plt.ylim()[1] - plt.ylim()[0])*0.12, 'Year', fontsize=12, ha='center')
    plt.text(17.5 + 50 * j, plt.ylim()[0] - (plt.ylim()[1] - plt.ylim()[0])*0.18, f"{carbon_mode}", fontsize=12, fontweight='bold', ha='center')

plt.ylabel('Total Emission (Million tCO2)', fontsize=12)
plt.xticks(years_positions, years_ticks, fontsize=10)
plt.xlim(-10, 145)
plt.text(-8, plt.ylim()[1]*1.02, "c.", fontsize=14, fontweight='bold')

# legend
emission_handles = [bar1, bar2, bar3, bar4]
emission_labels = ['Scrap-EAF', 'BF-BOF', 'H2-DRI-EAF', 'BF-BOF-CCS']

fig.legend(production_handles,
          production_labels,
          loc='lower center', bbox_to_anchor=(0.5, 0.05), ncol=4, fontsize=11, frameon=False)

plt.savefig('figs/Fig5.png', dpi=600, bbox_inches='tight')
#plt.show()