import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data_para = pd.read_excel("data_DMA.xlsx", sheet_name="parameters")
category = np.array(data_para['Category'])

data_output = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="output", index_col=0)
data_scrap = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="scrap", index_col=0)
data_stock = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="stock", index_col=0)

#plot
plt.rcParams['font.family'] = 'Arial'
color = ['darkorange', 'mediumpurple', 'saddlebrown', 'olive', 'forestgreen', 'khaki', 'pink', 'aqua',
         'lightgreen', 'steelblue', 'firebrick', 'royalblue', 'chocolate', 'hotpink', 'bisque', 'darkgreen', 'grey']
cmap = {}
for i in range(len(category)):
    cmap[category[i]] = color[i]

# production scrap stock unit 1e4

plt.figure(figsize=(20, 6))
grid = plt.GridSpec(25, 40, wspace=0.3, hspace=0.3, top=0.95, bottom=0.05)
ax1 = plt.subplot(grid[:, 0:19])
data_stock = data_stock.loc[2000:2060]
bottom = np.zeros(len(data_stock.index))
for i in range(len(category)):
    plt.bar(data_stock.index, data_stock[category[i]]/1e5, color=cmap[category[i]], label=category[i], bottom=bottom, alpha=0.8, edgecolor='k')
    bottom += np.array(data_stock[category[i]]/1e5)
plt.xlim(1999, 2061)
plt.xticks(np.arange(2000, 2061, 5))
plt.ylim(0, 20)
plt.yticks(np.arange(0, 20.01, 2))
plt.xlabel('Year')
plt.ylabel('Steel Stock (Gt)')
plt.text(1997, 20*1.02, 'a.', weight='bold', fontsize=15)
plt.text(1999, 20*1.02, 'In-use Stock', fontsize=12)
plt.legend(loc='upper left', bbox_to_anchor=(0, 1), frameon=False, ncol=4, fontsize=10)

ax1 = plt.subplot(grid[:, 21:40])
data_scrap_plot = data_scrap.loc[2000:2060]
bottom = np.zeros(len(data_scrap_plot.index))
data_output_plot = data_output.loc[2000:2060]
bar_handles = []
for i in range(len(category)):
    bar = plt.bar(data_scrap_plot.index, -data_scrap_plot[category[i]]/1e2, color=cmap[category[i]], label=category[i], bottom=bottom, alpha=0.8, edgecolor='k')
    bottom -= np.array(data_scrap_plot[category[i]]/1e2)
    bar_handles.append(bar)
x = np.arange(2025, 2061)
x1 = np.arange(2000, 2025)
y1 = data_output.loc[2000:2024, 'production']/1e2
y2 = data_output.loc[2024:2060, 'production']/1e2
line1, = plt.plot(x1, y1, color='k', label='Statistical Data', linestyle='-', linewidth=2)
line2, = plt.plot(np.arange(2024, 2061), y2, color='k', label='Prediction Data', linestyle='--', linewidth=2)
plt.plot(np.arange(1999, 2062), np.zeros(63), color='k', linestyle='-', linewidth=1)
#y1 = np.array(data_scrap.loc[2025:2060, 'sum']/1e3) * 9795.8 / data_scrap.loc[2020, 'sum']
y1 = np.array(data_output.loc[2025:2060, 'EAF']/1e2)
y2 = np.array(data_output.loc[2025:2060, 'production']/1e2) - y1
stack = plt.stackplot(x, y1, y2, labels=['Scrap-EAF Route', 'Other Routes'], colors=['royalblue', 'grey'], alpha=0.8)
line_stack_handles = [line1, line2] + stack
line_stack_labels = ['Statistical Data', 'Prediction Data', 'Scrap-EAF Route', 'Other Routes']
plt.xlim(1999, 2061)
plt.xticks(np.arange(2000, 2061, 5))
plt.ylim(-700, 1100)
plt.yticks(np.arange(-700, 1110, 100), np.concatenate([np.arange(700, 0, -100), np.arange(0, 1110, 100)]))
plt.xlabel('Year')
plt.ylabel('Production Demand and Steel Scrap (Mt)')
plt.text(1997, 1100+1200*0.03, 'b.', weight='bold', fontsize=15)
plt.text(1999, 1100+1200*0.03, 'Steel Production and Scrap', fontsize=12)
upper_legend = plt.legend(line_stack_handles, line_stack_labels, loc='upper left', bbox_to_anchor=(0, 1), frameon=False, fontsize=10, ncol=1)
ax1.add_artist(upper_legend)
lower_legend = plt.legend(bar_handles, category, loc='upper left', bbox_to_anchor=(0, 0.3), frameon=False, fontsize=10, ncol=1)

plt.savefig('figs/Fig2.png', dpi=600)