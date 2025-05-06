import pandas as pd

# Define the tonnage
tonnage = "H_32t"  # Standard axle load (30 tons), alternatively "H_32t" for heavy axle load (32.5 tons)

# Define the rail profile
rail_profile = "MB5"  # MB5 or MB6

# The actual path to your Excel file
file_path = './data/raw/raw_data_structured.csv'


# Call the function to read the data
data_df = read_input_data(file_path)
data_df

if data_df is not None:
    grinding_freq_max = 12

    # Example calls to the interpolation function
    h_index_interp = interpolate_rail_data(data_df, grinding_freq_max, 'H-index')
    print("\nH-index Interpolation:")
    if not h_index_interp.empty:
        print(h_index_interp)
    else:
        print("No H-index data to interpolate.")

    # wear_interp = interpolate_rail_data(data_df, grinding_freq_max, 'Wear')
    # print("\nWear Interpolation:")
    # if not wear_interp.empty:
    #     print(wear_interp)
    # else:
    #     print("No Wear data to interpolate.")

    # rcf_residual_interp = interpolate_rail_data(data_df, grinding_freq_max, 'RCF-residual')
    # print("\nRCF-residual Interpolation")
    # if not rcf_residual_interp.empty:
    #     print(rcf_residual_interp)
    # else:
    #     print("No RCF-residual data to interpolate")

    # rcf_depth_interp = interpolate_rail_data(data_df, grinding_freq_max, 'RCF-depth')
    # print("\n RCF-depth interpolation")
    # if not rcf_depth_interp.empty:
    #     print(rcf_depth_interp)
    # else:
    #     print("No RCF-depth data to interpolate")
else:
    print("Failed to load data.")