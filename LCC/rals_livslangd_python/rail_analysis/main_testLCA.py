
import pandas as pd

from LCA import get_LCA_renewal

if __name__ == "__main__":
    track_length = 1000
    asset_type = 'Track'
    year = 2025
    share_electricity = 0.8
    circularity_coefficient = 0.2  # Lägg till denna rad

    cost = get_LCA_renewal(track_length, asset_type, year, share_electricity, circularity_coefficient)
    print(
        f"Total LCA renewal cost for {asset_type} in {year} "
        f"with {share_electricity*100:.0f}% electricity and {circularity_coefficient*100:.0f}% circularity: "
        f"{cost:.2f} SEK"
    )
