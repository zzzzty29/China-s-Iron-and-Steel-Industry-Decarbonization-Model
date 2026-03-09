import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# 1. Data loading
output_data = pd.read_excel('outputs/output_basic.xlsx', sheet_name=None)
data_capacity_2024 = pd.read_excel('data_capacity.xlsx')
provinces_list = list(data_capacity_2024['Province'].values)

# Map loading 
gdf = gpd.read_file("Maps/Province.shp")
gdf_ten_dash = gpd.read_file("Maps/Tendash.shp") 

# 2. Grid Layout Definition
province_grid = {
    'Heilongjiang': (0, 8), 'Jilin': (1, 8), 'Liaoning': (2, 8),
    'Tianjin': (2, 7), 'Hebei': (3, 6), 'Shanxi': (3, 5),
    'Inner Mongolia': (2, 6), 'Shandong': (3, 7), 'Henan': (4, 5),
    'Jiangsu': (4, 7), 'Anhui': (4, 6), 'Shanghai': (4, 8),
    'Zhejiang': (5, 7), 'Jiangxi': (5, 6), 'Hubei': (4, 4), 'Hunan': (5, 5),
    'Fujian': (6, 6), 'Guangdong': (6, 5), 'Guangxi': (6, 4), 
    'Shaanxi': (3, 4), 'Gansu': (2, 3), 'Ningxia': (3, 3), 'Qinghai': (3, 2),
    'Xinjiang': (2, 2), 'Sichuan': (4, 2), 'Chongqing': (4, 3),
    'Guizhou': (5, 4), 'Yunnan': (5, 3), 
    #'Macau': (7, 4), 'Hong Kong': (7, 6), 'Beijing': (2, 6),'Tibet': (3, 1), 'Taiwan': (6, 7), 'Hainan': (7, 5),
}

# 3. Parameters
carbon_modes = ['reference', 'moderate', 'strict']
techs = ['EAF', 'CCS', 'H2']
colors = {'EAF': '#5b9bd5', 'CCS': '#ed7d31', 'H2': '#70ad47'} 

# 4. Global plotting setup
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['svg.fonttype'] = 'none'
fig = plt.figure(figsize=(24, 14))

# -------------------------- Modified Part: Schematic Diagram --------------------------
# Add schematic diagram axis (top center)
# Position: [left, bottom, width, height] - top center of the figure
# Reduce overall width from 0.2 to 0.15
ax_schematic = fig.add_axes([0.35, 0.75, 0.15, 0.1])  # Adjusted width to 0.15
ax_schematic.set_facecolor('none')

# Generate random data for schematic (same structure as province subplots)
np.random.seed(42)  # Fixed seed for reproducibility
schematic_data = np.random.randint(5, 20, size=(3, 3))  # 3 modes × 3 techs

# Plot stacked bar chart (same as province subplots)
x_pos = np.arange(3)
bottoms = np.zeros(3)
# Reduce bar width from 0.7 to 0.5 for narrower bars
for i, tech in enumerate(techs):
    ax_schematic.bar(x_pos, schematic_data[:, i], bottom=bottoms, color=colors[tech],
                     edgecolor='white', linewidth=0.2, width=0.5)  # Adjusted bar width to 0.5
    bottoms += schematic_data[:, i]

# Schematic styling
# Main title for schematic diagram
ax_schematic.set_title('Provincial crude steel production in 2060 (Mt)', 
                       fontsize=20, weight='bold', y=1.2, ha='center')
# X-axis labels (carbon modes)
ax_schematic.set_xticks(x_pos)
ax_schematic.set_xticklabels(carbon_modes, fontsize=16)
# Y-axis (simplified, same range as province subplots)
ax_schematic.set_ylim(0, 50)
ax_schematic.set_yticks(np.arange(0, 51, 10))
ax_schematic.tick_params(axis='y', labelsize=16)
# Remove spines (consistent with province subplots)
ax_schematic.spines['top'].set_visible(False)
ax_schematic.spines['right'].set_visible(False)

