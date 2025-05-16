from scipy.interpolate import PchipInterpolator  # type: ignore
from rail_analysis.rail_measures import get_table

SELECTED_PROFILE = 'MB4'  
SELECTED_GAUGE_WIDENING = 1  
SELECTED_RADIUS = '1465'

DR = 0.04
TRACK_LEN = 1000
TECH_LIFE_Y = 30 
MAX_MONTHS = TECH_LIFE_Y * 12

C_POSS = 50293
C_GRIND = 50
C_TAMP  = 40
T_GRIND_HR = 2
T_TAMP_HR  = 5

H_MAX = 14
RCF_MAX = 0.5# just for testing, but the real value is 0.5 mm

TRACK_RENEW = 6500 * TRACK_LEN
RAIL_RENEW  = 1500 * TRACK_LEN


def calculate_grinding_costs(rail, freq, since, gauge, H_curr, RCF_curr, Ht, NW, RRes, RDep, gauge_levels, t):
    """
    Calculate grinding costs and update H-index and RCF values for a rail.
    """
    ΔN = PchipInterpolator(gauge_levels, NW[NW['Month'] == since]['Value'])(gauge)

    if since == freq:
        # Add grinding cost including capacity cost
        grinding_cost = (C_GRIND * TRACK_LEN) / (1 + DR) ** t
        capacity_cost = (T_GRIND_HR * C_POSS) / (1 + DR) ** t

        # Update H-index using H-index table (minus natural wear)
        ΔH_g = PchipInterpolator(gauge_levels, Ht[Ht['Month'] == freq]['Value'])(gauge)
        H_curr += ΔH_g - ΔN

        # Update RCF using RCF-residual
        rcf_r = PchipInterpolator(gauge_levels, RRes[RRes['Month'] == freq]['Value'])(gauge)
        if rcf_r > 0:
            RCF_curr += rcf_r

        since = 0
    else:
        # Update H-index using natural wear
        H_curr += ΔN

        # Update RCF using RCF-depth
        ΔR = PchipInterpolator(gauge_levels, RDep[RDep['Month'] == since]['Value'])(gauge)
        RCF_curr += ΔR

        grinding_cost = capacity_cost = 0

    return grinding_cost, capacity_cost, H_curr, RCF_curr, since + 1


def calculate_tamping_costs(since_tamp, gauge_freq, gauge, t):
    """
    Calculate tamping costs and reset gauge if needed.
    """
    if since_tamp == gauge_freq:
        tamping_cost = (C_TAMP * TRACK_LEN) / (1 + DR) ** t
        capacity_cost = (T_TAMP_HR * C_POSS) / (1 + DR) ** t
        gauge = 1440
        since_tamp = 0
    else:
        tamping_cost = capacity_cost = 0

    return tamping_cost, capacity_cost, gauge, since_tamp + 1


def handle_double_grinding(rail, since_attr, gauge, H_curr, RCF_curr, gauge_levels, t, Ht_H):
    """
    Handle double grinding if RCF exceeds the maximum threshold.
    """
    if RCF_curr >= RCF_MAX:
        # Add milling costs (less than double grinding costs)
        milling_cost = (5 / 3 * C_GRIND * TRACK_LEN) / (1 + DR) ** t
        capacity_cost = (5 / 3 * T_GRIND_HR * C_POSS) / (1 + DR) ** t

        # Update H-index using H-index table (twice)
        ΔH1 = PchipInterpolator(gauge_levels, Ht_H[Ht_H['Month'] == since_attr + 1]['Value'])(gauge)
        ΔH2 = PchipInterpolator(gauge_levels, Ht_H[Ht_H['Month'] == 1]['Value'])(gauge)
        H_curr += ΔH1 + ΔH2

        # Reset RCF to zero and months since grinding
        RCF_curr = 0
        since_attr = 1
    else:
        milling_cost = capacity_cost = 0

    return milling_cost, capacity_cost, H_curr, RCF_curr, since_attr


def handle_rail_renewal(H_curr, RCF_curr, t):
    """
    Handle rail renewal if the H-index exceeds the maximum threshold.
    """
    if H_curr > H_MAX:
        renewal_cost = RAIL_RENEW / (1 + DR) ** t
        H_curr, RCF_curr = 0, 0
    else:
        renewal_cost = 0

    return renewal_cost, H_curr, RCF_curr


