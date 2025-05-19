from rail_analysis.LCC_two_rails import get_annuity_track_refactored, plot_historical_data_two_rails
from rail_analysis.LCC_single_rail import get_annuity_refactored, plot_historical_data_both_rails
from rail_analysis.constants import TECH_LIFE_YEARS
import pandas as pd

def optimise_and_compare(
    data_df,
    grinding_freq_low,
    grinding_freq_high,
    gauge_freq,
    maint_strategy_single=None,
    profile_low_rail='MB4',
    profile_high_rail='MB4',
    track_results=False,
    gauge_widening_per_year=1,
    radius='1465',
    track_life=TECH_LIFE_YEARS
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

    total_LCC_joint = ann_joint * comparison_lifetime  # per meter
    total_LCC_H = ann_H * comparison_lifetime         # per meter
    total_LCC_L = ann_L * comparison_lifetime         # per meter
    total_LCC_sum = total_LCC_H + total_LCC_L         # per meter

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
    return {
        'joint': {'annuity': ann_joint, 'lifetime': life_joint, 'history': hist_joint, 'total_LCC': total_LCC_joint},
        'high': {'annuity': ann_H, 'lifetime': life_H, 'history': hist_H, 'total_LCC': total_LCC_H},
        'low': {'annuity': ann_L, 'lifetime': life_L, 'history': hist_L, 'total_LCC': total_LCC_L},
        'sum': {'total_LCC': total_LCC_sum},
        'summary': summary
    }