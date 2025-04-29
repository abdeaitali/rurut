def interpolate_data(x, y, new_x):
    """
    Interpolates the data points using linear interpolation.

    Parameters:
    x (list): The x-coordinates of the data points.
    y (list): The y-coordinates of the data points.
    new_x (list): The x-coordinates where interpolation is to be performed.

    Returns:
    list: Interpolated y-coordinates corresponding to new_x.
    """
    from scipy.interpolate import interp1d

    # Create the interpolation function
    interpolation_function = interp1d(x, y, kind='linear', fill_value='extrapolate')

    # Perform the interpolation
    new_y = interpolation_function(new_x)

    return new_y

def main():
    # Example usage of the interpolation function
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    new_x = [0.5, 1.5, 2.5, 3.5]

    interpolated_values = interpolate_data(x, y, new_x)
    print("Interpolated values:", interpolated_values)

if __name__ == "__main__":
    main()