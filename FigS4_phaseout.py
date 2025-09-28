import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

#calculate
data_output = pd.read_excel('outputs/output_DMA.xlsx', sheet_name="output")
years1 = np.arange(2025, 2031, 5).tolist()
years2 = np.arange(2030, 2061, 5).tolist()
data_output.index = data_output['Year']
y = np.array(data_output.loc[2025:2060, 'production']/1e2)
y1 = np.array(data_output.loc[2025:2060, 'EAF']/1e2) # EAF
y2 = y - y1 # BOF
ratio = np.power(np.arange(1, -0.001, -1/30), 3)
y3 = y2[5:] * ratio
y4 = (y2[5:] - y3) * 0.6

index1 = np.arange(6)
index2 = np.arange(5, 36) + 20
plt.figure(figsize=(12, 6))
plt.rcParams['font.family'] = 'Arial'
plt.bar(index1, y2[:6], label='BF-BOF', color='orange', edgecolor='k', linewidth=1, alpha=0.8)
plt.bar(index1, y1[:6], label='Scrap-EAF', bottom=y2[:6], color='c', edgecolor='k', linewidth=1, alpha=0.8)
plt.bar(index2, y3, color='orange', edgecolor='k', linewidth=1, alpha=0.8)
plt.bar(index2, y4, bottom=y3, color='red', label='BF-BOF-CCS',edgecolor='k', linewidth=1, alpha=0.8)
plt.bar(index2, y2[5:]-y3-y4, bottom=y3+y4, label='H2-DRI-EAF',color='g', edgecolor='k', linewidth=1, alpha=0.8)
plt.bar(index2, y1[5:], bottom=y2[5:], color='c', edgecolor='k', linewidth=1, alpha=0.8)
plt.text(15, 750, 'Before 2030\nBF-BOF Phaseout\nBy Production Demand\nWithout New Construction', ha='center', va='center', fontsize=12)
plt.annotate('', xy=(7, 670), xytext=(23, 670), arrowprops=dict(arrowstyle='simple'), va='center')
plt.text(15, 480, 'After 2030\nBF-BOF Phaseout\nBy an Exponential Function\nWith New Construction', ha='center', va='center', fontsize=12)
plt.annotate('', xy=(23, 400), xytext=(7, 400), arrowprops=dict(arrowstyle='simple'), va='center')
plt.text(70, 430, 'New Construction of H2-DRI-EAF\nBy a Relative-Cost-Logit Function', ha='center', va='center', fontsize=12)
plt.annotate('', xy=(60, 370), xytext=(80, 370), arrowprops=dict(arrowstyle='simple'), va='center')
plt.text(70, 160, 'New Construction of BF-BOF-CCS\nBy a Relative-Cost-Logit Function', ha='center', va='center', fontsize=12)
plt.annotate('', xy=(60, 100), xytext=(80, 100), arrowprops=dict(arrowstyle='simple'), va='center')
plt.stackplot(np.arange(58, 83), y4[-1], y2[-1] - y4[-1], colors=['red','g'], edgecolor='k', linewidth=1, alpha=0.2, linestyle='--')
plt.xlim(-1, 85)
plt.ylim(0, 1000)
plt.xticks(np.append(np.arange(0, 6, 5), np.arange(5, 36, 5) + 20), years1 + years2)
plt.yticks(np.arange(0, 1001, 100))
plt.ylabel('Steel Production (Mt)')
plt.xlabel('Year')
plt.legend(loc='upper right', frameon=False, fontsize=10, ncol=2)

plt.savefig('figs/FigS4.png', dpi=600)
plt.show()