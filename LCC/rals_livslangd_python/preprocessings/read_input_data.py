import pandas as pd  # type: ignore

def read_input_data(file_path):
    """
    Reads input data from a CSV file with the specified structure
    and returns it as a Pandas DataFrame.

    Parameters:
    file_path (str): The path to the CSV file.

    Returns:
    pandas.DataFrame: A DataFrame containing the data.
    """
    try:
        # Read the CSV file, handling semicolon as a delimiter
        data = pd.read_csv(file_path, delimiter=";", encoding="utf-8")

        # Replace comma decimal separators with dots for numerical columns
        for col in data.columns[4:]:  # Start from 'month 1'
            data[col] = data[col].str.replace(',', '.').astype(float)

        # do the same for the 'Load' column
        data['Load'] = data['Load'].str.replace(',', '.').astype(float)

        # Reshape the DataFrame so that months are in one column
        data_melted = data.melt(
            id_vars=['Profile', 'Load','Condition', 'Gauge'], 
            value_vars=[f'month {i}' for i in range(1, 13)], 
            var_name='Month', 
            value_name='Value'
        )

        # Convert the 'Month' column to numeric by extracting the number
        data_melted['Month'] = data_melted['Month'].str.extract('(\d+)').astype(int)

        return data_melted

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None