# -------------------------- Modified Part: Legend --------------------------
# Global Legend - Next to schematic diagram (top center right)
# Map short names to full names for legend display only
tech_full_names = ['Scrap-EAF', 'BF-BOF-CCS', 'H2-DRI-EAF']
legend_elements = [Patch(facecolor=colors[t], label=tech_full_names[i]) for i, t in enumerate(techs)]
# Adjust legend position to be next to schematic (top center right)
fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.56, 0.83),
           ncol=1, fontsize=18, frameon=False)

# -------------------------------------------------------------------------------------
# Remaining code (unchanged)
# -------------------------------------------------------------------------------------
# Background Map - Crop to Hainan Island, shift left
ax_bg = fig.add_axes([0.01, 0.12, 0.9, 0.85], zorder=0)
# Crop map to Hainan Island range (adjust coordinates if needed)
gdf_cropped = gdf.cx[70:125, 15:55]  # Longitude:70-125, Latitude:15-55 (covers up to Hainan)
gdf_cropped.plot(ax=ax_bg, color='#f8f8f8', edgecolor='#dcdcdc', linewidth=0.6)
ax_bg.set_ylim(18, 55)
ax_bg.axis('off')

# South China Sea Inset - Move to bottom left
# [left, bottom, width, height] - bottom left position
ax_inset = fig.add_axes([0.12, 0.15, 0.12, 0.18])  
gdf.plot(ax=ax_inset, color='#f8f8f8', edgecolor='#dcdcdc', linewidth=0.4)
gdf_ten_dash.plot(ax=ax_inset, color='black', linewidth=0.8) 
ax_inset.set_xlim(106, 123); ax_inset.set_ylim(2, 25)
ax_inset.set_xticks([]); ax_inset.set_yticks([])

# 5. Grid processing & Bar plotting
grid_rows, grid_cols = 7, 9
# Enlarge subplots: increase width (w) and height (h)
w, h = 0.08, 0.09  # Original: 0.065, 0.075

for prov, (r, c) in province_grid.items():
    # Calculate aligned positions - Shifted to left (adjusted left offset)
    left = c/grid_cols * 0.82 - 0.02  # Adjust if subplots overlap
    bottom = (grid_rows-r-1)/grid_rows * 0.78 + 0.15
    ax = fig.add_axes([left, bottom, w, h])
    ax.set_facecolor('none')
    
    # Subplot styling
    ax.set_title(prov, fontsize=16, y=0.85, weight='bold')
    ax.set_xticks([])
    ax.set_ylim(0, 50)
    ax.set_yticks(np.arange(0, 51, 10))
    ax.tick_params(axis='y', labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Plot bars only if data exists for the province
    if prov in provinces_list:
        idx = provinces_list.index(prov)
        mode_data = []
        for mode in carbon_modes:
            df = output_data[f'{mode}_capacity']
            eaf_val = df['EAF'].values[idx] / 1000
            ccs_val = df['CCS'].values[idx] / 1000
            h2_val = df['H2'].values[idx] / 1000
            mode_data.append([eaf_val, ccs_val, h2_val])
        
        mode_data = np.array(mode_data)
        x_pos = np.arange(3)
        bottoms = np.zeros(3)
        for i, tech in enumerate(techs):
            ax.bar(x_pos, mode_data[:, i], bottom=bottoms, color=colors[tech], 
                   edgecolor='white', linewidth=0.2, width=0.7)
            bottoms += mode_data[:, i]
    else:
        pass

# 6. Add Scale Bar - Below South China Sea inset (bottom left)
scale_len = 5.5 
# Position scale bar below the inset map (bottom left)
scale_line = Line2D([0.24, 0.24 + (scale_len/360)], [0.16, 0.16], 
                    transform=fig.transFigure, color='black', linewidth=2)
fig.add_artist(scale_line)
plt.figtext(0.24 + (scale_len/720), 0.18, "500 km", fontsize=20, weight='bold', ha='center')

# Save
plt.savefig('figs/Fig4.png', dpi=600, bbox_inches='tight')
plt.savefig('figs/Fig4.svg', dpi=600, bbox_inches='tight')