import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.lines import Line2D

# 1. Data loading
critical_data = pd.read_excel(
    'outputs/output_critical_price.xlsx',
    sheet_name='CriticalPrice'
)
# Convert electricity price gap to USD/kWh for plotting
CNY_PER_USD = 7.0

critical_data['Electricity_gap_USD_per_kWh'] = (
    critical_data['Electricity_gap_actual_minus_critical']
    / CNY_PER_USD
)
# Map loading
gdf = gpd.read_file("Maps/Province.shp")
gdf_ten_dash = gpd.read_file("Maps/Tendash.shp")

# 2. Grid Layout Definition
# Unchanged from Fig4
province_grid = {
    'Heilongjiang': (0, 8), 'Jilin': (1, 8), 'Liaoning': (2, 8),
    'Tianjin': (2, 7), 'Hebei': (3, 6), 'Shanxi': (3, 5),
    'Inner Mongolia': (2, 6), 'Shandong': (3, 7), 'Henan': (4, 5),
    'Jiangsu': (4, 7), 'Anhui': (4, 6), 'Shanghai': (4, 8),
    'Zhejiang': (5, 7), 'Jiangxi': (5, 6), 'Hubei': (4, 4),
    'Hunan': (5, 5), 'Fujian': (6, 6), 'Guangdong': (6, 5),
    'Guangxi': (6, 4),
    'Shaanxi': (3, 4), 'Gansu': (2, 3), 'Ningxia': (3, 3),
    'Qinghai': (3, 2), 'Xinjiang': (2, 2),
    'Sichuan': (4, 2), 'Chongqing': (4, 3),
    'Guizhou': (5, 4), 'Yunnan': (5, 3),
}

# 3. Parameters
carbon_modes = ['reference', 'moderate', 'strict']

colors = {
    'reference': '#4472C4',
    'moderate': '#ED7D31',
    'strict': '#70AD47'
}

gap_col = 'Electricity_gap_USD_per_kWh'

# Consistent y-axis scale in USD/kWh
max_gap = critical_data[gap_col].abs().max()
y_limit = np.ceil(max_gap / 0.01) * 0.01
y_limit = max(y_limit, 0.02)
y_ticks = np.linspace(-y_limit, y_limit, 5)

year_min = int(critical_data['Year'].min())
year_max = int(critical_data['Year'].max())

# 4. Global plotting setup
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['svg.fonttype'] = 'none'
fig = plt.figure(figsize=(24, 14))

# ------------------------------------------------------------
# Background Map - UNCHANGED FROM FIG4
# ------------------------------------------------------------

ax_bg = fig.add_axes([0.01, 0.12, 0.9, 0.85], zorder=0)

gdf_cropped = gdf.cx[70:125, 15:55]

gdf_cropped.plot(
    ax=ax_bg,
    color='#f8f8f8',
    edgecolor='#dcdcdc',
    linewidth=0.6
)

ax_bg.set_ylim(18, 55)
ax_bg.axis('off')

# ------------------------------------------------------------
# Schematic Diagram - SAME POSITION AS FIG4, but higher zorder
# ------------------------------------------------------------

ax_schematic = fig.add_axes([0.3, 0.73, 0.2, 0.15], zorder=12)
ax_schematic.set_facecolor('white')
ax_schematic.patch.set_alpha(0.95)

# Illustrative trajectories only
schematic_years = np.linspace(year_min, year_max, 20)

schematic_reference = np.linspace(
    0.65 * y_limit, 0.25 * y_limit, 20
)

schematic_moderate = np.linspace(
    0.55 * y_limit, -0.35 * y_limit, 20
)

schematic_strict = np.linspace(
    0.45 * y_limit, -0.70 * y_limit, 20
)

schematic_series = {
    'reference': schematic_reference,
    'moderate': schematic_moderate,
    'strict': schematic_strict
}

for mode in carbon_modes:
    ax_schematic.plot(
        schematic_years,
        schematic_series[mode],
        color=colors[mode],
        linewidth=2.5
    )

ax_schematic.axhline(
    0,
    color='#555555',
    linestyle='--',
    linewidth=1
)

ax_schematic.set_title(
    'Electricity price gap (USD/kWh)',
    fontsize=20,
    weight='bold',
    y=1.2,
    ha='center'
)

