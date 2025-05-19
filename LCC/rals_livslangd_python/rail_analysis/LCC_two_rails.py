from scipy.interpolate import PchipInterpolator  # type: ignore
from rail_analysis.rail_measures import get_table
from rail_analysis.constants import (
    H_MAX,
    RAIL_RENEWAL_COST,
    RCF_MAX,
    TAMPING_COST_PER_M,
    GRINDING_COST_PER_M,
    POSS_TAMPING,
    POSS_GRINDING,
    POSS_GRINDING_TWICE,
    TRACK_RENEWAL_COST,
    CAP_POSS_PER_HOUR,
    DISCOUNT_RATE,
    TRACK_LENGTH_M,
    SELECTED_PROFILE,
    SELECTED_GAUGE_WIDENING,
    SELECTED_RADIUS,
    TECH_LIFE_YEARS,
    POSS_NEW_RAIL
)
import matplotlib.pyplot as plt

# === HELPER FUNCTIONS ===

def calculate_grinding_costs(freq, since, gauge, H_curr, rcf_r, Ht, NW, RRes, RDep, gauge_levels, t):
    """
    Calculate grinding costs and update H-index and RCF values for a rail.
    """
    ΔN = PchipInterpolator(gauge_levels, NW[NW['Month'] == since]['Value'])(gauge)

    if since == freq:
        # Add grinding cost including capacity cost
        grinding_cost = (GRINDING_COST_PER_M * TRACK_LENGTH_M) / (1 + DISCOUNT_RATE) ** t
        capacity_cost = (POSS_GRINDING * CAP_POSS_PER_HOUR) / (1 + DISCOUNT_RATE) ** t

        # Update H-index using H-index table (minus natural wear)
        ΔH_g = PchipInterpolator(gauge_levels, Ht[Ht['Month'] == freq]['Value'])(gauge)
        H_curr += ΔH_g - ΔN # Double check this with Jonathan!

        # Update RCF using RCF-residual
        rcf_r += PchipInterpolator(gauge_levels, RRes[RRes['Month'] == freq]['Value'])(gauge) # check this !
        RCF_curr = rcf_r
        since = 0
    else:
        # Update H-index using natural wear
        H_curr += ΔN

        # Update RCF using RCF-depth
        ΔR = PchipInterpolator(gauge_levels, RDep[RDep['Month'] == since]['Value'])(gauge)
        RCF_curr = rcf_r + ΔR

        grinding_cost = capacity_cost = 0

    return grinding_cost, capacity_cost, H_curr, RCF_curr, rcf_r, since + 1


def calculate_tamping_costs(since_tamp, gauge_freq, gauge, t):
    """
    Calculate tamping costs and reset gauge if needed.
    """
    if since_tamp == gauge_freq:
        tamping_cost = (TAMPING_COST_PER_M * TRACK_LENGTH_M) / (1 + DISCOUNT_RATE) ** t
        capacity_cost = (POSS_TAMPING * CAP_POSS_PER_HOUR) / (1 + DISCOUNT_RATE) ** t
        gauge = 1440
        since_tamp = 0
    else:
        tamping_cost = capacity_cost = 0

    return tamping_cost, capacity_cost, gauge, since_tamp + 1


def handle_double_grinding(since_attr, gauge, H_curr, RCF_curr, rcf_r, gauge_levels, t, Ht_H):
    """
    Handle double grinding if RCF exceeds the maximum threshold.
    """
    if RCF_curr >= RCF_MAX:
        # Add milling costs (less than double grinding costs)
        milling_cost = (5 / 3 * GRINDING_COST_PER_M * TRACK_LENGTH_M) / (1 + DISCOUNT_RATE) ** t
        capacity_cost = (5 / 3 * POSS_GRINDING * CAP_POSS_PER_HOUR) / (1 + DISCOUNT_RATE) ** t

        # Update H-index using H-index table (twice)
        ΔH1 = PchipInterpolator(gauge_levels, Ht_H[Ht_H['Month'] == since_attr + 1]['Value'])(gauge)
        ΔH2 = PchipInterpolator(gauge_levels, Ht_H[Ht_H['Month'] == 1]['Value'])(gauge)
        H_curr += ΔH1 + ΔH2

        # Reset RCF to zero and months since grinding
        RCF_curr = 0
        rcf_r = 0
        since_attr = 1
    else:
        milling_cost = capacity_cost = 0

    return milling_cost, capacity_cost, H_curr, RCF_curr, rcf_r, since_attr


