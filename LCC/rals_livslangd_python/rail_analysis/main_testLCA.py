
from LCA import get_LCA_renewal

if __name__ == "__main__":
    track_length = 1000
    asset_type = 'Track'
    year = 2025
    share_electricity = 0.8

    cost = get_LCA_renewal(track_length, asset_type, year, share_electricity)
    print(f"Total LCA renewal cost for {asset_type} in {year} with {share_electricity*100:.0f}% electricity: {cost:.2f} SEK")