### The goal is to create a more plausible input data file based on mistra_results
### Plausible here means using the following
###     1. Some values from the mistra_results, not between month 1-6
###     2. At month 0, we have no increase in H, i.e., H_index = 0
###     3. The average monthly increase should increase with higher gauge and nb. months since last grinding

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Given data
data = {
    "Track Gauge": ["1440", "1445", "1450", "1455"],
    "Month1": [np.nan] * 4,
    "Month2": [np.nan] * 4,
    "Month3": [np.nan] * 4,
    "Month4": [np.nan] * 4,
    "Month5": [np.nan] * 4,
    "Month6": [np.nan] * 4,
    "Month7": [0.74, 0.89, 0.895, 0.9],
    "Month8": [0.85, 0.98, 0.98, 0.98],
    "Month9": [0.88, 0.99, 0.99, 0.99],
    "Month10": [0.92, 0.98, 1.03, 1.11],
    "Month11": [0.95, 1.06, 1.12, 1.2],
    "Month12": [1.04, 1.14, 1.2, 1.27],
    "Month13": [np.nan] * 4,
    "Month14": [np.nan] * 4,
    "Month15": [np.nan] * 4,
    "Month16": [np.nan] * 4,
    "Month17": [np.nan] * 4,
    "Month18": [np.nan] * 4
}

df = pd.DataFrame(data)

# Function to interpolate values for months 1 to 6 using all available values between month 7 and 12
def interpolate_values(df):
    for i in range(len(df)):
        x_known = list(range(0, 13))  # Include month 0 and months 7 to 12
        y_known = [0] + df.iloc[i, 6:12].tolist()  # Start with value at month 0 and include months 7 to 12
        
        print("Length of x_known:", len(x_known))
        print("Length of y_known:", len(y_known))
        
        interpolator = interp1d(x_known, y_known, kind='linear', fill_value="extrapolate")
        
        interpolated_values = interpolator(np.arange(1, 7))
        df.iloc[i, 1:7] = interpolated_values
    return df

# Define function to maximize average monthly increase
def maximize_increase(df):
    for i in range(len(df)):
        gauge = int(df.iloc[i, 0])
        for j in range(6, len(df.columns)-1):
            if pd.isna(df.iloc[i, j + 1]):
                # Increase by a percentage based on gauge and number of months since last grinding
                df.iloc[i, j + 1] = df.iloc[i, j] * (1 + (gauge - 1440) * 0.001) * (1 + (j - 5) * 0.01)
    return df

# Interpolate values for months 1 to 6 and maximize increase
df_interpolated = interpolate_values(df.copy())
df_final = maximize_increase(df_interpolated)

# Plot df_final for different gauges over months
plt.figure(figsize=(10, 6))
for index, row in df_final.iterrows():
    plt.plot(range(1, 19), row[1:], marker='o', label=f'Track Gauge {row["Track Gauge"]}')
plt.title('Monthly Increase for Different Gauges')
plt.xlabel('Month')
plt.ylabel('Increase')
plt.legend()
plt.grid(True)
plt.xticks(range(1, 19))
plt.show()

