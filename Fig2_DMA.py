import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Data Acquisition ---
data_para = pd.read_excel("data_DMA.xlsx", sheet_name="parameters")
category = np.array(data_para['Category'])

data_output = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="output", index_col=0)
data_scrap = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="scrap", index_col=0)
data_stock = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="stock", index_col=0)

# --- Global Plot Configuration ---
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 14,
    'axes.labelsize': 18,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'svg.fonttype': 'none'
})

colors = ['darkorange', 'mediumpurple', 'saddlebrown', 'olive', 'forestgreen', 'khaki', 'pink', 'aqua',
          'lightgreen', 'steelblue', 'firebrick', 'royalblue', 'chocolate', 'hotpink', 'bisque', 'darkgreen', 'grey']

# --- Layout Initialization ---
fig = plt.figure(figsize=(20, 14)) 
grid = plt.GridSpec(1, 2, wspace=0.1, left=0.08, right=0.96, top=0.75, bottom=0.3)

# --- Panel a: In-use Stock (Reverted to Bar) ---
ax1 = plt.subplot(grid[0, 0])
df_stock = data_stock.loc[2000:2060]
bottom_stock = np.zeros(len(df_stock))
stock_handles = []

for i, cat in enumerate(category):
    h = ax1.bar(df_stock.index, df_stock[cat]/1e5, color=colors[i], 
                bottom=bottom_stock, alpha=0.8, edgecolor='k', linewidth=0.3)
    bottom_stock += np.array(df_stock[cat]/1e5)
    stock_handles.append(h)

ax1.set_xlim(1999, 2061)
ax1.set_xticks(np.arange(2000, 2061, 10))
ax1.set_ylim(0, 17) 
ax1.set_yticks(np.arange(0, 17, 2))
ax1.set_title('a. In-use Steel Stock (Gt)', fontsize=22, pad=5, weight='bold')

# --- Panel b: Steel Production and Scrap (Reverted to Bar) ---
ax2 = plt.subplot(grid[0, 1])
df_scrap = data_scrap.loc[2000:2060]
bottom_scrap = np.zeros(len(df_scrap))

# Scrap supply via bars (Negative)
for i, cat in enumerate(category):
    ax2.bar(df_scrap.index, -df_scrap[cat]/1e2, color=colors[i], 
            bottom=bottom_scrap, alpha=0.8, edgecolor='k', linewidth=0.3)
    bottom_scrap -= np.array(df_scrap[cat]/1e2)

# Production Demand Lines
x_hist = np.arange(2000, 2025)
x_proj = np.arange(2024, 2061)
y_hist = data_output.loc[2000:2024, 'production']/1e2
y_proj = data_output.loc[2024:2060, 'production']/1e2

line1, = ax2.plot(x_hist, y_hist, color='k', linestyle='-', linewidth=3)
line2, = ax2.plot(x_proj, y_proj, color='k', linestyle='--', linewidth=3)
ax2.axhline(0, color='k', linestyle='-', linewidth=1.5)

# Production Route decomposition (Reverted to Bar)
x_route = np.arange(2025, 2061)
y_eaf = np.array(data_output.loc[2025:2060, 'EAF']/1e2)
y_others = np.array(data_output.loc[2025:2060, 'production']/1e2) - y_eaf

bar_eaf = ax2.bar(x_route, y_eaf, color='royalblue', alpha=0.8, edgecolor='k', linewidth=0.3)
bar_others = ax2.bar(x_route, y_others, bottom=y_eaf, color='grey', alpha=0.8, edgecolor='k', linewidth=0.3)

ax2.set_xlim(1999, 2061)
ax2.set_xticks(np.arange(2000, 2061, 10))
ax2.set_ylim(-700, 1100) 
ax2.set_yticks(np.arange(-700, 1101, 100))
ax2.set_yticklabels([str(abs(x)) for x in np.arange(-700, 1101, 100)])
ax2.set_title('b. Steel Production and Scrap (Mt)', fontsize=22, pad=5, weight='bold')

# --- Universal Bottom Legend ---
# Row 1: Categories (Sectoral breakdown)
leg1 = fig.legend(stock_handles, category, loc='lower center', 
                  bbox_to_anchor=(0.5, 0.2), ncol=7, frameon=False, fontsize=20)

# Row 2: Production info
prod_handles = [line1, line2, bar_eaf, bar_others]
prod_labels = ['Historical Production', 'Total Projected', 'Scrap-EAF Route', 'Other Routes']
leg2 = fig.legend(prod_handles, prod_labels, loc='lower center', 
                  bbox_to_anchor=(0.5, 0.15), ncol=4, frameon=False, fontsize=20)

# --- Save Final Outputs ---
plt.savefig('figs/Fig2.png', dpi=600, bbox_inches='tight')
plt.savefig('figs/Fig2.svg', bbox_inches='tight')