#from rail_analysis.LCA_simple import get_LCA_renewal_simple
from rail_analysis.LCA import get_LCA_renewal


# === GLOBAL PARAMETERS ===

# default selected scenarios
SELECTED_PROFILE = 'MB4'  
SELECTED_GAUGE_WIDENING = 1 
SELECTED_RADIUS = '1465'


# annual million gross tonnes (MGT) for the track (used for plotting lifetimes together with months)
ANNUAL_MGT = 35

# discount rate for the annuity calculation
DISCOUNT_RATE = 0.04


# lenth of the track in meters
TRACK_LENGTH_M = 1000

# technical life of the track in yearsc, i.e., the simulation time
TECH_LIFE_YEARS = 30
MAX_MONTHS = 12 * TECH_LIFE_YEARS

# capacity possession per hour
CAP_POSS_PER_HOUR = 50293 # TODO: sensivitivity analysis for this value, currently set to 50293 SEK per hour!

# costs for the different maintenance activities per meter
TAMPING_COST_PER_M = 40
GRINDING_COST_PER_M = 60 # 60 SEK per meter (PO after meeting on 2025-05), previous value was 50 SEK per meter

# capacity possession for grinding and gauge correction (tamping) and milling
POSS_GRINDING = 2 # TRACK_LENGTH_M/3000 # 3 km per h, ref. https://www.charmec.chalmers.se/innotrack/deliverables/sp4/d455-f3-guidelines_for_management_of_rail_grinding.pdf
POSS_TAMPING = 5
POSS_GRINDING_TWICE = POSS_GRINDING * 5 / 3

# cost of renewing the track, i.e., both rails and sleepers
TRACK_RENEWAL_COST = 6500 * TRACK_LENGTH_M + TECH_LIFE_YEARS*get_LCA_renewal('Track', track_length=TRACK_LENGTH_M)

# cost of renewing a single rail
RAIL_RENEWAL_COST = 1500 * TRACK_LENGTH_M

# rail renewal time in hours for TRACK_LENGTH_M, i.e., 40 meter rail per hour from
POSS_NEW_RAIL = TRACK_LENGTH_M/40

# starting gauge level for the track
INIT_GAUGE_LEVEL = 1440

# maximum H value for the rail before renewal is triggered
H_MAX = 14
# maximum RCF value for the rail before double grinding (milling) is triggered
RCF_MAX = 0.5