def get_annuity_track_refactored(
    data_df,
    grinding_freq_low,
    grinding_freq_high,
    gauge_freq,
    profile_low_rail=SELECTED_PROFILE,
    profile_high_rail=SELECTED_PROFILE,
    track_results=False,
    gauge_widening_per_year=SELECTED_GAUGE_WIDENING,
    radius=SELECTED_RADIUS,
):
    """
    Refactored version of get_annuity_track using helper functions.
    """
    data_df_radius = data_df[data_df['Radius'] == radius]

    # --- LOAD TABLES ---
    Ht_H = get_table(data_df_radius, 'h-index', profile=profile_high_rail, rail='High', radius=radius)
    Ht_L = get_table(data_df_radius, 'h-index', profile=profile_low_rail, rail='Inner', radius=radius)
    NW_H = get_table(data_df_radius, 'wear', profile=profile_high_rail, rail='High', radius=radius)
    NW_L = get_table(data_df_radius, 'wear', profile=profile_low_rail, rail='Inner', radius=radius)
    RCF_RES_H = get_table(data_df_radius, 'rcf-residual', profile=profile_high_rail, rail='High', radius=radius)
    RCF_RES_L = get_table(data_df_radius, 'rcf-residual', profile=profile_low_rail, rail='Inner', radius=radius)
    RCF_DEP_H = get_table(data_df_radius, 'rcf-depth', profile=profile_high_rail, rail='High', radius=radius)
    RCF_DEP_L = get_table(data_df_radius, 'rcf-depth', profile=profile_low_rail, rail='Inner', radius=radius)

    gauge_levels = Ht_H['Gauge'].unique()
    gauge_levels.sort()

    # --- STATE & ACCUMULATORS ---
    PV_maint = 0.0
    PV_renew = 0.0#TRACK_RENEW
    PV_cap = 0.0

    H_H = H_L = 0.0
    R_H = R_L = 0.0
    gauge = gauge_levels[0]

    since_grind_H = since_grind_L = 1
    since_tamp = 1

    history = [] if track_results else None
    lifetime = TECH_LIFE_Y

    # --- SIMULATION LOOP ---
    for m in range(1, MAX_MONTHS + 1):
        t = m / 12
        gauge += gauge_widening_per_year / 12

        # Grinding for each rail
        for rail in ('H', 'L'):
            freq = grinding_freq_high if rail == 'H' else grinding_freq_low
            since = since_grind_H if rail == 'H' else since_grind_L
            H_curr = H_H if rail == 'H' else H_L
            RCF_curr = R_H if rail == 'H' else R_L
            Ht = Ht_H if rail == 'H' else Ht_L
            NW = NW_H if rail == 'H' else NW_L
            RRes = RCF_RES_H if rail == 'H' else RCF_RES_L
            RDep = RCF_DEP_H if rail == 'H' else RCF_DEP_L

            grinding_cost, capacity_cost, H_curr, RCF_curr, since = calculate_grinding_costs(
                rail, freq, since, gauge, H_curr, RCF_curr, Ht, NW, RRes, RDep, gauge_levels, t
            )

            PV_maint += grinding_cost
            PV_cap += capacity_cost

            if rail == 'H':
                since_grind_H = since
                H_H, R_H = H_curr, RCF_curr
            else:
                since_grind_L = since
                H_L, R_L = H_curr, RCF_curr

        # Tamping
        tamping_cost, capacity_cost, gauge, since_tamp = calculate_tamping_costs(since_tamp, gauge_freq, gauge, t)
        PV_maint += tamping_cost
        PV_cap += capacity_cost

        # Double grinding
        for rail, since_attr in (('H', 'since_grind_H'), ('L', 'since_grind_L')):
            RCF_curr = R_H if rail == 'H' else R_L
            H_curr = H_H if rail == 'H' else H_L
            since = locals()[since_attr]

            milling_cost, capacity_cost, H_curr, RCF_curr, since = handle_double_grinding(
                rail, since, gauge, H_curr, RCF_curr, gauge_levels, t, Ht_H if rail == 'H' else Ht_L
            )

            PV_maint += milling_cost
            PV_cap += capacity_cost

            if rail == 'H':
                H_H, R_H = H_curr, RCF_curr
                since_grind_H = since
            else:
                H_L, R_L = H_curr, RCF_curr
                since_grind_L = since

        # Rail renewal
        for H_curr, RCF_curr, name in ((H_H, R_H, 'H'), (H_L, R_L, 'L')):
            renewal_cost, H_curr, RCF_curr = handle_rail_renewal(H_curr, RCF_curr, t)
            PV_renew += renewal_cost

            if name == 'H':
                H_H, R_H = H_curr, RCF_curr
            else:
                H_L, R_L = H_curr, RCF_curr

        # Check technical track renewal
        if m == MAX_MONTHS:
            lifetime = t
            # add track renewal costs
            PV_renew += TRACK_RENEW / (1 + DR) ** t
            break

        if track_results:
            history.append({
                'Month': m, 'H_H': H_H, 'RCF_H': R_H,
                'H_L': H_L, 'RCF_L': R_L, 'Gauge': gauge
            })

    # Compute annuity
    total_PV = PV_maint + PV_cap + PV_renew
    annuity = total_PV / TRACK_LEN / lifetime

    return (annuity, lifetime, history) if track_results else (annuity, lifetime)