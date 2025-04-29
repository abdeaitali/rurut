def get_max_lifetime(data):
    """
    Calculate the maximum lifetime from the given data.

    Parameters:
    data (list): A list of lifetime values.

    Returns:
    float: The maximum lifetime value.
    """
    if not data:
        raise ValueError("Data list is empty.")
    
    max_lifetime = max(data)
    return max_lifetime

def main():
    # Example usage
    sample_data = [10, 20, 30, 40, 50]
    max_lifetime = get_max_lifetime(sample_data)
    print(f"The maximum lifetime is: {max_lifetime}")

if __name__ == "__main__":
    main()