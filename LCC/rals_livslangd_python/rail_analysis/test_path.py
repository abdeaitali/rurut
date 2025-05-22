import pandas as pd
import os

my_abs_path = r'C:\Users\EmmaFrom\Work Folders\Documents\GitHub\rurut\LCC\rurut\LCC\rals_livslangd_python\data\raw\LCA'
filepath = os.path.join(my_abs_path, 'lca_base_data.csv')

print("Reading:", filepath)
df = pd.read_csv(filepath, delimiter=';', encoding='utf-8')
print(df.head())