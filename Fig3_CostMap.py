import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

plt.rcParams['font.family'] = 'Arial'
plt.rcParams['svg.fonttype'] = 'none'
fig = plt.figure(figsize=(24, 14))  

# Technology color mapping
tech_colors = {
    'BF-BOF': '#5b9bd5', 
    'BF-BOF-CCS': '#ed7d31', 
    'Scrap-EAF': '#ffc000', 
    'H2-DRI-EAF': '#70ad47'
}
Routes = ['BF-BOF', 'BF-BOF-CCS', 'Scrap-EAF', 'H2-DRI-EAF']

# Cost category color mapping
cost_cmap = {
    'Fixed_Cost': 'aqua',
    'Operating_Cost': 'chocolate',
    'Fuel_Cost': 'bisque',
    'Material_Cost': 'steelblue',
    'Electricity_Cost': 'springgreen',
    'CCS_Cost': 'firebrick',
    'Transportation_Cost': 'hotpink'
}

# Time range settings
years_full = np.arange(2030, 2061, 5).tolist()
years_ticks = [2030, 2045, 2060]

# Carbon intensity mapping (tCO2/t-steel)
carbon_defaults = {
    'BF-BOF': 2.0,
    'BF-BOF-CCS': 1.1,
    'Scrap-EAF': 0.08,
    'H2-DRI-EAF': 0.1
}

# --------------------------
# Modified: Load carbon price data and create year-price mapping
# --------------------------
data_para = pd.read_excel("data_cost.xlsx", sheet_name="Industrial Parameters")
data_carbonprice = pd.read_excel('data_cost.xlsx', sheet_name="Carbon Price(CNY per tCO2)")
# Create year to moderate carbon price mapping
carbon_price_map = dict(zip(data_carbonprice['Year'], data_carbonprice['moderate']))

# Load route cost data
route_cat = {}
for route in Routes:
    try:
        df = pd.read_excel("outputs/output_cost_category.xlsx", sheet_name=route)
        route_cat[route] = df
    except Exception:
        pass

# Calculate route-level average cost (without carbon cost for reference)
data_route_cost = []
for route in Routes:
    if route not in route_cat:
        continue
    df = route_cat[route]
    Fixed_Cost = df['Fixed_Cost'].mean()
    Operating_Cost = df['Operating_Cost'].mean()
    Fuel_Cost = df['Fuel_Cost'].mean() if 'Fuel_Cost' in df.columns else 0.0
    Material_Cost = df['Material_Cost'].mean()
    Transportation_Cost = df['Transportation_Cost'].mean()
    CCS_Cost = df['CCS_Cost'].mean() if 'CCS_Cost' in df.columns else 0.0
    elec_cols = [y for y in years_full if y in df.columns]
    Electricity_Cost = np.array([df[y].mean() for y in elec_cols]).mean()
    
    data_route_cost.append({
        'Route': route,
        'Fixed_Cost': Fixed_Cost,
        'Operating_Cost': Operating_Cost,
        'Fuel_Cost': Fuel_Cost,
        'Material_Cost': Material_Cost,
        'Electricity_Cost': Electricity_Cost,
        'CCS_Cost': CCS_Cost,
        'Transportation_Cost': Transportation_Cost
    })
data_route_cost = pd.DataFrame(data_route_cost)

# --------------------------
# Modified: Add carbon cost to provincial cost calculation
# --------------------------
prov_cost_all = {}
for route in Routes:
    if route not in route_cat:
        continue
    df = route_cat[route].copy()
    prov_cost = {}
    # Get carbon intensity for current route
    carbon_intensity = carbon_defaults.get(route, 0.0)
    
    for prov in df['Province'].unique():
        df_p = df[df['Province'] == prov].iloc[0]
        yearly_cost = []
        for year in years_full:
            if year not in df.columns or year not in carbon_price_map:
                continue
            # Calculate basic production cost
            basic_cost_items = [
                df_p['Fixed_Cost'],
                df_p['Operating_Cost'],
                df_p['Fuel_Cost'] if 'Fuel_Cost' in df.columns else 0.0,
                df_p['Material_Cost'],
                df_p['Transportation_Cost'],
                df_p['CCS_Cost'] if 'CCS_Cost' in df.columns else 0.0,
                df_p[year],  # Electricity cost for current year
            ]
            basic_cost = sum(basic_cost_items)
            
            # Calculate carbon cost: carbon price × carbon intensity
            carbon_cost = carbon_price_map[year] * carbon_intensity
            
            # Total cost = basic cost + carbon cost
            total_cost = basic_cost + carbon_cost
            yearly_cost.append(total_cost)
        prov_cost[prov] = yearly_cost
    prov_cost_all[route] = prov_cost
provinces_list = route_cat['H2-DRI-EAF']['Province'].unique().tolist()

# Load China province map
gdf = gpd.read_file("Maps/Province.shp")
gdf_ten_dash = gpd.read_file("Maps/Tendash.shp") 
# Province grid position mapping
province_grid = {
    'Heilongjiang': (0, 8), 'Jilin': (1, 8), 'Liaoning': (2, 8),
    'Tianjin': (2, 7), 'Hebei': (3, 6), 'Shanxi': (3, 5),
    'Inner Mongolia': (2, 6), 'Shandong': (3, 7), 'Henan': (4, 5),
    'Jiangsu': (4, 7), 'Anhui': (4, 6), 'Shanghai': (4, 8),
    'Zhejiang': (5, 7), 'Jiangxi': (5, 6), 'Hubei': (4, 4), 'Hunan': (5, 5),
    'Fujian': (6, 6), 'Guangdong': (6, 5), 'Guangxi': (6, 4), 
    'Shaanxi': (3, 4), 'Gansu': (2, 3), 'Ningxia': (3, 3), 'Qinghai': (3, 2),
    'Xinjiang': (2, 2), 'Sichuan': (4, 2), 'Chongqing': (4, 3),
    'Guizhou': (5, 4), 'Yunnan': (5, 3)
}

