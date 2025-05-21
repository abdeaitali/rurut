import pandas as pd

def get_LCA_renewal(track_length, asset_type, year, share_electricity=1.0, circularity_coefficient=0.0):
    EF_ELECTRICITY = 0.006464924
    EF_DIESEL = 0.063583815

    lca = pd.read_csv('C:/Users/EmmaFrom/Work Folders/Documents/GitHub/rurut/LCC/rurut/LCC/rals_livslangd_python/data/raw/LCA/lca_base_data.csv', delimiter=';', encoding='utf-8')
    co2e = pd.read_csv('C:/Users/EmmaFrom/Work Folders/Documents/GitHub/rurut/LCC/rurut/LCC/rals_livslangd_python/data/raw/LCA/co2_valuation.csv', delimiter=';', encoding='utf-8')

    lca['CO2 emissions_kg/m'] = lca['CO2 emissions_kg/m'].str.replace(',', '.').astype(float)
    lca['Energy use_MJ_m'] = lca['Energy use_MJ_m'].str.replace(',', '.').astype(float)
    co2e.columns = co2e.columns.str.strip()
    co2_valuation_col = [col for col in co2e.columns if 'CO2_Valuation' in col][0]
    co2e[co2_valuation_col] = co2e[co2_valuation_col].str.replace(',', '.').astype(float)

    row = lca[lca['Asset'] == asset_type].iloc[0]
    co2_emission = row['CO2 emissions_kg/m']
    energy_use = row['Energy use_MJ_m']

    co2_price = co2e[co2e['Year'] == year][co2_valuation_col].values[0]

    emission_factor = share_electricity * EF_ELECTRICITY + (1 - share_electricity) * EF_DIESEL
    energy_co2 = energy_use * emission_factor

    total_co2_per_m = co2_emission + energy_co2
    adjusted_co2_per_m = total_co2_per_m * (1 - circularity_coefficient)
    total_cost = adjusted_co2_per_m * co2_price * track_length

    return total_cost
