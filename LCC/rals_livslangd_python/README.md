# rals_livslangd_python

## Project Overview
The `rals_livslangd_python` project is a Python implementation of the MATLAB project `räls_livslängd`. This project focuses on analyzing life cycle costs (LCC) and related metrics for railway tracks. It includes modules for data processing, graph creation, and result visualization, as well as tools for calculating optimal maintenance strategies and track lifetime.

## Project Structure
```
rals_livslangd_python/
├── main.py                      # Main script for  analysis
├── README.md                    # Documentation for the project
├── requirements.txt             # Lists dependencies required for the project
├── archived/                    # Archived scripts and data
├── data/                        # Data-related files
│   ├── raw/                     # Raw input data
│   └── processed/               # Processed data files
├── notebooks/                   # Jupyter notebooks for analysis and testing
├── figures/                     # Output figures and results
├── preprocessings/              # Preprocessing scripts for data preparation
├── rail_analysis/               # Core analysis modules
│   ├── LCC.py                   # Functions for LCC calculations
│   ├── rail_measures.py         # Functions for rail wear and RCF analysis
```

## Installation
To set up the project, clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd rals_livslangd_python
pip install -r requirements.txt
```

## Usage
To run the main script, execute the following command:

```bash
python src/main.py
```

This will coordinate the execution of various modules and provide the desired analysis.

## Modules Description
- **main.py**: Main script for analysis.
- **rail_analysis/LCC.py**: Implements calculations for life cycle costs, including the `get_annuity` function for LCC and track lifetime estimation.
- **rail_analysis/rail_measures.py**: Provides functions for analyzing rail wear, RCF residuals, and other rail-related metrics.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.