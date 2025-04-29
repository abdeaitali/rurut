# rals_livslangd_python

## Project Overview
The `rals_livslangd_python` project is a Python implementation of the MATLAB project `räls_livslängd`. This project focuses on analyzing life cycle costs (LCC) and related metrics for various components and systems. It includes modules for data processing, graph creation, and result visualization.

## Project Structure
```
rals_livslangd_python/
├── src/
│   ├── create_graph.py          # Functions to create graphs based on processed data
│   ├── get_lcc.py               # Functions to calculate Life Cycle Cost (LCC)
│   ├── get_lifetime.py          # Functions to determine the lifetime of components
│   ├── get_max_lifetime.py      # Functions to compute the maximum lifetime
│   ├── get_optimal.py           # Functions to find optimal solutions
│   ├── interpolation.py          # Functions for interpolating data points
│   ├── lifetimes.py              # Functions related to managing lifetimes
│   ├── main_gauge.py            # Main entry point for gauge-related calculations
│   ├── main_MB5_RCF.py          # Main script for the MB5 RCF project
│   ├── main_MB5.py              # Main script for the MB5 project
│   ├── main.py                  # Main entry point for the entire project
│   ├── plot_figure.py           # Functions for plotting figures and visualizing data
│   ├── read_input_data.py       # Functions to read and process input data
│   ├── test_interp.py           # Test functions for validating interpolation methods
│   └── Wear/
│       ├── data.csv             # Data related to wear for analysis
│       ├── main.py              # Main script for wear analysis
│       ├── mistra_results_artificial.xlsx  # Artificial results for mistra analysis
│       ├── mistra_results - no risk.xlsx   # Mistra results with no risk considerations
│       ├── mistra_results.xlsx   # Main mistra results
│       └── archive/
│           ├── mistra_results - kopia.xlsx  # Copy of mistra results for archival
│           └── mistra_results.xlsx          # Archived version of main mistra results
├── requirements.txt              # Lists dependencies required for the project
└── README.md                     # Documentation for the project
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
- **create_graph.py**: Contains functions to create visual representations of data.
- **get_lcc.py**: Implements calculations for life cycle costs.
- **get_lifetime.py**: Provides methods to assess the lifespan of components.
- **get_max_lifetime.py**: Computes the maximum lifetime based on input data.
- **get_optimal.py**: Finds optimal solutions based on defined criteria.
- **interpolation.py**: Offers functions for data interpolation.
- **lifetimes.py**: Manages calculations related to component lifetimes.
- **main_gauge.py**: Entry point for gauge-related calculations.
- **main_MB5_RCF.py**: Handles specific calculations for the MB5 RCF project.
- **main_MB5.py**: Focuses on calculations for the MB5 project.
- **main.py**: The main script that coordinates the project execution.
- **plot_figure.py**: Functions for data visualization.
- **read_input_data.py**: Reads and processes input data.
- **test_interp.py**: Validates interpolation methods.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.