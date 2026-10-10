"""Cost parity between BF-BOF-CCS and H2-DRI-EAF, consistent with Process_Cost.py.

Run from any directory:
    python Process_CriticalPrice.py
    python Process_CriticalPrice.py --base-dir /path/to/project

Inputs in --base-dir: data_cost.xlsx, data_electricity.xlsx
Outputs in --base-dir/outputs: output_critical_price.xlsx and critical_price_summary.txt

IMPORTANT: This calculates *unit-cost parity*, not the deployment switching
threshold of the subsequent Logit capacity-allocation model.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROUTES = ('BF-BOF-CCS', 'H2-DRI-EAF')
SCENARIOS = ('reference', 'moderate', 'strict')
YEARS = list(range(2025, 2061))
REPORT_YEARS = (2030, 2040, 2050, 2060)
INTENSITIES = {'BF-BOF-CCS': 1.1, 'H2-DRI-EAF': 0.1}  # same as Process_Cost.py


def param_vector(parameters: pd.DataFrame, route: str) -> np.ndarray:
    """Rows are deliberately position-based, exactly as in Process_Cost.py."""
    if route not in parameters:
        raise ValueError(f'Missing route in Industrial Parameters: {route}')
    vals = pd.to_numeric(parameters[route], errors='raise').to_numpy(dtype=float)
    if len(vals) < 15 or not np.isfinite(vals[:15]).all():
        raise ValueError(f'Unexpected parameter vector for {route}')
    return vals


def non_electric_cost(provinces: pd.DataFrame, a: np.ndarray) -> pd.Series:
    """CNY/t-steel, carbon price and electricity EXCLUDED.
    Literal translation of Process_Cost.py lines calculating categories.
    """
    fixed, fuel, lime_price, ore_use, scrap_use, lime_use, operating, electricity = (
        a[0], a[2], a[3], a[4], a[5], a[6], a[7], a[8]
    )
    captured, capture_price, storage_price, transport_price = a[9:13]
    freight_fixed, freight_distance = a[13:15]
    return (
        fixed + operating
        + fuel * provinces['Fuel price(CNY/kgce)']
        + (lime_price * lime_use
           + ore_use * provinces['Iron ore price(CNY/t)']
           + scrap_use * provinces['Scrap price(CNY/t)']) / 1000.0
        + captured * (capture_price + storage_price
                      + transport_price * provinces['CCUS transportation distance(km)'])
        + freight_fixed
        + freight_distance * provinces['Product transportation distance(km)']
    )


def main(base: Path) -> None:
    path_cost = base / 'data_cost.xlsx'
    path_power = base / 'data_electricity.xlsx'
    for p in [path_cost, path_power]:
        if not p.is_file():
            raise FileNotFoundError(f'Input file not found: {p}')
    out_dir = base / 'outputs'
    out_dir.mkdir(exist_ok=True, parents=True)

    parameters = pd.read_excel(path_cost, sheet_name='Industrial Parameters')
    provinces = pd.read_excel(path_cost, sheet_name='Provincal Parameters')
    carbon = pd.read_excel(path_cost, sheet_name='Carbon Price(CNY per tCO2)')
    provinces['Province'] = provinces['Province'].astype(str).str.strip()
    if provinces['Province'].duplicated().any():
        raise ValueError('Duplicated Province in Provincal Parameters')
    carbon = carbon.sort_values('Year')
    if carbon['Year'].min() > min(YEARS) or carbon['Year'].max() < max(YEARS):
        raise ValueError('Carbon price lookup does not cover the analysis horizon')

    a_ccs = param_vector(parameters, ROUTES[0]); a_h2 = param_vector(parameters, ROUTES[1])
    E_ccs, E_h2 = a_ccs[8], a_h2[8]
    dE = E_h2 - E_ccs
    if abs(dE) < 1e-12:
        raise ValueError('Both routes have the same electricity intensity; no unique price threshold')
    A_ccs = non_electric_cost(provinces, a_ccs).to_numpy(dtype=float)
    A_h2 = non_electric_cost(provinces, a_h2).to_numpy(dtype=float)

    records = []
    for scen in SCENARIOS:
        power = pd.read_excel(path_power, sheet_name=f'{scen}_cost')
        power['Provinces'] = power['Provinces'].astype(str).str.strip()
        if power['Provinces'].duplicated().any():
            raise ValueError(f'Duplicated province in {scen}_cost')
        power = power.set_index('Provinces')
        missing = sorted(set(provinces['Province']) - set(power.index))
        if missing:
            raise ValueError(f'Unmatched electricity provinces in {scen}: {missing}')
        carbon_vals = np.interp(YEARS, carbon['Year'], carbon[scen])

        for idx, prov in enumerate(provinces['Province']):
            for j, year in enumerate(YEARS):
                if year not in power.columns:
                    raise ValueError(f'Missing year {year} in {scen}_cost')
                P = float(power.loc[prov, year])
                CP = float(carbon_vals[j])
                if not np.isfinite(P):
                    raise ValueError(f'Non-finite electricity price: {scen}, {prov}, {year}')
                # Original model also adds scenario-specific residual-emission cost.
                B_ccs = A_ccs[idx] + INTENSITIES[ROUTES[0]] * CP
                B_h2 = A_h2[idx] + INTENSITIES[ROUTES[1]] * CP
                P_star = (B_ccs - B_h2) / dE
                c_ccs = B_ccs + E_ccs * P
                c_h2 = B_h2 + E_h2 * P
                gap = c_h2 - c_ccs
                predicted_gap = dE * (P - P_star)
                records.append({
                    'Scenario': scen, 'Province': prov, 'Year': year,
                    'Carbon_price_CNY_per_tCO2': CP,
                    'Electricity_actual_CNY_per_kWh': P,
                    'Electricity_critical_CNY_per_kWh': P_star,
                    'Electricity_gap_actual_minus_critical': P-P_star,
                    'Electricity_decline_required_CNY_per_kWh': max(0.0,P-P_star),
                    'Electricity_decline_required_pct_of_actual': max(0.0,(P-P_star)/P*100) if P>0 else np.nan,
                    'Cost_CCS_CNY_per_tsteel': c_ccs,
                    'Cost_H2_CNY_per_tsteel': c_h2,
                    'Cost_gap_H2_minus_CCS_CNY_per_tsteel': gap,
                    'Electricity_intensity_CCS_kWh_per_tsteel': E_ccs,
                    'Electricity_intensity_H2_kWh_per_tsteel': E_h2,
                    'Parity_reconstruction_error_CNY_per_tsteel': gap-predicted_gap,
                    'Lower_cost_route': (ROUTES[1] if gap < -1e-8 else ROUTES[0] if gap > 1e-8 else 'Equal'),
                    'Parity_at_nonnegative_price': P_star >= 0,
                })

    data = pd.DataFrame(records)
    max_err = data['Parity_reconstruction_error_CNY_per_tsteel'].abs().max()
    if max_err > 1e-7:
        raise AssertionError(f'Cost-parity validation FAILED, maximum error={max_err}')

    # Province counts are UNWEIGHTED; not steel production or capacity shares.
    summary = (data.groupby(['Scenario','Year'], sort=False)
               .agg(n_provinces=('Province','nunique'),
                    n_H2_cheaper=('Lower_cost_route',lambda x:(x==ROUTES[1]).sum()),
                    n_CCS_cheaper=('Lower_cost_route',lambda x:(x==ROUTES[0]).sum()),
                    median_critical_CNY_per_kWh=('Electricity_critical_CNY_per_kWh','median'),
                    min_critical_CNY_per_kWh=('Electricity_critical_CNY_per_kWh','min'),
                    max_critical_CNY_per_kWh=('Electricity_critical_CNY_per_kWh','max'),
                    median_actual_CNY_per_kWh=('Electricity_actual_CNY_per_kWh','median'),
                    median_cost_gap_CNY_per_tsteel=('Cost_gap_H2_minus_CCS_CNY_per_tsteel','median'))
               .reset_index())
    summary['pct_provinces_H2_cheaper'] = summary['n_H2_cheaper']/summary['n_provinces']*100
    summary['n_provinces_H2_cheaper'] = summary['n_H2_cheaper']
    report = summary[summary['Year'].isin(REPORT_YEARS)].copy()
    provinces_focus = data[(data['Scenario']=='moderate') & (data['Year']==2050)].copy()
    provinces_focus = provinces_focus.sort_values('Cost_gap_H2_minus_CCS_CNY_per_tsteel')
    validation = pd.DataFrame([
        {'Check':'Input provinces','Value':len(provinces)},
        {'Check':'Scenarios','Value':len(SCENARIOS)},
        {'Check':'Years','Value':len(YEARS)},
        {'Check':'Records','Value':len(data)},
        {'Check':'Electricity intensity CCS (kWh/t-steel)','Value':E_ccs},
        {'Check':'Electricity intensity H2 (kWh/t-steel)','Value':E_h2},
        {'Check':'Max algebraic parity error (CNY/t-steel)','Value':max_err},
        {'Check':'Nonnegative critical price records','Value':int((data['Electricity_critical_CNY_per_kWh']>=0).sum())},
        {'Check':'NOTE','Value':'Local cost parity is not a Logit deployment switching threshold.'},
        {'Check':'NOTE','Value':'All province counts are UNWEIGHTED, not capacity shares.'},
        {'Check':'NOTE','Value':'CCS and H2 both face same provincial power price per Process_Cost.py.'},
    ])

    outfile = out_dir / 'output_critical_price.xlsx'
    with pd.ExcelWriter(outfile, engine='openpyxl') as writer:
        data.to_excel(writer, sheet_name='CriticalPrice', index=False)
        data[['Scenario','Province','Year','Cost_CCS_CNY_per_tsteel','Cost_H2_CNY_per_tsteel',
              'Cost_gap_H2_minus_CCS_CNY_per_tsteel','Lower_cost_route']].to_excel(writer,sheet_name='CostGap',index=False)
        summary.to_excel(writer,sheet_name='Summary',index=False)
        report.to_excel(writer,sheet_name='KeyYears',index=False)
        provinces_focus.to_excel(writer,sheet_name='Provinces_2050_moderate',index=False)
        validation.to_excel(writer,sheet_name='Validation',index=False)

    heading = ('Cost parity: H2-DRI-EAF vs BF-BOF-CCS\n'
               'Based on the equations of Process_Cost.py\n'
               'A positive cost gap means CCS is cheaper.\n'
               'Province counts are UNWEIGHTED; not predicted deployment.\n')
    print('\n'+heading)
    print('Electricity intensities (kWh/t-steel): CCS={:.1f}; H2={:.1f}; difference={:.1f}'.format(E_ccs,E_h2,dE))
    print('Max parity identity error: {:.3g} CNY/t-steel'.format(max_err))
    print('\nKey-year summary:')
    cols=['Scenario','Year','n_H2_cheaper','n_provinces','median_critical_CNY_per_kWh',
          'median_actual_CNY_per_kWh','median_cost_gap_CNY_per_tsteel']
    print(report[cols].round(3).to_string(index=False))
    print('\nModerate, 2050: 5 smallest H2-minus-CCS cost gaps:')
    focuscols=['Province','Electricity_actual_CNY_per_kWh','Electricity_critical_CNY_per_kWh','Cost_gap_H2_minus_CCS_CNY_per_tsteel']
    print(provinces_focus[focuscols].head(5).round(3).to_string(index=False))
    print('\nModerate, 2050: 5 largest H2-minus-CCS cost gaps:')
    print(provinces_focus[focuscols].tail(5).round(3).to_string(index=False))
    print(f'\nExcel: {outfile.resolve()}')
    summary_txt = out_dir / 'critical_price_summary.txt'
    with summary_txt.open('w', encoding='utf-8') as f:
        f.write(heading + '\n')
        f.write(report[cols].round(4).to_string(index=False))
        f.write('\n\nModerate, 2050 — lowest cost gaps\n')
        f.write(provinces_focus[focuscols].head(5).round(4).to_string(index=False))
        f.write('\n\nModerate, 2050 — highest cost gaps\n')
        f.write(provinces_focus[focuscols].tail(5).round(4).to_string(index=False))
        f.write('\n\nMaximum parity error: '+str(max_err)+'\n')
    print(f'Text summary: {summary_txt.resolve()}')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir',type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args()
    main(args.base_dir.resolve())
