from scipy.interpolate import PchipInterpolator  # type: ignore
from rail_analysis.rail_measures import get_table



# --- PARAMETERS ---

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


def get_annuity_track(
    data_df,
    grinding_freq_low,     # grinding interval (months) for low rail 
    grinding_freq_high,    # grinding interval (months) for high rail 
    gauge_freq,            # tamping interval (months)
    profile_low_rail=SELECTED_PROFILE,
    profile_high_rail=SELECTED_PROFILE,
    track_results=False,
    gauge_widening_per_year=SELECTED_GAUGE_WIDENING, 
    radius=SELECTED_RADIUS,  # radius of curvature (not used in this function)
):
    """
    Calculate the annuity (LCC per year) and track lifetime for both rails.

    Returns:
      (annuity, lifetime, [optional] history)
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
    PV_renew = 0.0#TRACK_RENEW # TODO: add LCA
    PV_cap   = 0.0

    H_H = H_L = 0.0
    R_H = R_L = 0.0
    gauge = gauge_levels[0]

    since_grind_H = since_grind_L = 1
    since_tamp        = 1

    history = [] if track_results else None
    lifetime = TECH_LIFE_Y

    # --- SIMULATION LOOP ---
    for m in range(1, MAX_MONTHS + 1):
        t = m / 12
        gauge += gauge_widening_per_year / 12

        # --- Grinding for each rail ---
        for rail in ('H','L'):
            freq = grinding_freq_high if rail=='H' else grinding_freq_low
            since = since_grind_H if rail=='H' else since_grind_L
            H_curr = H_H if rail=='H' else H_L
            RCF_curr = R_H if rail=='H' else R_L
            Ht = Ht_H if rail=='H' else Ht_L
            NW = NW_H if rail=='H' else NW_L
            RRes = RCF_RES_H if rail=='H' else RCF_RES_L
            RDep = RCF_DEP_H if rail=='H' else RCF_DEP_L

            # natural wear
            ΔN   = PchipInterpolator(gauge_levels, NW[NW['Month']==since]['Value'])(gauge)
            
            # check if grinding is scheduled
            if since == freq:
                # add grinding cost including capacity cost # TODO: may also add LCA
                PV_maint += (C_GRIND*TRACK_LEN)/(1+DR)**t
                PV_cap   += (T_GRIND_HR*C_POSS)/(1+DR)**t

                # update H-index using H-index table (minus natural wear)
                ΔH_g = PchipInterpolator(gauge_levels, Ht[Ht['Month']==freq]['Value'])(gauge)
                H_curr += ΔH_g - ΔN

                # update RCF using RCF-residual
                rcf_r = PchipInterpolator(gauge_levels, RRes[RRes['Month']==freq]['Value'])(gauge)
                if rcf_r>0:
                    RCF_curr += rcf_r

                # update months since grinding
                since = 0
            else:
                # update H-index using natural wear
                H_curr += ΔN

                # update RCF using RCF-depth
                ΔR = PchipInterpolator(gauge_levels, RDep[RDep['Month']==since]['Value'])(gauge)
                RCF_curr += ΔR

            # save back
            if rail=='H':
                since_grind_H = since+1
                H_H, R_H      = H_curr, RCF_curr
            else:
                since_grind_L = since+1
                H_L, R_L      = H_curr, RCF_curr

        # --- Gauge correction (tamping) ---
        if since_tamp == gauge_freq:
            # add tamping cost including capacity cost # TODO: may also add LCA
            PV_maint += (C_TAMP*TRACK_LEN)/(1+DR)**t
            PV_cap   += (T_TAMP_HR*C_POSS)/(1+DR)**t
            # update gauge
            gauge     = gauge_levels[0]
            # update months since tamping
            since_tamp= 0
        since_tamp += 1

        # --- Double grind if RCF excess ---
        for rail, since_attr in (('H', 'since_grind_H'), ('L','since_grind_L')):
            RCF_curr = R_H if rail=='H' else R_L
            H_curr = H_H if rail=='H' else H_L
            since   = locals()[since_attr]

            if RCF_curr >= RCF_MAX:
                # add milling costs (less than double grinding costs) # TODO: may also add LCA
                PV_maint += (5/3*C_GRIND*TRACK_LEN)/(1+DR)**t
                PV_cap   += (5/3*T_GRIND_HR*C_POSS)/(1+DR)**t

                # update H-index using H-index table (twice)
                ΔH1 = PchipInterpolator(gauge_levels, Ht_H[Ht_H['Month']==since+1]['Value'])(gauge)
                ΔH2 = PchipInterpolator(gauge_levels, Ht_H[Ht_H['Month']==1]['Value'])(gauge)
                H_curr += ΔH1 + ΔH2

                # reset RCF to zero and months since grinding
                RCF_curr  = 0
                since   = 1

            # save back
            if rail=='H':
                H_H, R_H = H_curr, RCF_curr
                since_grind_H = since
            else:
                H_L, R_L = H_curr, RCF_curr
                since_grind_L = since

        # --- Rail renewal if worn out ---
        for H_curr, RCF_curr, name in ((H_H,R_H,'H'),(H_L,R_L,'L')):
            if H_curr > H_MAX:
                # add rail renewal costs # TODO: may also add LCA
                PV_renew += RAIL_RENEW/(1+DR)**t
                # reset H-index and RCF to zero (new rail)
                if name=='H': H_H, R_H = 0,0
                else:         H_L, R_L = 0,0

        # --- Check technical track renewal ---
        if m == MAX_MONTHS:
            lifetime = t
            # add track renewal costs # TODO: may also add LCA
            PV_renew += TRACK_RENEW/(1+DR)**t
            break

        if track_results:
            history.append({
                'Month':m, 'H_H':H_H,'RCF_H':R_H,
                'H_L':H_L,'RCF_L':R_L,'Gauge':gauge
            })

    # --- Compute annuity ---
    total_PV = PV_maint + PV_cap + PV_renew
    annuity = total_PV / TRACK_LEN / lifetime

    return (annuity, lifetime, history) if track_results else (annuity, lifetime)


import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

def plot_historical_data(historical_data):
    """
    Plots the historical data for H_index and RCF_residual for both high and low rails, and Gauge over time.

    Parameters:
    - historical_data: List of dictionaries containing historical data with keys 'Month', 'H_H', 'RCF_H', 'H_L', 'RCF_L', and 'Gauge'.
    """

    historical_df = pd.DataFrame(historical_data)

    # figure size
    fig_size = (10, 5)

    # Plot H_index for high and low rails
    plt.figure(figsize=fig_size)
    sns.lineplot(data=historical_df, x='Month', y='H_H', label='H_index High Rail', marker='o')
    sns.lineplot(data=historical_df, x='Month', y='H_L', label='H_index Low Rail', marker='o')
    plt.title('Historical H_index Values (High and Low Rails)')
    plt.xlabel('Month')
    plt.ylabel('H_index')
    plt.legend()
    plt.grid()
    plt.show()

    # Plot RCF_residual for high and low rails
    plt.figure(figsize=fig_size)
    sns.lineplot(data=historical_df, x='Month', y='RCF_H', label='RCF High Rail', marker='o')
    sns.lineplot(data=historical_df, x='Month', y='RCF_L', label='RCF Low Rail', marker='o')
    plt.title('Historical RCF Values (High and Low Rails)')
    plt.xlabel('Month')
    plt.ylabel('RCF')
    plt.legend()
    plt.grid()
    plt.show()

    # Plot Gauge
    plt.figure(figsize=fig_size)
    sns.lineplot(data=historical_df, x='Month', y='Gauge', label='Gauge', marker='o')
    plt.title('Historical Gauge Values')
    plt.xlabel('Month')
    plt.ylabel('Gauge')
    plt.grid()
    plt.show()

