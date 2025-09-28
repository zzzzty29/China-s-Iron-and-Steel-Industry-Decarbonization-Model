import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# read data
plt.rcParams['font.family'] = 'Arial'
data_para = pd.read_excel("data_cost.xlsx", sheet_name="Industrial Parameters")
Routes = data_para.columns.to_list()[2:]
years = np.arange(2025, 2061).tolist()

# colors
cmap = {
    'Fixed_Cost': 'aqua',
    'Operating_Cost': 'chocolate',
    'Fuel_Cost': 'bisque',
    'Material_Cost': 'steelblue',
    'Electricity_Cost': 'springgreen',
    'CCS_Cost': 'firebrick',
    'Transportation_Cost': 'hotpink',
    'Electricity_Cost_Low': 'lightgreen',
    'Electricity_Cost_High': 'darkgreen'
}

# read route sheets
route_cat = {}
for route in Routes:
    try:
        df = pd.read_excel("outputs/output_cost_category.xlsx", sheet_name=route)
        route_cat[route] = df
    except Exception:
        pass

# compute route-level bars
data_route_cost = []
for route in Routes:
    if route not in route_cat:
        continue
    df = route_cat[route]
    Fixed_Cost = df['Fixed_Cost'].mean()
    Operating_Cost = df['Operating_Cost'].mean()
    Fuel_Cost = df['Fuel_Cost'].mean()
    Material_Cost = df['Material_Cost'].mean()
    Transportation_Cost = df['Transportation_Cost'].mean()
    CCS_Cost = df['CCS_Cost'].mean() if 'CCS_Cost' in df.columns else 0.0
    elec_cols = [y for y in years if y in df.columns]
    elec_by_year_mean = np.array([df[y].mean() for y in elec_cols])
    Electricity_Cost_Mean = elec_by_year_mean.mean()
    Electricity_Cost_Low = np.min(df[elec_cols])
    Electricity_Cost_High = np.max(df[elec_cols])
    data_route_cost.append({
        'Route': route,
        'Fixed_Cost': Fixed_Cost,
        'Operating_Cost': Operating_Cost,
        'Fuel_Cost': Fuel_Cost,
        'Material_Cost': Material_Cost,
        'Electricity_Cost': Electricity_Cost_Mean,
        'Electricity_Cost_Low': Electricity_Cost_Low,
        'Electricity_Cost_High': Electricity_Cost_High,
        'CCS_Cost': CCS_Cost,
        'Transportation_Cost': Transportation_Cost
    })
data_route_cost = pd.DataFrame(data_route_cost)

# plot
plt.figure(figsize=(20, 12))
grid = plt.GridSpec(31, 42, wspace=0.3, hspace=0.3, top=0.9, bottom=0.05)

# plot a
ax1 = plt.subplot(grid[:20, :20])
index_1 = np.arange(len(data_route_cost)) - 0.3
index_2 = np.arange(len(data_route_cost))
index_3 = np.arange(len(data_route_cost)) + 0.3
width = 0.25
cost_labels = ['Low       Mean       High\n' + r for r in data_route_cost['Route'].tolist()]

stack_categories = ['Fixed_Cost', 'Operating_Cost', 'Fuel_Cost', 'Material_Cost', 'Electricity_Cost', 'CCS_Cost', 'Transportation_Cost']
bottom1 = np.zeros(len(data_route_cost))
bottom2 = np.zeros(len(data_route_cost))
bottom3 = np.zeros(len(data_route_cost))

