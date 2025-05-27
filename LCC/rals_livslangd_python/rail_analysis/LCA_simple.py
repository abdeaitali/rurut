import pandas as pd

# Default values
DEFAULT_SHARE_EL = 0.4  # 40% electricity
DEFAULT_CIRCULARITY_COEF = 0.2  # 20% circularity

# Emission factors kg CO2e per MJ
EF_ELECTRICITY = 0.006464924
EF_DIESEL = 0.063583815

def get_LCA_renewal_simple(
    asset_type,
    year=2019,
    circularity_coef=DEFAULT_CIRCULARITY_COEF,
    share_electricity=DEFAULT_SHARE_EL,
    track_length=1000,
    return_per_meter=False
):
   """
   Calculate the LCA cost of renewal for a given asset type and year.

   Parameters:
      asset_type (str): 'Rail' or 'Track'
      year (int): Year for CO2 valuation
      circularity_coef (float): Fraction of circularity (0-1)
      share_electricity (float): Fraction of electricity use (0-1)
      length (float): Length in meters (default TRACK_LENGTH)
      return_per_meter (bool): If True, return cost per meter, else total cost

   Returns:
      float: LCA renewal cost (SEK) for the given length or per meter
   """
   # Paths
   base_path = r'c:\Users\AbdouAA\Work Folders\Documents\GitHub\rurut\LCC\rals_livslangd_python\data\raw\LCA\\'
   lca_data = pd.read_csv(base_path + 'LCA_indata_EF.csv', delimiter=';', encoding='utf-8')
   co2e_data = pd.read_csv(base_path + 'co2_valuation.csv', delimiter=';', encoding='utf-8')

   # Clean up data: replace ',' with '.' and convert to float where needed
   for df in [lca_data, co2e_data]:
      for col in df.columns:
         if df[col].dtype == object:
               df[col] = df[col].str.replace(',', '.', regex=False)

   # get the costs of renewal for the given asset type
   # Select the row for the given asset_type and keep only 'CO2 (kg)' and 'Energy (Gj)' columns
   lca_row = lca_data[
      (lca_data['Asset'].str.lower() == asset_type.lower()) &
      (lca_data['Phase'].str.lower() == "reinvestment / year".lower())
   ][['CO2e (kg)', 'Energy (GJ)', 'Quantity (in meter)']]

   # calculate the CO2 emissions from energy use
   # Convert 'Energy (GJ)' and 'CO2e (kg)' to per meter using 'Quantity (in meter)'
   lca_row['Energy use_MJ_m'] = lca_row['Energy (GJ)'].astype(float) * 1000 / lca_row['Quantity (in meter)'].astype(float)
   lca_row['CO2 emissions_kg/m'] = lca_row['CO2e (kg)'].astype(float) / lca_row['Quantity (in meter)'].astype(float)

   # Convert energy use to CO2e emissions
   emission_factor = share_electricity * EF_ELECTRICITY + (1 - share_electricity) * EF_DIESEL
   energy_co2 = lca_row['Energy use_MJ_m'] * emission_factor  # kg/m

   # Total CO2e per meter
   total_co2_per_m = float((lca_row['CO2 emissions_kg/m'] + energy_co2).values[0])  # kg/m

   # Total cost per meter
   co2_price = float(co2e_data[co2e_data['Year'] == year]['CO2_Valuation (kr/kg Co2e)'].values[0])  # Get CO2e valuation for the year
   cost_per_meter = total_co2_per_m * co2_price  # SEK/m

   # Apply circularity
   cost_per_meter = cost_per_meter * (1 - circularity_coef)

   if return_per_meter:
      return cost_per_meter
   else:
      return cost_per_meter * track_length