def handle_rail_renewal(H_curr, RCF_curr, t):
    """
    Handle rail renewal if the H-index exceeds the maximum threshold.
    """
    if H_curr > H_MAX:
        renewal_cost = RAIL_RENEWAL_COST / (1 + DISCOUNT_RATE) ** t
        H_curr, RCF_curr = 0, 0
    else:
        renewal_cost = 0

    return renewal_cost, H_curr, RCF_curr


# === MAIN LCC FUNCTION (REFACTORED) ===

def get_annuity_track_refactored(
    data_df,
    grinding_freq_low,
    grinding_freq_high,
    gauge_freq,
    profile_low_rail=SELECTED_PROFILE,
    profile_high_rail=SELECTED_PROFILE,
    track_results=False,
    gauge_widening_per_year=SELECTED_GAUGE_WIDENING,
    radius=SELECTED_RADIUS, track_life=TECH_LIFE_YEARS, 
    plot_timeline=False,
    verbose=False
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
    PV_maint_H = 0.0
    PV_maint_L = 0.0
    PV_renew_H = 0.0
    PV_renew_L = 0.0
    PV_cap_H = 0.0
    PV_cap_L = 0.0

    PV_tamping = 0.0
    PV_cap_tamping = 0.0

    # Initial renewal cost for the whole track
    #PV_renew_track = TRACK_RENEWAL_COST

    H_H = H_L = 0.0
    R_H = R_L = 0.0
    R_r_H = R_r_L = 0.0
    lifetime_H = lifetime_L = -1
    gauge = gauge_levels[0]

    since_grind_H = since_grind_L = 1
    since_tamp = 1

    history = [] if track_results else None
    renewal_options = []

    MAX_MONTHS = 12 * track_life
    for m in range(1, MAX_MONTHS + 1):
        t = m / 12
        gauge += gauge_widening_per_year / 12

        # Grinding for each rail (costs separated)
        for rail in ('H', 'L'):
            freq = grinding_freq_high if rail == 'H' else grinding_freq_low
            since = since_grind_H if rail == 'H' else since_grind_L
            H_curr = H_H if rail == 'H' else H_L
            RCF_curr = R_H if rail == 'H' else R_L
            rcf_r = R_r_H if rail == 'H' else R_r_L
            Ht = Ht_H if rail == 'H' else Ht_L
            NW = NW_H if rail == 'H' else NW_L
            RRes = RCF_RES_H if rail == 'H' else RCF_RES_L
            RDep = RCF_DEP_H if rail == 'H' else RCF_DEP_L

            grinding_cost, capacity_cost, H_curr, RCF_curr, rcf_r, since = calculate_grinding_costs(
                freq, since, gauge, H_curr, rcf_r, Ht, NW, RRes, RDep, gauge_levels, t
            )

            if rail == 'H':
                PV_maint_H += grinding_cost
                PV_cap_H += capacity_cost
                since_grind_H = since
                H_H, R_H, R_r_H = H_curr, RCF_curr, rcf_r
            else:
                PV_maint_L += grinding_cost
                PV_cap_L += capacity_cost
                since_grind_L = since
                H_L, R_L, R_r_L = H_curr, RCF_curr, rcf_r

        # Tamping (shared)
        tamping_cost, capacity_cost, gauge, since_tamp = calculate_tamping_costs(since_tamp, gauge_freq, gauge, t)
        PV_tamping += tamping_cost
        PV_cap_tamping += capacity_cost

        # Double grinding (costs separated)
        for rail, since_attr in (('H', 'since_grind_H'), ('L', 'since_grind_L')):
            RCF_curr = R_H if rail == 'H' else R_L
            H_curr = H_H if rail == 'H' else H_L
            since = locals()[since_attr]

            milling_cost, capacity_cost, H_curr, RCF_curr, rcf_r, since = handle_double_grinding(
                since, gauge, H_curr, RCF_curr, rcf_r, gauge_levels, t, Ht_H if rail == 'H' else Ht_L
            )

            if rail == 'H':
                PV_maint_H += milling_cost
                PV_cap_H += capacity_cost
                H_H, R_H, R_r_H = H_curr, RCF_curr, rcf_r
                since_grind_H = since
            else:
                PV_maint_L += milling_cost
                PV_cap_L += capacity_cost
                H_L, R_L, R_r_L = H_curr, RCF_curr, rcf_r
                since_grind_L = since

        # Rail renewal (costs separated)
        for H_curr, RCF_curr, name in ((H_H, R_H, 'H'), (H_L, R_L, 'L')):
            if H_curr > H_MAX:
                # Option 1: Renew both rails at the same time
                material_cost = RAIL_RENEWAL_COST / (1 + DISCOUNT_RATE) ** t
                cap_renewal_cost = (CAP_POSS_PER_HOUR * POSS_NEW_RAIL) / (1 + DISCOUNT_RATE) ** t
                lcc_H = PV_renew_H + PV_maint_H + PV_cap_H + material_cost
                lcc_L = PV_renew_L + PV_maint_L + PV_cap_L + material_cost 
                lcc_shared =  PV_tamping + PV_cap_tamping + cap_renewal_cost
                lifetime_H = t if name == 'H' else lifetime_H
                lifetime_L = t if name == 'L' else lifetime_L
                renewal_options.append({
                    "Option": "Renew both @" + name,
                    "Rail": name,
                    "Lifetime_H": t,
                    "Lifetime_L": t,
                    "Horizon": t,
                    "LCC_H": lcc_H,
                    "LCC_L": lcc_L,
                    "LCC_shared": lcc_shared
                })


                # if both rails have been renewed, we add save the final case in renewal options where rails are separately renewed
                if lifetime_L > 0 and lifetime_H > 0:
                    renewal_options.append({
                        "Option": "Renew separately",
                        "Rail": name,
                        "Lifetime_H": lifetime_H,
                        "Lifetime_L": lifetime_L,
                        "Horizon": t,
                        "LCC_H": lcc_H + cap_renewal_cost,
                        "LCC_L": lcc_L + cap_renewal_cost,
                        "LCC_shared": lcc_shared - cap_renewal_cost
                    })
                    break

                # Option 2: Renew only the rail that reached the limit
                if name == 'H':
                    PV_renew_H += material_cost 
                    PV_cap_H += cap_renewal_cost
                    H_H, R_H, R_r_H = 0, 0, 0
                else:
                    PV_renew_L += material_cost
                    PV_cap_L += cap_renewal_cost
                    H_L, R_L, R_r_L = 0, 0, 0

        if track_results:
            history.append({
                'Month': m, 'H_H': H_H, 'RCF_H': R_H,
                'H_L': H_L, 'RCF_L': R_L, 'Gauge': gauge
            })

        # if both rails are renewed, we can stop the simulation
        if lifetime_H > 0 and lifetime_L > 0:
            break

        # end of simulation with the end of the technical lifetime of the track
        if m == MAX_MONTHS:
            material_cost = RAIL_RENEWAL_COST / (1 + DISCOUNT_RATE) ** t
            cap_renewal_cost = (CAP_POSS_PER_HOUR * POSS_NEW_RAIL) / (1 + DISCOUNT_RATE) ** t
            renewal_options.append({
                "Option": "Renew - EoL track",
                "Rail": "Both",
                "Lifetime_H": t,
                "Lifetime_L": t,
                "Horizon": t,
                "LCC_H": PV_maint_H + PV_cap_H + material_cost,
                "LCC_L": PV_maint_L + PV_cap_L + material_cost,
                "LCC_shared": PV_tamping + PV_cap_tamping + cap_renewal_cost
            })
            break



    # --- END OF SIMULATION ---

    # to renewal options, add one column for annuity
    for option in renewal_options:
        annuity_H = option["LCC_H"]/option["Horizon"]
        annuity_L = option["LCC_L"]/option["Horizon"]
        annuity_shared = option["LCC_shared"]/option["Horizon"]
        option["Annuity"] = (annuity_H + annuity_L + annuity_shared)/TRACK_LENGTH_M


    optimal_option = min(renewal_options, key=lambda x: x["Annuity"])
    if verbose:
        print(f"Optimal option: {optimal_option['Option']} with annuity {optimal_option['Annuity']:.2f} €/m/year")

    if plot_timeline:
        plot_renewal_options(renewal_options)



    annuity = optimal_option["Annuity"]
    lifetime = optimal_option["Horizon"]


    if track_results:
        return annuity, lifetime, history
    else:
        return annuity, lifetime


# === PLOTTING FUNCTIONS ===

def plot_renewal_options(renewal_options):
    """
    Plot the renewal options: x-axis is the lifetime (years), y-axis is the annuity (€/m/year).
    """
    lifetimes = [12*option["Horizon"] for option in renewal_options]
    annuities = [option["Annuity"] for option in renewal_options]
    labels = [option["Option"] for option in renewal_options]

    plt.figure(figsize=(10, 6))
    plt.scatter(lifetimes, annuities, color='green', label='Renewal Option')

    for i, label in enumerate(labels):
        plt.annotate(label, (lifetimes[i], annuities[i]), textcoords="offset points", xytext=(5, 5), ha='left', fontsize=9)

    plt.xlabel('Lifetime (months)')
    plt.ylabel('Annuity (€/m/year)')
    plt.title('Renewal Options: Lifetime vs Annuity')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_historical_data_two_rails(history):
    """
    Plots the historical data for H_H, RCF_H, H_L, RCF_L, and Gauge over time
    using the history returned by get_annuity_track_refactored.

    Parameters:
    - history: List of dicts with keys 'Month', 'H_H', 'RCF_H', 'H_L', 'RCF_L', 'Gauge'
    """
    df = pd.DataFrame(history)
    fig_size = (10, 4)

    # Plot H-index for both rails
    plt.figure(figsize=fig_size)
    sns.lineplot(data=df, x='Month', y='H_H', marker='o', label='High Rail H')
    sns.lineplot(data=df, x='Month', y='H_L', marker='o', label='Low Rail H')
    plt.title('Historical H-index (H) for Both Rails')
    plt.xlabel('Month')
    plt.ylabel('H-index')
    plt.legend()
    plt.grid()
    plt.show()

    # Plot RCF for both rails
    plt.figure(figsize=fig_size)
    sns.lineplot(data=df, x='Month', y='RCF_H', marker='o', label='High Rail RCF')
    sns.lineplot(data=df, x='Month', y='RCF_L', marker='o', label='Low Rail RCF')
    plt.title('Historical RCF for Both Rails')
    plt.xlabel('Month')
    plt.ylabel('RCF')
    plt.legend()
    plt.grid()
    plt.show()

    # Plot Gauge
    plt.figure(figsize=fig_size)
    sns.lineplot(data=df, x='Month', y='Gauge', marker='o')
    plt.title('Historical Gauge')
    plt.xlabel('Month')
    plt.ylabel('Gauge')
    plt.grid()
    plt.show()