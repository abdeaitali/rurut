from rail_analysis.LCC_two_rails import get_annuity_track_refactored, plot_historical_data_two_rails
from rail_analysis.LCC_single_rail import get_annuity_refactored, plot_historical_data_both_rails
from rail_analysis.constants import (
    TECH_LIFE_YEARS, 
    TRACK_RENEWAL_COST, 
    TRACK_LENGTH_M
)

import pandas as pd

def run_joint_optimisation(
    data_df,
    grinding_freq_low,
    grinding_freq_high,
    gauge_freq=48,
    profile_low_rail='MB4',
    profile_high_rail='MB4',
    track_results=False,
    gauge_widening_per_year=1,
    radius='1465',
    track_life=TECH_LIFE_YEARS
):
    ann_joint, life_joint, hist_joint = get_annuity_track_refactored(
        data_df,
        grinding_freq_low,
        grinding_freq_high,
        gauge_freq,
        profile_low_rail=profile_low_rail,
        profile_high_rail=profile_high_rail,
        track_results=track_results,
        gauge_widening_per_year=gauge_widening_per_year,
        radius=radius,
        track_life=track_life
    )
    return ann_joint, life_joint, hist_joint

def run_separate_optimisation(
    data_df,
    grinding_freq,
    gauge_freq=48,
    profile_rail='MB4',
    track_results=False,
    gauge_widening_per_year=1,
    radius='1465'
):
    maint_strategy = (grinding_freq, gauge_freq)
    ann_H, life_H, hist_H = get_annuity_refactored(
        data_df,
        maint_strategy,
        high_or_low_rail='High',
        track_results=track_results,
        gauge_widening_per_year=gauge_widening_per_year,
        radius=radius
    )
    ann_L, life_L, hist_L = get_annuity_refactored(
        data_df,
        maint_strategy,
        high_or_low_rail='Inner',
        track_results=track_results,
        gauge_widening_per_year=gauge_widening_per_year,
        radius=radius
    )
    return ann_H, life_H, hist_H, ann_L, life_L, hist_L

def compare_joint_vs_separate(
    data_df,
    grinding_freqs,
    gauge_freq=48,
    profile_low_rail='MB4',
    profile_high_rail='MB4',
    track_results=False,
    gauge_widening_per_year=1,
    radius='1465',
    track_life=TECH_LIFE_YEARS,
    bar_chart=False
):
    results = []
    for freq in grinding_freqs:
        # Joint
        ann_joint, life_joint, _ = run_joint_optimisation(
            data_df, freq, freq, gauge_freq,
            profile_low_rail, profile_high_rail,
            track_results, gauge_widening_per_year, radius, track_life
        )
        # Separate
        ann_H, life_H, _, ann_L, life_L, _ = run_separate_optimisation(
            data_df, freq, gauge_freq, profile_low_rail, track_results, gauge_widening_per_year, radius
        )
        # LCC over technical lifetime
        total_LCC_joint = ann_joint * TECH_LIFE_YEARS + TRACK_RENEWAL_COST / TRACK_LENGTH_M
        total_LCC_H = ann_H * TECH_LIFE_YEARS
        total_LCC_L = ann_L * TECH_LIFE_YEARS
        total_LCC_sum = total_LCC_H + total_LCC_L + TRACK_RENEWAL_COST / TRACK_LENGTH_M
        results.append({
            'GrindingFreq': freq,
            'Annuity_Joint': ann_joint,
            'Lifetime_Joint': life_joint,
            'TotalLCC_Joint': total_LCC_joint,
            'Annuity_High': ann_H,
            'Lifetime_High': life_H,
            'TotalLCC_High': total_LCC_H,
            'Annuity_Low': ann_L,
            'Lifetime_Low': life_L,
            'TotalLCC_Low': total_LCC_L,
            'TotalLCC_Sum': total_LCC_sum
        })
    df = pd.DataFrame(results)
    print(df)
    if bar_chart:
        plot_comparison_grid(df)
    return df

def plot_comparison_grid(df):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    x = df['GrindingFreq']

    axs[0].plot(x, df['Annuity_Joint'], label='Joint', marker='o')
    axs[0].plot(x, df['Annuity_High'], label='Separate High', marker='x')
    axs[0].plot(x, df['Annuity_Low'], label='Separate Low', marker='s')
    axs[0].set_title('Annuity [SEK/m/year]')
    axs[0].set_xlabel('Grinding Frequency (months)')
    axs[0].legend()
    axs[0].grid()

    axs[1].plot(x, df['Lifetime_Joint'], label='Joint', marker='o')
    axs[1].plot(x, df['Lifetime_High'], label='Separate High', marker='x')
    axs[1].plot(x, df['Lifetime_Low'], label='Separate Low', marker='s')
    axs[1].set_title('Lifetime [years]')
    axs[1].set_xlabel('Grinding Frequency (months)')
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(x, df['TotalLCC_Joint'], label='Joint', marker='o')
    axs[2].plot(x, df['TotalLCC_Sum'], label='Separate (Sum H+L)', marker='s')
    axs[2].set_title(f'Total LCC over {TECH_LIFE_YEARS} years [SEK/m]')
    axs[2].set_xlabel('Grinding Frequency (months)')
    axs[2].legend()
    axs[2].grid()

    plt.tight_layout()
    plt.show()
