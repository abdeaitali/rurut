function [opt_grinding, opt_tamping, min_ANN, opt_lifetime] = get_optimal(H_interpolated, ...
    NW_interpolated, gauge_widening, RCF_residual, RCF_depth,...
    max_lifetime, tamping_freq_max, renewal_costs_rate, tamping_costs_rate)
%get_optimal Finds the optimal maintenance strategy and lifetime
%   Given certain inputs (interpolated H-table, gauge widening), the
%   function finds the optimal rail lifetime and the maintenance strategy
%   (grinding & tamping) as well as the corresponding LCCs


%%% initializations
months_tamping = 1:tamping_freq_max; % max number of months before tamping
grinding_freq_max = 12;
months_grinding = 1:grinding_freq_max;
simulation_LCC = zeros(months_grinding(end),months_tamping(end));
rail_lifetime = zeros(months_grinding(end),months_tamping(end));

%%% find the optimal (LCC-minimal) strategies for tamping and grinding
for grinding_freq=months_grinding % different grinding frequencies
    for tamping_freq=months_tamping % different tamping frequencies
        %%% set strategy
        maint_strategy = [grinding_freq,tamping_freq];
        maint_strategy = [12,48];
        %%% calculate LCC (annuity)
        [simulation_LCC(grinding_freq,tamping_freq),rail_lifetime(grinding_freq,tamping_freq)] = ...
            get_lcc(H_interpolated, NW_interpolated, maint_strategy, ...
            gauge_widening, RCF_residual, RCF_depth, max_lifetime, renewal_costs_rate, tamping_costs_rate);
    end
end

%%% plot the variation of LCC/annuity for different maintenance strategies
%plot_figure('LCC_heatmap', {simulation_LCC, 'contours'});

%%% get optimal/minimal annuity
min_ANN = min(simulation_LCC(:));

%%% get the corresponding optimal strategy (or strategies)
[opt_grinding_val, opt_tamping_val] = find(simulation_LCC==min_ANN);

[opt_tamping, opt_tamping_id] = max(opt_tamping_val);
opt_grinding = opt_grinding_val(opt_tamping_id);

%%% get the corresponding optimal rail lifetime
opt_lifetime = rail_lifetime(opt_grinding, opt_tamping);


end