for cat in stack_categories:
    if cat == 'Electricity_Cost':
        plt.bar(index_1, data_route_cost['Electricity_Cost_Low'], bottom=bottom1, width=width, label='Electricity_Cost_Low', color=cmap['Electricity_Cost_Low'], alpha=0.8, edgecolor='k')
        plt.bar(index_2, data_route_cost['Electricity_Cost'],     bottom=bottom2, width=width, label='Electricity_Cost_Mean', color=cmap['Electricity_Cost'], alpha=0.8, edgecolor='k')
        plt.bar(index_3, data_route_cost['Electricity_Cost_High'],bottom=bottom3, width=width, label='Electricity_Cost_High', color=cmap['Electricity_Cost_High'], alpha=0.8, edgecolor='k')
        bottom1 += data_route_cost['Electricity_Cost_Low'].values
        bottom2 += data_route_cost['Electricity_Cost'].values
        bottom3 += data_route_cost['Electricity_Cost_High'].values
    else:
        val = data_route_cost[cat].values
        plt.bar(index_1, val, bottom=bottom1, width=width, color=cmap.get(cat, 'grey'), alpha=0.8, edgecolor='k')
        plt.bar(index_2, val, bottom=bottom2, width=width, label=cat, color=cmap.get(cat, 'grey'), alpha=0.8, edgecolor='k')
        plt.bar(index_3, val, bottom=bottom3, width=width, color=cmap.get(cat, 'grey'), alpha=0.8, edgecolor='k')
        bottom1 += val
        bottom2 += val
        bottom3 += val

# add carbon price bands (100/500/1000 CNY/tCO2)
carbon_defaults = {'BF-BOF': 2.0, 'BF-BOF-CCS': 1.1, 'Scrap-EAF': 0.08, 'H2-DRI-EAF': 0.1}
# route order aligned with data_route_cost
route_names = data_route_cost['Route'].tolist()
carbon_emission = np.array([carbon_defaults.get(r, 1.0) for r in route_names])

plt.bar(index_1, 100*carbon_emission, bottom=bottom1, width=width, color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='//')
plt.bar(index_2, 100*carbon_emission, bottom=bottom2, width=width, label='Carbon Price (100 CNY/tCO2)', color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='//')
plt.bar(index_3, 100*carbon_emission, bottom=bottom3, width=width, color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='//')
bottom1 += 100*carbon_emission
bottom2 += 100*carbon_emission
bottom3 += 100*carbon_emission

plt.bar(index_1, 400*carbon_emission, bottom=bottom1, width=width, color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='..')
plt.bar(index_2, 400*carbon_emission, bottom=bottom2, width=width, label='Carbon Price (500 CNY/tCO2)', color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='..')
plt.bar(index_3, 400*carbon_emission, bottom=bottom3, width=width, color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='..')
bottom1 += 400*carbon_emission
bottom2 += 400*carbon_emission
bottom3 += 400*carbon_emission

plt.bar(index_1, 500*carbon_emission, bottom=bottom1, width=width, color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='xx')
plt.bar(index_2, 500*carbon_emission, bottom=bottom2, width=width, label='Carbon Price (1000 CNY/tCO2)', color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='xx')
plt.bar(index_3, 500*carbon_emission, bottom=bottom3, width=width, color='white', alpha=0.8, edgecolor='k', linestyle='--', hatch='xx')

plt.xlim(-0.5, len(data_route_cost)-0.5)
plt.ylim(0, 5501)
plt.xticks(index_2, cost_labels)
plt.yticks(np.arange(0, 5501, 500))
plt.ylabel('Steel Production Cost (CNY / t-steel)')
plt.text(-0.5, 5500*1.02, 'a.', weight='bold', fontsize=15)
plt.text(-0.4, 5500*1.02, 'Time-averaged Steel Production Cost of Each Route', fontsize=12)
plt.legend(loc='upper left', frameon=False, fontsize=10, ncol=3)

