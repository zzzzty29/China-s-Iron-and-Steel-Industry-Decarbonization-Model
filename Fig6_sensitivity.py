import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Read sensitivity analysis results
df = pd.read_excel('outputs/output_sensitivity.xlsx')

# Convert units
# Production: divide by 1000 (million ton)
h2_cols = ['H2_2030', 'H2_2040', 'H2_2050', 'H2_2060']
ccs_cols = ['CCS_2030', 'CCS_2040', 'CCS_2050', 'CCS_2060']
for col in h2_cols + ccs_cols:
    df[col] = df[col] / 1000

# Emissions: divide by 1e6 (million ton)
emission_cols = ['Emission_2030', 'Emission_2040', 'Emission_2050', 'Emission_2060']
for col in emission_cols:
    df[col] = df[col] / 1e6

# Cost: divide by 1e9 (billion CNY)
cost_cols = ['Cost_2030', 'Cost_2040', 'Cost_2050', 'Cost_2060']
for col in cost_cols:
    df[col] = df[col] / 1e9

# Set up the plot with better spacing
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
plt.subplots_adjust(hspace=0.35, wspace=0.3, top=0.94, bottom=0.1, left=0.08, right=0.96)

# Define colors for different categories
carbon_colors = {'reference': '#1f77b4', 'moderate': '#ff7f0e', 'strict': '#2ca02c'}
phaseout_colors = {0.5: '#d62728', 0.7: '#9467bd', 1.0: '#8c564b', 1.3: '#e377c2', 1.5: '#7f7f7f'}

# Boxplot properties for thinner black lines
boxprops = dict(linewidth=1.5, color='black')
whiskerprops = dict(linewidth=1.5, color='black')
capprops = dict(linewidth=1.5, color='black')
medianprops = dict(linewidth=1.5, color='black')

# Plot a: Carbon scenario vs CCS production
ax = axes[0, 0]
years = [2030, 2040, 2050, 2060]

