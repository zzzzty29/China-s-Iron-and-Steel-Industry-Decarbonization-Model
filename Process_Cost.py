import pandas as pd
import numpy as np

# read data
data_para = pd.read_excel("data_cost.xlsx", sheet_name="Industrial Parameters")
Routes = data_para.columns.to_list()[2:]
years = np.arange(2025, 2061).tolist()
carbon_modes = ['reference', 'strict', 'moderate']
data_province_base = pd.read_excel("data_cost.xlsx", sheet_name="Provincal Parameters")
data_carbonprice = pd.read_excel("data_cost.xlsx", sheet_name="Carbon Price(CNY per tCO2)")
year_short = np.arange(2025, 2061, 5)

# mapping carbon intensity (tCO2/t-steel)
carbon_defaults = {
    'BF-BOF': 2.0,
    'BF-BOF-CCS': 1.1,
    'Scrap-EAF': 0.08,
    'H2-DRI-EAF': 0.1
}

# compute category outputs
category_outputs = {route: None for route in Routes}


# compute total cost with carbon price
for carbon_mode in carbon_modes:
    data_electricity = pd.read_excel("data_electricity.xlsx", sheet_name=f"{carbon_mode}_cost")
    data_province = pd.merge(
        data_province_base,
        data_electricity,
        left_on="Province",
        right_on="Provinces",
        how="left"
    ).reset_index(drop=True)
    Price_carbon = np.interp(years, year_short, data_carbonprice[carbon_mode].values)

    with pd.ExcelWriter(f"outputs/output_cost_{carbon_mode}.xlsx") as writer_mode:
        for route in Routes:
            Fixed_Cost = data_para[route].iloc[0]
            Fuel_Intensity = data_para[route].iloc[2]
            Lime_price = data_para[route].iloc[3]
            Iron_ore_consumption = data_para[route].iloc[4]
            Scrap_consumption = data_para[route].iloc[5]
            Lime_consumption = data_para[route].iloc[6]
            Operating_Cost = data_para[route].iloc[7]
            Electricity_Intensity = data_para[route].iloc[8]
            Carbon_Capture = data_para[route].iloc[9]
            Carbon_Capture_Cost = data_para[route].iloc[10]
            Carbon_Storage_Cost = data_para[route].iloc[11]
            Carbon_Transportation_Cost = data_para[route].iloc[12]
            Transportation_cost1 = data_para[route].iloc[13]
            Transportation_cost2 = data_para[route].iloc[14]

            df = data_province.copy()
            # compute
            df['Fixed_Cost'] = Fixed_Cost
            df['Operating_Cost'] = Operating_Cost
            df['Fuel_Cost'] = Fuel_Intensity * df['Fuel price(CNY/kgce)']
            df['Material_Cost'] = (
                Lime_price * Lime_consumption
                + Iron_ore_consumption * df['Iron ore price(CNY/t)']
                + Scrap_consumption * df['Scrap price(CNY/t)']
            ) / 1000.0
            df['CCS_Cost'] = Carbon_Capture * (
                Carbon_Capture_Cost
                + Carbon_Storage_Cost
                + Carbon_Transportation_Cost * df['CCUS transportation distance(km)']
            )
            df['Transportation_Cost'] = (
                Transportation_cost1
                + Transportation_cost2 * df['Product transportation distance(km)']
            )

            # use moderate data for electricity cost
            df_cat = df[['Province', 'Fixed_Cost', 'Operating_Cost', 'Fuel_Cost',
                            'Material_Cost', 'Transportation_Cost', 'CCS_Cost']].copy()
            for y in years:
                df_cat[y] = df[y] * Electricity_Intensity
            category_outputs[route] = df_cat

            provincial_total = pd.DataFrame(columns=['Province'] + years)
            provincial_total['Province'] = df['Province']
            carbon_intensity = carbon_defaults.get(route, 1.0)
            for y_idx, y in enumerate(years):
                electricity_cost_y = df[y] * Electricity_Intensity
                carbon_cost_y = Price_carbon[y_idx] * carbon_intensity
                provincial_total[y] = (
                    df['Fixed_Cost']
                    + df['Operating_Cost']
                    + df['Fuel_Cost']
                    + df['Material_Cost']
                    + df['CCS_Cost']
                    + df['Transportation_Cost']
                    + electricity_cost_y
                    + carbon_cost_y
                )

            # write
            provincial_total.to_excel(writer_mode, sheet_name=f"{route}-{carbon_mode}", index=False)

# write category outputs (no carbon price)
with pd.ExcelWriter("outputs/output_cost_category.xlsx") as writer_cat:
    for route, df_cat in category_outputs.items():
        df_cat.to_excel(writer_cat, sheet_name=route, index=False)
