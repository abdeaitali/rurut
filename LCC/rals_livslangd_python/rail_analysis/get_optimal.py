def get_optimal_solution(data, criteria):
    """
    Function to find the optimal solution based on the defined criteria.
    
    Parameters:
    data (list): A list of data points to evaluate.
    criteria (function): A function that defines the criteria for optimality.
    
    Returns:
    optimal_solution: The solution that meets the optimal criteria.
    """
    optimal_solution = None
    optimal_value = float('inf')  # Assuming we are minimizing the criteria

    for point in data:
        value = criteria(point)
        if value < optimal_value:
            optimal_value = value
            optimal_solution = point

    return optimal_solution

def example_criteria(point):
    """
    Example criteria function for demonstration purposes.
    
    Parameters:
    point: A data point to evaluate.
    
    Returns:
    float: A value representing the evaluation of the point.
    """
    # Replace with actual criteria logic
    return point['cost']  # Assuming point is a dictionary with a 'cost' key

# Example usage
if __name__ == "__main__":
    sample_data = [
        {'cost': 100, 'other_metric': 5},
        {'cost': 80, 'other_metric': 10},
        {'cost': 120, 'other_metric': 3},
    ]
    
    optimal = get_optimal_solution(sample_data, example_criteria)
    print("Optimal solution:", optimal)