ax_schematic.set_xlim(year_min, year_max)
xticks = list(range(year_min, year_max + 1, 5))
ax_schematic.set_xticks(xticks)
ax_schematic.set_xticklabels(
    [str(x) for x in xticks],
    fontsize=16
)

ax_schematic.set_ylim(-y_limit, y_limit)
ax_schematic.set_yticks(y_ticks)
ax_schematic.tick_params(axis='y', labelsize=16)

ax_schematic.spines['top'].set_visible(False)
ax_schematic.spines['right'].set_visible(False)

# ------------------------------------------------------------
# Legend - SAME POSITION BASIS AS FIG4, moved slightly right
# ------------------------------------------------------------

legend_elements = [
    Line2D(
        [0], [0],
        color=colors[mode],
        linewidth=3,
        label=mode.capitalize()
    )
    for mode in carbon_modes
]

fig.legend(
    handles=legend_elements,
    loc='upper center',
    bbox_to_anchor=(0.54, 0.83),
    ncol=1,
    fontsize=18,
    frameon=False
)

# ------------------------------------------------------------
# South China Sea Inset - UNCHANGED FROM FIG4
# ------------------------------------------------------------

ax_inset = fig.add_axes([0.12, 0.15, 0.12, 0.18])

gdf.plot(
    ax=ax_inset,
    color='#f8f8f8',
    edgecolor='#dcdcdc',
    linewidth=0.4
)

gdf_ten_dash.plot(
    ax=ax_inset,
    color='black',
    linewidth=0.8
)

ax_inset.set_xlim(106, 123)
ax_inset.set_ylim(2, 25)

ax_inset.set_xticks([])
ax_inset.set_yticks([])

# ------------------------------------------------------------
# 5. Grid processing & Line plotting
# ALL SUBPLOT POSITION PARAMETERS UNCHANGED FROM FIG4
# except slightly narrower width to increase spacing
# ------------------------------------------------------------

grid_rows, grid_cols = 7, 9

# narrower width to increase horizontal spacing
w, h = 0.07, 0.09

# determine the left-most plotted column in each row
row_min_col = {}
for prov, (r, c) in province_grid.items():
    if r not in row_min_col:
        row_min_col[r] = c
    else:
        row_min_col[r] = min(row_min_col[r], c)

for prov, (r, c) in province_grid.items():

    # EXACT position formula from Fig4
    left = c/grid_cols * 0.82 - 0.02
    bottom = (grid_rows-r-1)/grid_rows * 0.78 + 0.15

    ax = fig.add_axes([left, bottom, w, h], zorder=8)
    ax.set_facecolor('none')

    ax.set_title(
        prov,
        fontsize=16,
        y=0.85,
        weight='bold'
    )

    for mode in carbon_modes:

        df = critical_data[
            (critical_data['Province'] == prov)
            & (critical_data['Scenario'] == mode)
        ].sort_values('Year')

        if df.empty:
            continue

        ax.plot(
            df['Year'],
            df[gap_col],
            color=colors[mode],
            linewidth=1.8,
            zorder=3
        )

    ax.axhline(
        0,
        color='#777777',
        linestyle='--',
        linewidth=0.8,
        zorder=2
    )

    ax.set_xlim(year_min, year_max)
    ax.set_xticks([])

    ax.set_ylim(-y_limit, y_limit)
    ax.set_yticks(y_ticks)

    # Show y-axis tick labels for all provincial subplots
    ax.tick_params(axis='y', labelsize=12, length=2)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# ------------------------------------------------------------
# 6. Scale Bar - UNCHANGED FROM FIG4
# ------------------------------------------------------------

scale_len = 5.5

scale_line = Line2D(
    [0.24, 0.24 + (scale_len/360)],
    [0.16, 0.16],
    transform=fig.transFigure,
    color='black',
    linewidth=2
)

fig.add_artist(scale_line)

plt.figtext(
    0.24 + (scale_len/720),
    0.18,
    "500 km",
    fontsize=20,
    weight='bold',
    ha='center'
)

# ------------------------------------------------------------
# 7. Save - Figure name is Fig5
# ------------------------------------------------------------

plt.savefig(
    'figs/Fig5.png',
    dpi=600,
    bbox_inches='tight'
)

plt.savefig(
    'figs/Fig5.svg',
    dpi=600,
    bbox_inches='tight'
)


