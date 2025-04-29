def calculate_life_cycle_cost(initial_cost, maintenance_cost, operational_cost, lifespan):
    """
    Calculate the Life Cycle Cost (LCC) based on input parameters.

    Parameters:
    initial_cost (float): The initial cost of the project or asset.
    maintenance_cost (float): The total maintenance cost over the lifespan.
    operational_cost (float): The total operational cost over the lifespan.
    lifespan (int): The expected lifespan of the asset in years.

    Returns:
    float: The total Life Cycle Cost.
    """
    total_lcc = initial_cost + maintenance_cost + operational_cost
    return total_lcc


def calculate_lcc_with_discount(initial_cost, maintenance_cost, operational_cost, lifespan, discount_rate):
    """
    Calculate the discounted Life Cycle Cost (LCC) over the lifespan.

    Parameters:
    initial_cost (float): The initial cost of the project or asset.
    maintenance_cost (float): The total maintenance cost over the lifespan.
    operational_cost (float): The total operational cost over the lifespan.
    lifespan (int): The expected lifespan of the asset in years.
    discount_rate (float): The discount rate for present value calculations.

    Returns:
    float: The discounted Life Cycle Cost.
    """
    total_lcc = calculate_life_cycle_cost(initial_cost, maintenance_cost, operational_cost, lifespan)
    discounted_lcc = total_lcc / ((1 + discount_rate) ** lifespan)
    return discounted_lcc