# plot b (H2-DRI-EAF in 2030, sorted)
route_for_prov = 'H2-DRI-EAF'
if route_for_prov in route_cat:
    axb = plt.subplot(grid[0:9, 22:])
    df = route_cat[route_for_prov].copy()
    df_b = df[['Province', 2030]].copy()
    df_b['Fixed_Cost'] = df['Fixed_Cost']
    df_b['Operating_Cost'] = df['Operating_Cost']
    df_b['Material_Cost'] = df['Material_Cost']
    df_b['Transportation_Cost'] = df['Transportation_Cost']
    df_b['Electricity_Cost'] = df[2030]
    df_b['Total_2030'] = df_b[['Fixed_Cost','Operating_Cost','Material_Cost','Transportation_Cost','Electricity_Cost']].sum(axis=1)
    df_b = df_b.sort_values(by='Total_2030', ascending=True)
    provinces = df_b['Province'].tolist()
    cats_b = ['Fixed_Cost', 'Operating_Cost', 'Material_Cost', 'Transportation_Cost', 'Electricity_Cost']
    bottom = np.zeros(len(provinces))
    idx = np.arange(len(provinces))
    for cat in cats_b:
        plt.bar(idx, df_b[cat], color=cmap.get(cat, 'grey'), label=cat, bottom=bottom, alpha=0.8, edgecolor='k')
        bottom += df_b[cat].values
    plt.xlim(-1, len(provinces))
    plt.xticks([i+0.3 for i in idx], provinces, ha='right', rotation=25, fontsize=8)
    plt.tick_params(axis='x', length=0)
    plt.ylim(0, 5501)
    plt.yticks(np.arange(0, 5501, 500))
    plt.ylabel('Steel Production Cost (CNY / t-steel)')
    plt.text(-1, 5500*1.02, 'b.', weight='bold', fontsize=15)
    plt.text(0, 5500*1.02, 'Provincial Steel Production Cost of H2-DRI-EAF in 2030', fontsize=12)
    plt.legend(loc='upper left', frameon=False, fontsize=10, ncol=3)

# plot c (H2-DRI-EAF in 2060, sorted)
if route_for_prov in route_cat:
    axc = plt.subplot(grid[11:20, 22:])
    df = route_cat[route_for_prov].copy()
    df_c = df[['Province', 2060]].copy()
    df_c['Fixed_Cost'] = df['Fixed_Cost']
    df_c['Operating_Cost'] = df['Operating_Cost']
    df_c['Material_Cost'] = df['Material_Cost']
    df_c['Transportation_Cost'] = df['Transportation_Cost']
    df_c['Electricity_Cost'] = df[2060]
    df_c['Total_2060'] = df_c[['Fixed_Cost','Operating_Cost','Material_Cost','Transportation_Cost','Electricity_Cost']].sum(axis=1)
    df_c = df_c.sort_values(by='Total_2060', ascending=True)
    provinces = df_c['Province'].tolist()
    cats_c = ['Fixed_Cost', 'Operating_Cost', 'Material_Cost', 'Transportation_Cost', 'Electricity_Cost']
    bottom = np.zeros(len(provinces))
    idx = np.arange(len(provinces))
    for cat in cats_c:
        plt.bar(idx, df_c[cat], color=cmap.get(cat, 'grey'), label=cat, bottom=bottom, alpha=0.8, edgecolor='k')
        bottom += df_c[cat].values
    plt.xlim(-1, len(provinces))
    plt.xticks([i+0.3 for i in idx], provinces, ha='right', rotation=25, fontsize=8)
    plt.tick_params(axis='x', length=0)
    plt.ylim(0, 5501)
    plt.yticks(np.arange(0, 5501, 500))
    plt.ylabel('Steel Production Cost (CNY / t-steel)')
    plt.text(-1, 5500*1.02, 'c.', weight='bold', fontsize=15)
    plt.text(0, 5500*1.02, 'Provincial Steel Production Cost of H2-DRI-EAF in 2060', fontsize=12)
    plt.legend(loc='upper left', frameon=False, fontsize=10, ncol=3)

