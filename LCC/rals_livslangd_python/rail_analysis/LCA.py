import pandas as pd

def get_LCA_renewal (track_length, asset_type, year, share_electricity=1.0):

# Emissionfactors kg Co2e per MJ 
   EF_ELECTRICITY = 0.006464924
   EF_DIESEL = 0.063583815

# Read LCA-data och CO2e-valuation
   lca = pd.read_csv('../data/raw/LCA/lca_base_data.csv', delimiter=';', encoding='utf-8')
   co2e = pd.read_csv('../data/raw/LCA/co2_valuation.csv', delimiter=';', encoding='utf-8')

# Convert commas to dots
   lca['CO2 emissions_kg/m'] = lca['CO2 emissions_kg/m'].str.replace(',', '.').astype(float)
   lca['Energy use_MJ_m'] = lca['Energy use_MJ_m'].str.replace(',', '.').astype(float)
   co2e['CO2_Valuation (SEK/kg Co2e)'] = co2e['CO2_Valuation (SEK/kg Co2e)'].str.replace(',', '.').astype(float)

# filter asset
   row = lca[lca['Asset'] == asset_type].iloc[0]
   co2_emission = row['CO2 emissions_kg/m']  # kg/m
   energy_use = row['Energy use_MJ_m']       # MJ/m

# get co2e valuation for year 
   co2_price = co2e[co2e['Year'] == year]['CO2_Valuation (SEK/kg Co2e)'].values[0]

#convert energy use to co2e - emissions 
   emission_factor = share_electricity * EF_ELECTRICITY + (1 - share_electricity) * EF_DIESEL
   energy_co2 = energy_use * emission_factor  # kg/m

#total co2e per meter 
   total_co2_per_m = co2_emission + energy_co2  # kg/m

#total cost 
   total_cost = total_co2_per_m * co2_price * track_length  # SEK

   return total_cost

# test 

track_length = 1000                # in meter
asset_type = 'Track'              # or 'Rail'
year = 2025
share_electricity = 0.8           # 80% el, 20% diesel

# Anropa funktionen
cost = get_LCA_renewal(track_length, asset_type, year, share_electricity)

# Skriv ut resultatet
print(f"Total LCA renewal cost for {asset_type} in year {year} with {share_electricity*100:.0f}% electricity: {cost:.2f} SEK")