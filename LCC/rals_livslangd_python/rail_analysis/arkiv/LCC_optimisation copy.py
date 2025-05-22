from rail_analysis.LCC_two_rails import get_annuity_track_refactored, plot_historical_data_two_rails
from rail_analysis.LCC_single_rail import get_annuity_refactored, plot_historical_data_both_rails
from rail_analysis.constants import (
    TECH_LIFE_YEARS, 
    TRACK_RENEWAL_COST,
    TRACK_LENGTH_M     
)

import pandas as pd
import numpy as np

def optimise_and_compare(
    data_df,
    grinding_freq_low,
    grinding_freq_high,
    gauge_freq=48,
    maint_strategy_single=None,
    profile_low_rail='MB4',
    profile_high_rail='MB4',
    track_results=False,
    gauge_widening_per_year=1,
    radius='1465',
    track_life=TECH_LIFE_YEARS,
    bar_chart=False
):
    # --- Joint (two-rail) optimisation ---
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

    # --- Separate (single-rail) optimisation ---
    if maint_strategy_single is None:
        maint_strategy_single = (grinding_freq_low, gauge_freq)
    ann_H, life_H, hist_H = get_annuity_refactored(
        data_df,
        maint_strategy_single,
        high_or_low_rail='High',
        track_results=track_results,
        gauge_widening_per_year=gauge_widening_per_year,
        radius=radius
    )
    ann_L, life_L, hist_L = get_annuity_refactored(
        data_df,
        maint_strategy_single,
        high_or_low_rail='Inner',
        track_results=track_results,
        gauge_widening_per_year=gauge_widening_per_year,
        radius=radius
    )

    # --- Plot the history of the rail using the functions plot_historical_data_two_rails ---
    if track_results:
        plot_historical_data_two_rails(hist_joint)
        plot_historical_data_both_rails(hist_L, hist_H)


    # --- Use the technical lifetime for fair comparison ---
    comparison_lifetime = TECH_LIFE_YEARS

    total_LCC_joint = ann_joint * comparison_lifetime + TRACK_RENEWAL_COST/TRACK_LENGTH_M    # per meter
    total_LCC_H = ann_H * comparison_lifetime        # per meter
    total_LCC_L = ann_L * comparison_lifetime       # per meter
    total_LCC_sum = total_LCC_H + total_LCC_L + TRACK_RENEWAL_COST/TRACK_LENGTH_M          # per meter

    # --- Comparison summary ---
    summary = pd.DataFrame({
        'Approach': [
            'Joint (two-rail)',
            'Separate (High)',
            'Separate (Low)',
            'Separate (Sum H+L)'
        ],
        'Annuity [SEK/m/year]': [ann_joint, ann_H, ann_L, None],
        'Lifetime [years]': [life_joint, life_H, life_L, None],
        f'Total LCC over {comparison_lifetime:.1f} years [SEK/m]': [
            total_LCC_joint, total_LCC_H, total_LCC_L, total_LCC_sum
        ]
    })
    print(summary)
    # print also the percentage of savings in total LCC when joingt (two-rail) approach instead of separate (high+low)
    savings_percentage = (total_LCC_sum - total_LCC_joint) / total_LCC_sum * 100
    print(f"Savings in total LCC when using joint (two-rail) approach instead of separate (high+low): {savings_percentage:.2f}%")

    # If bar_chart is True: plot the results as bar charts
    if bar_chart:
        plot_comparison_figures(
            ann_joint, ann_H, ann_L,
            life_joint, life_H, life_L,
            total_LCC_joint, total_LCC_H, total_LCC_L,
            comparison_lifetime
        )


    
    return {
        'joint': {'annuity': ann_joint, 'lifetime': life_joint, 'history': hist_joint, 'total_LCC': total_LCC_joint},
        'high': {'annuity': ann_H, 'lifetime': life_H, 'history': hist_H, 'total_LCC': total_LCC_H},
        'low': {'annuity': ann_L, 'lifetime': life_L, 'history': hist_L, 'total_LCC': total_LCC_L},
        'sum': {'total_LCC': total_LCC_sum},
        'summary': summary
    }

def plot_comparison_figures(
        ann_joint, ann_H, ann_L,
        life_joint, life_H, life_L,
        total_LCC_joint, total_LCC_H, total_LCC_L,
        comparison_lifetime
        ):
        import matplotlib.pyplot as plt
        # Convert costs to thousand SEK
        annuities = [ann_joint / 1000, ann_H / 1000, ann_L / 1000]
        total_LCC_joint_thousand = total_LCC_joint / 1000
        total_LCC_H_thousand = total_LCC_H / 1000
        total_LCC_L_thousand = total_LCC_L / 1000

        approaches = ['Joint (two-rail)', 'Separate (High)', 'Separate (Low)']
        lifetimes = [life_joint, life_H, life_L]

        bar_width = 0.35  # Slightly wider bars to reduce distance

        # --- Create figure with 3 subplots ---
        fig, axs = plt.subplots(1, 3, figsize=(10, 5))

        # 1. Annuity bar chart
        axs[0].bar(approaches, annuities, color=['black', 'dimgray', 'lightgray'], width=bar_width)
        axs[0].set_ylabel('Annuity [kSEK/m/year]')
        axs[0].set_title('Annuity Comparison')
        axs[0].set_xticks(np.arange(len(approaches)))
        axs[0].set_xticklabels(approaches, rotation=15)

        # 2. Lifetime bar chart
        axs[1].bar(approaches, lifetimes, color=['black', 'dimgray', 'lightgray'], width=bar_width)
        axs[1].set_ylabel('Lifetime [years]')
        axs[1].set_title('Lifetime Comparison')
        axs[1].set_xticks(np.arange(len(approaches)))
        axs[1].set_xticklabels(approaches, rotation=15)

        # 3. Total LCC bar chart (joint vs separate stacked)
        approaches_lcc = ['Joint (two-rail)', 'Separate (High+Low)']
        axs[2].bar(approaches_lcc[0], total_LCC_joint_thousand, color='black', label='Joint (two-rail)', width=bar_width)
        axs[2].bar(approaches_lcc[1], total_LCC_H_thousand, color='dimgray', label='Separate (High)', width=bar_width)
        axs[2].bar(approaches_lcc[1], total_LCC_L_thousand, bottom=total_LCC_H_thousand, color='lightgray', label='Separate (Low)', width=bar_width)
        axs[2].set_ylabel(f'Total LCC over {comparison_lifetime:.1f} years [kSEK/m]')
        axs[2].set_title('Total LCC Comparison')
        axs[2].set_xticks(np.arange(len(approaches_lcc)))
        axs[2].set_xticklabels(approaches_lcc, rotation=15)

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.22)  # Make space for legend
        plt.show()
