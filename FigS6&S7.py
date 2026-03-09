import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

# Create directory if not exists
if not os.path.exists('figs'):
    os.makedirs('figs')

# Read sensitivity analysis results
df = pd.read_excel('outputs/output_sensitivity.xlsx')
plt.rcParams['svg.fonttype'] = 'none'

# --- Unit Conversion ---
# Production: million ton
h2_cols = ['H2_2030', 'H2_2040', 'H2_2050', 'H2_2060']
ccs_cols = ['CCS_2030', 'CCS_2040', 'CCS_2050', 'CCS_2060']
for col in h2_cols + ccs_cols:
    df[col] = df[col] / 1000

# Emissions: million ton CO2
emission_cols = ['Emission_2030', 'Emission_2040', 'Emission_2050', 'Emission_2060']
for col in emission_cols:
    df[col] = df[col] / 1e6

# Cost: billion CNY
cost_cols = ['Cost_2030', 'Cost_2040', 'Cost_2050', 'Cost_2060']
for col in cost_cols:
    df[col] = df[col] / 1e9

def get_stats(data):
    return np.percentile(data, [25, 50, 75])

def generate_figure_and_stats(df, param_col, param_values, colors, labels, filename, param_name):
    """
    Generate the 2x2 plot and print statistics in Fig6 format.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.subplots_adjust(hspace=0.3, wspace=0.25, top=0.92, bottom=0.1)
    
    # Configuration for subplots
    configs = [
        (ccs_cols, 'BF-BOF-CCS Production', 'million t-steel', (0, 0), "a."),
        (h2_cols, 'H2-DRI-EAF Production', 'million t-steel', (0, 1), "b."),
        (emission_cols, 'Carbon Emissions', 'billion tCO2e', (1, 0), "c."),
        (cost_cols, 'Production Cost', 'trillion CNY', (1, 1), "d.")
    ]
    
    boxprops = dict(linewidth=1.2, color='black')
    print(f"\n" + "="*50)
    print(f"STATISTICS FOR: {param_name} ({filename})")
    print("="*50)

    for cols, title, unit, idx, tag in configs:
        ax = axes[idx]
        
        # --- Statistics Printing (Fig6 Format) ---
        print(f"\n{title} Statistics (25th percentile, median, 75th percentile):")
        data_2030 = df[cols[0]].values
        print(f"2030 (All scenarios): {[f'{x:.2f}' for x in get_stats(data_2030)]} {unit}")
        
        # --- Plotting 2030 Base ---
        bp_base = ax.boxplot([data_2030], positions=[0], widths=0.6, patch_artist=True,
                             boxprops=boxprops, showfliers=False)
        bp_base['boxes'][0].set_facecolor('lightgray')
        
        handles = [bp_base['boxes'][0]]
        legend_labels = ['2030 Base']
        
        # --- Plotting & Printing 2040, 2050, 2060 ---
        x_positions = []
        for i, year_col in enumerate(cols[1:]):
            year = [2040, 2050, 2060][i]
            print(f"\n{year}:")
            
            box_data = []
            for v_idx, val in enumerate(param_values):
                subset = df[df[param_col] == val][year_col].values
                box_data.append(subset)
                # Print stats for each parameter value
                stats = get_stats(subset)
                print(f"{labels[v_idx]}: {[f'{x:.2f}' for x in stats]} {unit}")
            
            center_pos = 2.6 + i * 4.5
            half_width = (len(param_values) - 1) * 0.4
            pos = [center_pos - half_width + j*0.8 for j in range(len(param_values))]
            x_positions.append(center_pos)
            
            bp = ax.boxplot(box_data, positions=pos, widths=0.6, patch_artist=True,
                            boxprops=boxprops, showfliers=False)
            
            for j, patch in enumerate(bp['boxes']):
                patch.set_facecolor(colors[j])
                if i == 0:
                    handles.append(patch)
                    legend_labels.append(labels[j])
        
        # --- Axis and Legend Formatting ---
        ax.set_xticks([0] + x_positions)
        ax.set_xticklabels(['2030\n(Base)', '2040', '2050', '2060'])
        ax.set_ylabel(f"{title}\n({unit})")
        ax.set_xlabel('Year')
        ax.text(-0.05, 1.05, tag, transform=ax.transAxes, fontsize=14, fontweight='bold')
        
        if tag == "d.": # Cost
            ax.set_ylim(1, 4) # Extended range to fit legend at bottom
            ax.legend(handles, legend_labels, loc='lower right', frameon=False, fontsize=9)
        elif tag == "c.": # Emission
            ax.set_ylim(0, 1.5)
            ax.legend(handles, legend_labels, loc='upper right', frameon=False, fontsize=9)
        else: # Production
            ax.legend(handles, legend_labels, loc='upper left', frameon=False, fontsize=9)

    plt.savefig(f'figs/{filename}.png', dpi=600, bbox_inches='tight')
    plt.savefig(f'figs/{filename}.svg', bbox_inches='tight')
    print(f"\n>>> Successfully saved {filename} to figs/ folder.")

# --- Figure S5: Electricity Price Multiplier ---
# Using 5 representative values for clarity
elec_vals = [-0.2, -0.1, 0.0, 0.1, 0.2]
elec_colors = sns.color_palette("RdBu_r", len(elec_vals))
elec_labels = [f"Price {int(v*100):+d}%" for v in elec_vals]

generate_figure_and_stats(df, 'electricity_multiplier', elec_vals, 
                         elec_colors, elec_labels, 'FigS6', 'Electricity Price Multiplier')

# --- Figure S6: CPP Share ---
cpp_vals = [0.0, 0.25, 0.5, 0.75, 1.0]
cpp_colors = sns.color_palette("Greens", len(cpp_vals))
cpp_labels = [f"CPP {int(v*100)}%" for v in cpp_vals]

generate_figure_and_stats(df, 'cpp_share', cpp_vals, 
                         cpp_colors, cpp_labels, 'FigS7', 'CPP Share')