# ------------------------------------------------------------
# 8. Print numerical results
# ------------------------------------------------------------

print("\n" + "=" * 76)
print("FIGURE 5: ELECTRICITY PRICE GAP")
print("=" * 76)

report_years = [2030, 2040, 2050, 2060]

for mode in carbon_modes:

    print(f"\nSCENARIO: {mode.upper()}")
    print("-" * 76)

    for year in report_years:

        df = critical_data[
            (critical_data['Scenario'] == mode)
            & (critical_data['Year'] == year)
        ]

        if df.empty:
            continue

        h2_cheaper = (
            df['Cost_gap_H2_minus_CCS_CNY_per_tsteel'] < 0
        )

        print(
            f"{year}: "
            f"H2 cheaper in {h2_cheaper.sum()}/{len(df)} provinces; "
            f"median actual price = "
            f"{df['Electricity_actual_CNY_per_kWh'].median():.3f}; "
            f"median critical price = "
            f"{df['Electricity_critical_CNY_per_kWh'].median():.3f}; "
            f"median gap = {df[gap_col].median():.3f} CNY/kWh"
        )

# ------------------------------------------------------------
# 9. Representative provinces
# ------------------------------------------------------------

focus_provinces = [
    'Inner Mongolia',
    'Gansu',
    'Qinghai',
    'Ningxia',
    'Hebei',
    'Jiangsu',
    'Shandong',
    'Liaoning'
]

print("\n" + "=" * 76)
print("REPRESENTATIVE PROVINCES - MODERATE SCENARIO")
print("=" * 76)

for year in [2040, 2050, 2060]:

    print(f"\nYear: {year}")

    df = critical_data[
        (critical_data['Scenario'] == 'moderate')
        & (critical_data['Year'] == year)
        & (critical_data['Province'].isin(focus_provinces))
    ].sort_values('Province')

    for _, row in df.iterrows():

        advantage = (
            "H2"
            if row['Cost_gap_H2_minus_CCS_CNY_per_tsteel'] < 0
            else "CCS"
        )

        print(
            f"{row['Province']:<16} "
            f"actual={row['Electricity_actual_CNY_per_kWh']:.3f}, "
            f"critical={row['Electricity_critical_CNY_per_kWh']:.3f}, "
            f"gap={row[gap_col]:+.3f}, "
            f"cost_gap="
            f"{row['Cost_gap_H2_minus_CCS_CNY_per_tsteel']:+.1f}, "
            f"cheaper={advantage}"
        )

# ------------------------------------------------------------
# 10. National steel-production-weighted results
# ------------------------------------------------------------

production_file = 'outputs/output_steel_production_by_province.xlsx'

print("\n" + "=" * 76)
print("PRODUCTION-WEIGHTED SHARE")
print("=" * 76)

production_frames = []

for mode in carbon_modes:

    prod = pd.read_excel(production_file, sheet_name=mode)

    prod = prod.melt(
        id_vars='Year',
        var_name='Province',
        value_name='Steel_production'
    )

    prod['Scenario'] = mode
    production_frames.append(prod)

production = pd.concat(production_frames, ignore_index=True)

merged = critical_data.merge(
    production,
    on=['Scenario', 'Province', 'Year'],
    how='left',
    validate='one_to_one'
)

if merged['Steel_production'].isna().any():
    raise ValueError("Missing provincial steel production weights")

merged['H2_advantaged_output'] = (
    merged['Steel_production'].where(
        merged['Cost_gap_H2_minus_CCS_CNY_per_tsteel'] < 0,
        0
    )
)

weighted = (
    merged.groupby(['Scenario', 'Year'], as_index=False)
    .agg(
        total_output=('Steel_production', 'sum'),
        h2_advantaged_output=('H2_advantaged_output', 'sum')
    )
)

weighted['share_pct'] = (
    weighted['h2_advantaged_output']
    / weighted['total_output']
    * 100
)

for mode in carbon_modes:

    print(f"\n{mode.upper()}")

    for year in report_years:

        df = weighted[
            (weighted['Scenario'] == mode)
            & (weighted['Year'] == year)
        ]

        if not df.empty:
            print(
                f"{year}: "
                f"{df['share_pct'].iloc[0]:.2f}% of national "
                f"steel production is located in provinces "
                f"where H2 is cheaper"
            )