# Plot China map background
ax_bg = fig.add_axes([0.01, 0.12, 0.9, 0.85], zorder=0)
gdf_cropped = gdf.cx[70:125, 15:55]
gdf_cropped.plot(ax=ax_bg, color='#f8f8f8', edgecolor='#dcdcdc', linewidth=0.6)
ax_bg.set_ylim(18, 55)
ax_bg.axis('off')

# Add South China Sea inset map
ax_inset = fig.add_axes([0.09, 0.15, 0.12, 0.18])  
gdf.plot(ax=ax_inset, color='#f8f8f8', edgecolor='#dcdcdc', linewidth=0.4)
gdf_ten_dash.plot(ax=ax_inset, color='black', linewidth=0.8) 
ax_inset.set_xlim(106, 123); ax_inset.set_ylim(2, 25)
ax_inset.set_xticks([]); ax_inset.set_yticks([])

# Add scale bar (500km)
scale_len = 5.5 
scale_line = Line2D([0.21, 0.21 + (scale_len/360)], [0.16, 0.16], 
                    transform=fig.transFigure, color='black', linewidth=2)
fig.add_artist(scale_line)
plt.figtext(0.21 + (scale_len/720), 0.18, "500 km", fontsize=20, weight='bold', ha='center')

# Plot provincial cost trend subplots
grid_rows, grid_cols = 7, 9
w, h = 0.08, 0.09

for prov, (r, c) in province_grid.items():
    if prov not in provinces_list:
        continue
    left = c/grid_cols * 0.82 - 0.05
    bottom = (grid_rows-r-1)/grid_rows * 0.78 + 0.15
    ax = fig.add_axes([left, bottom, w, h])
    ax.set_facecolor('none')
    
    ax.set_title(prov, fontsize=16, y=0.85, weight='bold')
    ax.set_xticks([])
    ax.set_ylim(2500, 5500)
    ax.set_yticks(np.arange(3000, 5001, 1000))
    ax.set_yticklabels(np.arange(3, 6, 1), fontsize=16)
    ax.tick_params(axis='y', labelsize=16)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Plot cost trend with carbon cost for each route
    for route in Routes:
        if route not in prov_cost_all or prov not in prov_cost_all[route]:
            continue
        cost_vals = prov_cost_all[route][prov]
        ax.plot(years_full, cost_vals, marker='o', color=tech_colors[route], 
                linewidth=1.5, markersize=3, label=route)

# --------------------------
# Modified: Add carbon cost to national average trend
# --------------------------
ax_schematic = fig.add_axes([0.25, 0.72, 0.3, 0.2])
ax_schematic.set_facecolor('none')

route_yearly_mean = {}
for route in Routes:
    if route not in route_cat:
        continue
    df = route_cat[route]
    yearly_mean = []
    # Get carbon intensity for current route
    carbon_intensity = carbon_defaults.get(route, 0.0)
    
    for year in years_full:
        if year not in df.columns or year not in carbon_price_map:
            continue
        # Calculate basic average cost
        basic_cost_items = [
            df['Fixed_Cost'].mean(),
            df['Operating_Cost'].mean(),
            df['Fuel_Cost'].mean() if 'Fuel_Cost' in df.columns else 0.0,
            df['Material_Cost'].mean(),
            df['Transportation_Cost'].mean(),
            df['CCS_Cost'].mean() if 'CCS_Cost' in df.columns else 0.0,
            df[year].mean()
        ]
        basic_mean = sum(basic_cost_items)
        
        # Add carbon cost
        carbon_cost = carbon_price_map[year] * carbon_intensity
        total_mean = basic_mean + carbon_cost
        yearly_mean.append(total_mean)
    route_yearly_mean[route] = yearly_mean

# Plot national average trend with carbon cost
for route in Routes:
    if route not in route_yearly_mean:
        continue
    ax_schematic.plot(years_full, route_yearly_mean[route], marker='o', 
                      color=tech_colors[route], linewidth=2, markersize=5, label=route)

# Format national trend plot
ax_schematic.set_title('Cost Trend (thousand CNY/t-steel)', fontsize=20, weight='bold', y=0.9)
ax_schematic.set_xlim(2025, 2065)
ax_schematic.set_xticks(years_ticks)
ax_schematic.set_xticklabels(years_ticks, fontsize=16)
ax_schematic.set_ylim(2500, 5500)
ax_schematic.set_yticks(np.arange(2500, 5001, 500))
ax_schematic.set_yticklabels(np.arange(2.5, 5.5, 0.5), fontsize=16)
ax_schematic.tick_params(axis='y', labelsize=16)
ax_schematic.spines['top'].set_visible(False)
ax_schematic.spines['right'].set_visible(False)
ax_schematic.legend(frameon=False, fontsize=20, loc='upper center', bbox_to_anchor=(1.2, 0.83),
           ncol=1)

# Save figures
plt.savefig("figs/Fig3.png", dpi=600, bbox_inches='tight')
plt.savefig("figs/Fig3.svg", dpi=600, bbox_inches='tight')