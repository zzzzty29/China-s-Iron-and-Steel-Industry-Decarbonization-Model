import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math


# demand
data_para = pd.read_excel("data_DMA.xlsx", sheet_name="parameters")

data_historical = pd.read_excel("data_DMA.xlsx", sheet_name="historical")
data_historical = data_historical.set_index('Year')

data_ssp = pd.read_excel("data_DMA.xlsx", sheet_name="prediction")
data_ssp = data_ssp.set_index('Year')
data_ssp['GDP_per_capita'] = data_ssp['GDP'] / data_ssp['Population']


consumption_rate = 0.925
category = np.array(data_para['Category'])
ratio = np.array(data_para['ratio'])
lifetime = np.array(data_para['lifetime'])
saturate = np.array(data_para['saturate'])
netexport = np.array(data_ssp['NetExport'])


def scrapratio(lifetime, life):
    a = lifetime
    b = 0.5 * lifetime
    if life == 0:
        ratio = 0
    else:
        ratio = 1 / (b * pow(2 * math.pi, 0.5)) * np.exp(-pow(life - a, 2) / (2 * b * b))
    return ratio


with pd.ExcelWriter('outputs/output_DMA.xlsx') as writer:
        data_scrap = pd.DataFrame()
        data_output = pd.DataFrame()
        data_stock = pd.DataFrame()
        data_stock['GDP'] = data_historical.loc[1952:2024, 'GDP']
        data_stock['Population'] = data_historical.loc[1952:2024, 'Population']
        data_stock['GDP_per_capita'] = data_stock['GDP'] / data_stock['Population']

        # Loop through categories and process data
        for i in range(len(category)):
            data_output[category[i]] = (data_historical.loc[1952:2024, 'Output'] - data_historical.loc[1952:2024, 'NetExport']) * consumption_rate * ratio[i] / 100
            stock = 0
            for year_end in range(1952, 2025):
                scrap = 0
                for year in range(1952, year_end):
                    scrap += data_output.loc[year, category[i]] * scrapratio(lifetime[i], year_end - year)
                data_scrap.loc[year_end, category[i]] = scrap
                stock += data_output.loc[year_end, category[i]] - scrap
                data_stock.loc[year_end, category[i]] = stock

        for i in range(len(category)):
            x = np.array(data_stock.loc[2007:2024, 'GDP_per_capita'])
            y = np.array(np.log(saturate[i] / (data_stock.loc[2007:2024, category[i]] / data_stock.loc[2007:2024, 'Population']) - 1))
            
            slope, intercept = np.polyfit(x, y, 1)

            for year_end in range(2025, 2061):
                data_stock.loc[year_end, category[i]] = saturate[i] / (np.exp(slope * data_ssp.loc[year_end, 'GDP_per_capita'] + intercept) + 1) * data_ssp.loc[year_end, 'Population']
                scrap = 0
                for year in range(1952, year_end):
                    scrap += data_output.loc[year, category[i]] * scrapratio(lifetime[i], year_end - year)
                data_scrap.loc[year_end, category[i]] = scrap
                output = data_stock.loc[year_end, category[i]] - data_stock.loc[year_end - 1, category[i]] + scrap
                data_output.loc[year_end, category[i]] = output

    
        data_output['sum'] = data_output.sum(axis=1)
        data_output.loc[1952:2024, 'NetExport'] = data_historical.loc[1952:2024, 'NetExport']
        data_output.loc[2025:2060, 'NetExport'] = data_ssp.loc[2025:2060, 'NetExport']
        data_output['production'] = data_output['sum'] / consumption_rate + data_output['NetExport']

        data_scrap['sum'] = data_scrap[category].sum(axis=1)
        data_stock['sum'] = data_stock[category].sum(axis=1)

        data_output['EAF'] = data_scrap['sum'] * 9795.8 / data_scrap.loc[2020, 'sum']

        data_output.to_excel(writer, sheet_name='output', index=True)
        data_scrap.to_excel(writer, sheet_name='scrap', index=True)
        data_stock.to_excel(writer, sheet_name='stock', index=True)