function [lcc_total, track_lifetime] = get_lcc(H_table, NW_table, maint_strategy, ...
    gauge_widening, RCF_residual_table, RCF_depth_table, max_lifetime, renewal_costs_rate, maintenance_costs_rate)
%GET_LCC calculates the total lifecycle costs
%   Given a maintenance strategy (frequency of tamping/grinding), the
%   function estimates the total LCC in net present value

discount_rate = 0.04; % 4%

% Track parameters
track_length_meter = 1000; 
track_lifetime_years = 15;

% Cost parameters (sek/m)
tamping_cost_per_meter = maintenance_costs_rate*40;
grinding_cost_per_meter = maintenance_costs_rate*50;%50
renewal_costs = renewal_costs_rate*1500*track_length_meter; % track renewal is 6 500 kr/m mulplied by sensitivity rate

% maintenance frequency
grinding_freq = maint_strategy(1);
tamping_freq = maint_strategy(2);

% train operation parameters (SEk per hour)
cost_hourly_poss = 50293;

% track possession per activity (in hours)
poss_grinding = 2;
poss_tamping = 5; %%% more hours than grinding, 5-10 hours
%poss_grinding_MB6 = 3;

% gauge intervals (in mm)
gauge = [1440,1445,1450,1455];
% if(strcmp(inner_rail,"MB6"))
%     gauge = gauge(3:4);
% end

Xq = gauge;
Xq_gauge_widening = [1440,1442,1445,1446,1447,1448,1449,1450];


% get max months before grinding
max_months_grinding = size(H_table, 2);

% months (for interpolation)
months = 1:max_months_grinding;
Yq= months;

% maximum H (criterion for rail renewal)
H_max = 14;

% find the corresponding total LCC 
H_curr = 0;
gauge_curr = gauge(1);
maintenance = 0;
train_op = 0;
latest_grinding_since = 1; % in months
latest_tamping_since = 1; % in months
track_lifetime = 15;
max_m = 12*track_lifetime_years;
rail_lifetime_remainder = max_m;

RCF_residual_curr = 0;

%%% renewal cost
% Renewal cost (Material + Work) in SEK per meter
% if(strcmp(inner_rail,"MB6"))
%     renewal_costs =2214;  %500+924.7;% 
% end
% renewal_costs = 1500;%500+924.4;%; 
% total renewl cost
renewal = renewal_costs_rate*6500*track_length_meter;% + renewal_costs*track_length_meter;

RCF_res_grinding = 0;


gauge_curr_historic = zeros(1, max_m);
H_curr_historic = zeros(1, max_m);
RCF_historic = zeros(1, max_m);


%%% simulation of LCC
for m=1:max_m % till track lifetime
    
    %%% convert month to year
    y = m/12; % ceil(m/12);
    
    %%% gauge increase after 1 month
    avg_yearly_gauge_widening = pchip(Xq_gauge_widening, gauge_widening(:), gauge_curr); 
    gauge_curr = gauge_curr+avg_yearly_gauge_widening/12;
    
    rail_lifetime_remainder = rail_lifetime_remainder-1;
    % calculate the marginal increase delta_H
    delta_H = pchip(Xq, NW_table(:, latest_grinding_since), gauge_curr);
        
    % Grinding and its costs
    if(latest_grinding_since==grinding_freq) % time to do grinding
        maintenance = maintenance + grinding_cost_per_meter*track_length_meter/(1+discount_rate)^y; 
        latest_grinding_since = 0;
        train_op = train_op + poss_grinding*cost_hourly_poss/(1+discount_rate)^y;
        % update the H-index using + H_index - natural wear
        H_curr = H_curr + pchip(Xq, H_table(:, grinding_freq), gauge_curr) - delta_H;

        % Update the RCF residual
        rcf_grinding = pchip(Xq, RCF_residual_table(:, grinding_freq), gauge_curr);
        if(rcf_grinding>0)
            RCF_res_grinding = RCF_res_grinding + rcf_grinding;
        end
        RCF_residual_curr = RCF_res_grinding;
    else
        %%% update the RCF residual
        RCF_residual_curr = RCF_res_grinding + pchip(Xq, RCF_depth_table(:, latest_grinding_since), gauge_curr); 
        
        %%% update the current H-index
        H_curr = H_curr + delta_H;
    end
    
    % Tamping and its costs
    if(latest_tamping_since==tamping_freq || rail_lifetime_remainder == 0) % time to do tamping or rail renewal
        maintenance = maintenance + tamping_cost_per_meter*track_length_meter/(1+discount_rate)^y;
        train_op = train_op + poss_tamping*cost_hourly_poss/(1+discount_rate)^y;
        gauge_curr = gauge(1);
        latest_tamping_since = 0;
        %%% rail renewal if rail_lifetime is over (because of derailement risk)
        if(rail_lifetime_remainder == 0)
            renewal = renewal + renewal_costs/(1+discount_rate)^y; % return lifetime in years
            maintenance = maintenance - tamping_cost_per_meter*track_length_meter/(1+discount_rate)^y;
            rail_lifetime_remainder = max_m;
        end
    end
    
    %%% Do melling, i.e., two grindings if RCF_max is reached
    RCF_max = .5;
    if(RCF_residual_curr>RCF_max)
        RCF_residual_curr = 0; % reset the accumulated total RCF residual
        RCF_res_grinding = 0; % reset the accumulated RCF residual after grinding
        % add grinding costs * 2
        poss_grinding_twice = poss_grinding*5/3;
        grinding_cost_per_meter_twice = grinding_cost_per_meter*5/3;
        maintenance = maintenance + grinding_cost_per_meter_twice*track_length_meter/(1+discount_rate)^y;
        train_op = train_op + poss_grinding_twice*cost_hourly_poss/(1+discount_rate)^y;
        % update the H-index
        delta_H_1 = pchip(Xq, H_table(:, latest_grinding_since+1), gauge_curr);
        delta_H_2 = pchip(Xq, H_table(:, 1), gauge_curr);
        H_curr = H_curr + delta_H_1 + delta_H_2;
        % update when grinding was performed
        latest_grinding_since = 0;
    end

    %%% too high gauge, i.e., risk for derailment 
    if(gauge_curr>=1450)
        if(rail_lifetime_remainder > max_lifetime)
            rail_lifetime_remainder = max_lifetime;
        end
    end
            
    % older grindng and tamping
    latest_grinding_since = latest_grinding_since + 1; % in months
    latest_tamping_since = latest_tamping_since + 1; % in months
    
    H_curr_historic(m) = H_curr;
    RCF_historic(m) = RCF_residual_curr;
    gauge_curr_historic(m) = gauge_curr;
    
    % stop if we need to renew the rail or if we are beyond the maximal gauge limit
    % include remaining_lifetime using max_lifetime (from risk tables)
    if(H_curr>H_max)
        track_lifetime = y; % return lifetime in years
        break;
    end
    
end

% total LCC in NPV/meter
lcc_total = train_op +maintenance+renewal;%+end_of_life;
lcc_total = lcc_total/track_length_meter/track_lifetime;

% %% print historical values of H_index and Gauge
plot_figure('historic', {H_curr_historic, track_lifetime, RCF_historic, gauge_curr_historic});

end