# 2030 - all scenarios
ccs_2030_all = df['CCS_2030'].values
bp1 = ax.boxplot([ccs_2030_all], positions=[0], widths=0.6, patch_artist=True,
                 boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
bp1['boxes'][0].set_facecolor('lightgray')

# Collect legend handles and labels
handles_a = [bp1['boxes'][0]]
labels_a = ['All scenarios']

# 2040, 2050, 2060 - by carbon scenario
x_positions = []
for i, year in enumerate([2040, 2050, 2060]):
    col = ccs_cols[i+1]
    box_data = []
    colors = []
    scenarios = ['reference', 'moderate', 'strict']
    for scenario in scenarios:
        data = df[df['carbon_mode'] == scenario][col].values
        box_data.append(data)
        colors.append(carbon_colors[scenario])
    
    # Calculate center position for this year
    center_pos = 2.2 + i * 3
    positions = [center_pos - 0.8, center_pos, center_pos + 0.8]
    x_positions.append(center_pos)
    
    bp = ax.boxplot(box_data, positions=positions, widths=0.6, patch_artist=True,
                    boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
    for j, (patch, color) in enumerate(zip(bp['boxes'], colors)):
        patch.set_facecolor(color)
        if i == 0:  # Only add to legend once
            handles_a.append(patch)
            labels_a.append(scenarios[j].capitalize())

ax.set_xticks([0] + x_positions)
ax.set_xticklabels(['2030\n(All scenarios)', '2040', '2050', '2060'])
ax.set_ylabel('BF-BOF-CCS Production\n(million t-steel)')
ax.legend(handles_a, labels_a, loc='upper left', frameon=False)
ax.text(-2, ax.get_ylim()[1] + 0.02*(ax.get_ylim()[1] - ax.get_ylim()[0]), "a.", fontsize=14, fontweight='bold')

# Plot b: Phaseout factor vs CCS production
ax = axes[1, 0]

# 2030 - all scenarios
bp1 = ax.boxplot([ccs_2030_all], positions=[0], widths=0.6, patch_artist=True,
                 boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
bp1['boxes'][0].set_facecolor('lightgray')

handles_b = [bp1['boxes'][0]]
labels_b = ['All scenarios']

# 2040, 2050, 2060 - by phaseout factor
x_positions = []
phaseout_values = sorted(df['phaseout_factor'].unique())
for i, year in enumerate([2040, 2050, 2060]):
    col = ccs_cols[i+1]
    box_data = []
    colors = []
    for pf in phaseout_values:
        data = df[df['phaseout_factor'] == pf][col].values
        box_data.append(data)
        colors.append(phaseout_colors[pf])
    
    # Calculate center position for this year
    center_pos = 2.6 + i * 4.4
    half_width = (len(phaseout_values) - 1) * 0.4
    positions = [center_pos - half_width + j*0.8 for j in range(len(phaseout_values))]
    x_positions.append(center_pos)
    
    bp = ax.boxplot(box_data, positions=positions, widths=0.6, patch_artist=True,
                    boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
    for j, (patch, color) in enumerate(zip(bp['boxes'], colors)):
        patch.set_facecolor(color)
        if i == 0:  # Only add to legend once
            handles_b.append(patch)
            labels_b.append(f'PF={phaseout_values[j]}')

ax.set_xticks([0] + x_positions)
ax.set_xticklabels(['2030\n(All scenarios)', '2040', '2050', '2060'])
ax.set_ylabel('BF-BOF-CCS Production\n(million t-steel)')
ax.legend(handles_b, labels_b, loc='upper left', frameon=False)
ax.text(-2, ax.get_ylim()[1] + 0.02*(ax.get_ylim()[1] - ax.get_ylim()[0]), "b.", fontsize=14, fontweight='bold')

# Plot c: Carbon scenario vs H2 production
ax = axes[0, 1]

# 2030 - all scenarios
h2_2030_all = df['H2_2030'].values
bp1 = ax.boxplot([h2_2030_all], positions=[0], widths=0.6, patch_artist=True,
                 boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
bp1['boxes'][0].set_facecolor('lightgray')

handles_c = [bp1['boxes'][0]]
labels_c = ['All scenarios']

# 2040, 2050, 2060 - by carbon scenario
x_positions = []
for i, year in enumerate([2040, 2050, 2060]):
    col = h2_cols[i+1]
    box_data = []
    colors = []
    scenarios = ['reference', 'moderate', 'strict']
    for scenario in scenarios:
        data = df[df['carbon_mode'] == scenario][col].values
        box_data.append(data)
        colors.append(carbon_colors[scenario])
    
    center_pos = 2.2 + i * 3
    positions = [center_pos - 0.8, center_pos, center_pos + 0.8]
    x_positions.append(center_pos)
    
    bp = ax.boxplot(box_data, positions=positions, widths=0.6, patch_artist=True,
                    boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
    for j, (patch, color) in enumerate(zip(bp['boxes'], colors)):
        patch.set_facecolor(color)
        if i == 0:
            handles_c.append(patch)
            labels_c.append(scenarios[j].capitalize())

ax.set_xticks([0] + x_positions)
ax.set_xticklabels(['2030\n(All scenarios)', '2040', '2050', '2060'])
ax.set_ylabel('H2-DRI-EAF Production\n(million t-steel)')
ax.legend(handles_c, labels_c, loc='upper left', frameon=False)
ax.text(-2, ax.get_ylim()[1] + 0.02*(ax.get_ylim()[1] - ax.get_ylim()[0]), "c.", fontsize=14, fontweight='bold')

# Plot d: Phaseout factor vs H2 production
ax = axes[1, 1]

# 2030 - all scenarios
bp1 = ax.boxplot([h2_2030_all], positions=[0], widths=0.6, patch_artist=True,
                 boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
bp1['boxes'][0].set_facecolor('lightgray')

handles_d = [bp1['boxes'][0]]
labels_d = ['All scenarios']

# 2040, 2050, 2060 - by phaseout factor
x_positions = []
for i, year in enumerate([2040, 2050, 2060]):
    col = h2_cols[i+1]
    box_data = []
    colors = []
    for pf in phaseout_values:
        data = df[df['phaseout_factor'] == pf][col].values
        box_data.append(data)
        colors.append(phaseout_colors[pf])
    
    center_pos = 2.6 + i * 4.4
    half_width = (len(phaseout_values) - 1) * 0.4
    positions = [center_pos - half_width + j*0.8 for j in range(len(phaseout_values))]
    x_positions.append(center_pos)
    
    bp = ax.boxplot(box_data, positions=positions, widths=0.6, patch_artist=True,
                    boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
    for j, (patch, color) in enumerate(zip(bp['boxes'], colors)):
        patch.set_facecolor(color)
        if i == 0:
            handles_d.append(patch)
            labels_d.append(f'PF={phaseout_values[j]}')

ax.set_xticks([0] + x_positions)
ax.set_xticklabels(['2030\n(All scenarios)', '2040', '2050', '2060'])
ax.set_ylabel('H2-DRI-EAF Production\n(million t-steel)')
ax.legend(handles_d, labels_d, loc='upper left', frameon=False)
ax.text(-2, ax.get_ylim()[1] + 0.02*(ax.get_ylim()[1] - ax.get_ylim()[0]), "d.", fontsize=14, fontweight='bold')

# Plot e: Phaseout factor vs Carbon emissions
ax = axes[0, 2]

# 2030 - all scenarios
emission_2030_all = df['Emission_2030'].values
bp1 = ax.boxplot([emission_2030_all], positions=[0], widths=0.6, patch_artist=True,
                 boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
bp1['boxes'][0].set_facecolor('lightgray')

handles_e = [bp1['boxes'][0]]
labels_e = ['All scenarios']

# 2040, 2050, 2060 - by phaseout factor
x_positions = []
for i, year in enumerate([2040, 2050, 2060]):
    col = emission_cols[i+1]
    box_data = []
    colors = []
    for pf in phaseout_values:
        data = df[df['phaseout_factor'] == pf][col].values
        box_data.append(data)
        colors.append(phaseout_colors[pf])
    
    center_pos = 2.6 + i * 4.4
    half_width = (len(phaseout_values) - 1) * 0.4
    positions = [center_pos - half_width + j*0.8 for j in range(len(phaseout_values))]
    x_positions.append(center_pos)
    
    bp = ax.boxplot(box_data, positions=positions, widths=0.6, patch_artist=True,
                    boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
    for j, (patch, color) in enumerate(zip(bp['boxes'], colors)):
        patch.set_facecolor(color)
        if i == 0:
            handles_e.append(patch)
            labels_e.append(f'PF={phaseout_values[j]}')

ax.set_xticks([0] + x_positions)
ax.set_xticklabels(['2030\n(All scenarios)', '2040', '2050', '2060'])
ax.set_ylabel('Carbon Emissions\n(million tCO2)')
ax.set_ylim(0, 1.5)
ax.legend(handles_e, labels_e, loc='upper right', frameon=False)
ax.text(-2, ax.get_ylim()[1] + 0.02*(ax.get_ylim()[1] - ax.get_ylim()[0]), "e.", fontsize=14, fontweight='bold')

# Plot f: Phaseout factor vs Production cost
ax = axes[1, 2]

# 2030 - all scenarios
cost_2030_all = df['Cost_2030'].values
bp1 = ax.boxplot([cost_2030_all], positions=[0], widths=0.6, patch_artist=True,
                 boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
bp1['boxes'][0].set_facecolor('lightgray')

handles_f = [bp1['boxes'][0]]
labels_f = ['All scenarios']

# 2040, 2050, 2060 - by phaseout factor
x_positions = []
for i, year in enumerate([2040, 2050, 2060]):
    col = cost_cols[i+1]
    box_data = []
    colors = []
    for pf in phaseout_values:
        data = df[df['phaseout_factor'] == pf][col].values
        box_data.append(data)
        colors.append(phaseout_colors[pf])
    
    center_pos = 2.6 + i * 4.4
    half_width = (len(phaseout_values) - 1) * 0.4
    positions = [center_pos - half_width + j*0.8 for j in range(len(phaseout_values))]
    x_positions.append(center_pos)
    
    bp = ax.boxplot(box_data, positions=positions, widths=0.6, patch_artist=True,
                    boxprops=boxprops, whiskerprops=whiskerprops, capprops=capprops, medianprops=medianprops)
    for j, (patch, color) in enumerate(zip(bp['boxes'], colors)):
        patch.set_facecolor(color)
        if i == 0:
            handles_f.append(patch)
            labels_f.append(f'PF={phaseout_values[j]}')

ax.set_xticks([0] + x_positions)
ax.set_xticklabels(['2030\n(All scenarios)', '2040', '2050', '2060'])
ax.set_ylabel('Production Cost\n(billion CNY)')
ax.set_ylim(1, 4)
ax.legend(handles_f, labels_f, loc='lower right', frameon=False)
ax.text(-2, ax.get_ylim()[1] + 0.02*(ax.get_ylim()[1] - ax.get_ylim()[0]), "f.", fontsize=14, fontweight='bold')

# Add x-axis label for all subplots with closer positioning
for i in range(2):
    for j in range(3):
        axes[i, j].set_xlabel('Year', labelpad=5)

# Get median, 25th and 75th percentiles
def get_stats(data):
    return np.percentile(data, [25, 50, 75])

# CCS Production
print("\nCCS Production Statistics (25th percentile, median, 75th percentile):")
print("2030 (All scenarios):", [f"{x:.2f}" for x in get_stats(ccs_2030_all)], "million t-steel")
for year, col in zip([2040, 2050, 2060], ccs_cols[1:]):
    print(f"\n{year}:")
    for scenario in ['reference', 'moderate', 'strict']:
        stats = get_stats(df[df['carbon_mode'] == scenario][col])
        print(f"{scenario}: {[f'{x:.2f}' for x in stats]} million t-steel")

# H2 Production
print("\nH2 Production Statistics (25th percentile, median, 75th percentile):")
print("2030 (All scenarios):", [f"{x:.2f}" for x in get_stats(h2_2030_all)], "million t-steel")
for year, col in zip([2040, 2050, 2060], h2_cols[1:]):
    print(f"\n{year}:")
    for scenario in ['reference', 'moderate', 'strict']:
        stats = get_stats(df[df['carbon_mode'] == scenario][col])
        print(f"{scenario}: {[f'{x:.2f}' for x in stats]} million t-steel")

# Emissions and Cost by phaseout factor
print("\nEmissions Statistics (25th percentile, median, 75th percentile):")
print("2030 (All scenarios):", [f"{x:.2f}" for x in get_stats(emission_2030_all)], "million tCO2")
for year, col in zip([2040, 2050, 2060], emission_cols[1:]):
    print(f"\n{year}:")
    for pf in phaseout_values:
        stats = get_stats(df[df['phaseout_factor'] == pf][col])
        print(f"PF={pf}: {[f'{x:.2f}' for x in stats]} million tCO2")

print("\nCost Statistics (25th percentile, median, 75th percentile):")
print("2030 (All scenarios):", [f"{x:.2f}" for x in get_stats(cost_2030_all)], "billion CNY")
for year, col in zip([2040, 2050, 2060], cost_cols[1:]):
    print(f"\n{year}:")
    for pf in phaseout_values:
        stats = get_stats(df[df['phaseout_factor'] == pf][col])
        print(f"PF={pf}: {[f'{x:.2f}' for x in stats]} billion CNY")

plt.savefig('figs/Fig6', dpi=600, bbox_inches='tight')
#plt.show()