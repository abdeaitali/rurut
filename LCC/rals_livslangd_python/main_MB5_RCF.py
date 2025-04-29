# Contents of /rals_livslangd_python/rals_livslangd_python/src/main_MB5_RCF.py

import numpy as np
import pandas as pd
from get_lcc import calculate_lcc
from get_lifetime import determine_lifetime
from plot_figure import plot_results

def main():
    # Load input data
    input_data = pd.read_csv('Wear/data.csv')
    
    # Perform calculations
    lcc = calculate_lcc(input_data)
    lifetime = determine_lifetime(input_data)
    
    # Plot results
    plot_results(lcc, lifetime)

if __name__ == "__main__":
    main()