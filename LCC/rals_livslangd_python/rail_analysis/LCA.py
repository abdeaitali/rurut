import pandas as pd

# Emissionfactors kg Co2e per MJ 
EF_ELECTRICITY = 0.006464924
EF_DIESEL = 0.063583815

# Default values
DEFAULT_SHARE_EL = 0.8  # 80% electricity
DEFAULT_CIRCULARITY_COEF = 0.0  # 0% circularity

def get_LCA_renewal(asset_type, year, track_length=100, circularity_coef=DEFAULT_CIRCULARITY_COEF, share_electricity=DEFAULT_SHARE_EL):

   # Read LCA-data och CO2e-valuation
   # absolute path
   my_abs_path = r'C:\Users\EmmaFrom\Work Folders\Documents\GitHub\rurut\LCC\rurut\LCC\rals_livslangd_python\data\raw\LCA\\'
   lca = pd.read_csv(my_abs_path + 'lca_base_data.csv', delimiter=';', encoding='utf-8')
   co2e = pd.read_csv(my_abs_path + 'co2_valuation.csv', delimiter=';', encoding='utf-8')
   # read Energy use emissions file
   energy_emissions = pd.read_csv(my_abs_path + 'Energy use emissions.csv', delimiter=';', encoding='utf-8')

   # clean up data: replace ',' with '.' and convert to float
   lca = lca.replace(',', '.', regex=True)
   co2e = co2e.replace(',', '.', regex=True)
   energy_emissions = energy_emissions.replace(',', '.', regex=True) 

   lca['CO2 emissions_kg/m'] = lca['CO2 emissions_kg/m'].astype(float)
   lca['Energy use_MJ_m'] = lca['Energy use_MJ_m'].astype(float)
   co2e['CO2_Valuation (kr/kg Co2e)'] = co2e['CO2_Valuation (kr/kg Co2e)'].astype(float)

   # filter asset
   row = lca[lca['Asset'].str.lower() == asset_type.lower()].iloc[0]
   co2_emission = row['CO2 emissions_kg/m']  # kg/m
   energy_use = row['Energy use_MJ_m']       # MJ/m

   # get co2e valuation for year 
   co2_price = co2e[co2e['Year'] == year]['CO2_Valuation (kr/kg Co2e)'].values[0]

   #convert energy use to co2e - emissions 
   emission_factor = share_electricity * EF_ELECTRICITY + (1 - share_electricity) * EF_DIESEL
   energy_co2 = energy_use * emission_factor

   total_co2_per_m = co2_emission + energy_co2  # kg/m

   #total cost 
   total_cost = total_co2_per_m * co2_price * track_length  # SEK

   return total_cost*(1-circularity_coef)  # SEK