# plot d (BF-BOF-CCS in 2030, sorted)
route_ccs = 'BF-BOF-CCS'
if route_ccs in route_cat:
    axd = plt.subplot(grid[22:31, 0:20])
    df = route_cat[route_ccs].copy()
    df_d = df[['Province', 2030]].copy()
    df_d['Fixed_Cost'] = df['Fixed_Cost']
    df_d['Operating_Cost'] = df['Operating_Cost']
    df_d['Fuel_Cost'] = df['Fuel_Cost']
    df_d['Material_Cost'] = df['Material_Cost']
    df_d['Transportation_Cost'] = df['Transportation_Cost']
    df_d['CCS_Cost'] = df['CCS_Cost']
    df_d['Electricity_Cost'] = df[2030]
    df_d['Total_2030'] = df_d[['Fixed_Cost','Operating_Cost','Fuel_Cost','Material_Cost','Transportation_Cost','Electricity_Cost','CCS_Cost']].sum(axis=1)
    df_d = df_d.sort_values(by='Total_2030', ascending=True)
    provinces = df_d['Province'].tolist()
    cats_d = ['Fixed_Cost', 'Operating_Cost', 'Fuel_Cost', 'Material_Cost', 'Transportation_Cost', 'Electricity_Cost', 'CCS_Cost']
    bottom = np.zeros(len(provinces))
    idx = np.arange(len(provinces))
    for cat in cats_d:
        plt.bar(idx, df_d[cat], color=cmap.get(cat, 'grey'), label=cat, bottom=bottom, alpha=0.8, edgecolor='k')
        bottom += df_d[cat].values
    plt.xlim(-1, len(provinces))
    plt.xticks([i+0.3 for i in idx], provinces, ha='right', rotation=25, fontsize=8)
    plt.tick_params(axis='x', length=0)
    plt.ylim(0, 4001)
    plt.yticks(np.arange(0, 4001, 500))
    plt.ylabel('Steel Production Cost (CNY / t-steel)')
    plt.text(-1, 4000*1.02, 'd.', weight='bold', fontsize=15)
    plt.text(0, 4000*1.02, 'Provincial Steel Production Cost of BF-BOF-CCS in 2030', fontsize=12)
    plt.legend(loc='upper left', frameon=False, fontsize=10, ncol=4)

# plot e (BF-BOF-CCS in 2060, sorted)
if route_ccs in route_cat:
    axe = plt.subplot(grid[22:31, 22:42])
    df = route_cat[route_ccs].copy()
    df_e = df[['Province', 2060]].copy()
    df_e['Fixed_Cost'] = df['Fixed_Cost']
    df_e['Operating_Cost'] = df['Operating_Cost']
    df_e['Fuel_Cost'] = df['Fuel_Cost']
    df_e['Material_Cost'] = df['Material_Cost']
    df_e['Transportation_Cost'] = df['Transportation_Cost']
    df_e['CCS_Cost'] = df['CCS_Cost']
    df_e['Electricity_Cost'] = df[2060]
    df_e['Total_2060'] = df_e[['Fixed_Cost','Operating_Cost','Fuel_Cost','Material_Cost','Transportation_Cost','Electricity_Cost','CCS_Cost']].sum(axis=1)
    df_e = df_e.sort_values(by='Total_2060', ascending=True)
    provinces = df_e['Province'].tolist()
    cats_e = ['Fixed_Cost', 'Operating_Cost', 'Fuel_Cost', 'Material_Cost', 'Transportation_Cost', 'Electricity_Cost', 'CCS_Cost']
    bottom = np.zeros(len(provinces))
    idx = np.arange(len(provinces))
    for cat in cats_e:
        plt.bar(idx, df_e[cat], color=cmap.get(cat, 'grey'), label=cat, bottom=bottom, alpha=0.8, edgecolor='k')
        bottom += df_e[cat].values
    plt.xlim(-1, len(provinces))
    plt.xticks([i+0.3 for i in idx], provinces, ha='right', rotation=25, fontsize=8)
    plt.tick_params(axis='x', length=0)
    plt.ylim(0, 4001)
    plt.yticks(np.arange(0, 4001, 500))
    plt.ylabel('Steel Production Cost (CNY / t-steel)')
    plt.text(-1, 4000*1.02, 'e.', weight='bold', fontsize=15)
    plt.text(0, 4000*1.02, 'Provincial Steel Production Cost of BF-BOF-CCS in 2060', fontsize=12)
    plt.legend(loc='upper left', frameon=False, fontsize=10, ncol=4)

plt.savefig("figs/Fig3.png", dpi=600)
plt.show()