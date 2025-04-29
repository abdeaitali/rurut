function [table_interpol] = interpolation(table, grinding_freq_max, arg_num)
%INTERPOLATION Interpolation of the H-index look-up table
%   Given a specific interpolation method, this function replaces the values
%   of the first months with an interpolation.
%   Parameter arg_num:
%       1  - Natural wear interpolation
%       0  - Gauge widening interpolation
%       -1 - H-index interpolation
%       -2 - RCF residual interpolation

% Define month indices (months 7-12, and month 0 treated as 1)
% month_indices = [0, 7, 10, 12];
month_indices = [0, 7, 8, 9, 10, 11, 12];
% if strcmp(tonnage, 'H_32t')
%     month_indices = [0, 8, 10];
% end 
% Define standard track gauges (in mm)
standard_gauges = [1440, 1445, 1450, 1455];

if arg_num == 0
    % Call the specific helper function for gauge widening interpolation
    table_interpol = gauge_widening_interpolation(table, standard_gauges);
else
    % Perform the common interpolation for other cases
    % Extend the table by prepending a zero column for month 0
    extended_table = [zeros(size(standard_gauges, 2), 1), table];
    table_interpol = common_interpolation(standard_gauges, month_indices, extended_table, grinding_freq_max);
end

end

function table_interpol = gauge_widening_interpolation(table, standard_gauges)
%GAUGE_WIDENING_INTERPOLATION Handles interpolation specific to gauge widening (arg_num = 0)
%   Performs interpolation when the table represents gauge widening data.

% Use the table's first column as standard_gauges
gauges = table(:,1)';

% The table data excludes the first column which contains gauges
table = table(:,2:end);

% For gauge widening, use first three months as month indices (1, 2, 3 mm/year)
initial_widening_rates = 1:3;

% Initialize the output table
table_interpol = zeros(length(standard_gauges), length(initial_widening_rates));

% Perform interpolation and fill the output table
for g_id = 1:length(standard_gauges)
    for init_rate = 1:length(initial_widening_rates) % for each of the three initial widening
        table_interpol(g_id, init_rate) = pchip(gauges, table(:,init_rate), standard_gauges(g_id));
        %interpolated_table = max(interpolated_value, 0); % Ensure non-negative values
    end
end

end

function interpolated_table = common_interpolation(gauges, months, values, max_freq)
%COMMON_INTERPOLATION Performs the interpolation for given gauges and months
%   This function is reused by both the gauge widening-specific interpolation and other cases.

% Initialize the output table
interpolated_table = zeros(length(gauges), max_freq);

% Perform interpolation and fill the output table
for g_id = 1:length(gauges)
    for m = 1:max_freq
        interpolated_table(g_id, m) = pchip(months, values(g_id, months+1), m);
        %interpolated_table(g_id, m) = max(interpolated_value, 0); % Ensure non-negative values
    end
end

end



% function [table_interpol] = interpolation(table, type, grinding_freq_max, arg_num)
% %INTERPOLATION Interpolation of the H-index look-up table
% %   Given a specific interpolation method, this function replaces the values
% %   of the first months with an interpolation
% %   parameter arg_num is 1 if it is natural wear interpolation
% %                        0 if it is gauge widening interpolation
% %                        -1 if it is H-index
% %                        -2 if it is RCF residual
% 
% 
% %%% the indices of the months
% 
% Yq = [0,7,8,9,10,11,12]; % months. month zero is 1 in the list
% %Yq = [0,7,8,9];
% 
% % if(arg_num==1)
% %     Yq = linspace(0,9,10);% for natural wear, consider all months in the interpolation
% % end
% 
% %Yq = linspace(1,12,12)-1;
% 
% %%% the indices of the track gauges (in mm)
% gauge = [1440,1445,1450,1455];
% if(arg_num==0)
%   gauge = table(:,1)';
%   table = table(:,2:end);
%   Yq = [1,2,3]; % initial gauge widening 1, 2 or 3mm/y
% end
% 
% %%% initializations
% table_interpol = zeros(4,grinding_freq_max);
% ext_H_table = [zeros(size(gauge,2),1) table];
% 
% if(arg_num == 0) % gauge widening
%     table_interpol = zeros(4,3);
% 
%     %%% interpolation of the gauge widening
%     % Prepare the data for interpolation
%     [X, Y] = meshgrid(Yq, gauge);
%     V = table(:, Yq);
%     
%     % Flatten the data for scatteredInterpolant
%     X = X(:);
%     Y = Y(:);
%     V = V(:);
%     
%     % Create the interpolant
%     F = scatteredInterpolant(X, Y, V, type, 'linear');
% 
%     % Interpolation and extrapolation 
%     std_gauge = [1440,1445,1450,1455];
%     for g_id = 1:length(std_gauge) % for each gauge 
%         for init_wg = 1:length(Yq) % for each of the three initial widening
%             table_interpol(g_id, init_wg) = F(init_wg, std_gauge(g_id));
%         end
%     end
% else
%     %%% interpolation of the look-up tables
%     % Prepare the data for interpolation
%     [X, Y] = meshgrid(Yq, gauge);
%     V = ext_H_table(:, Yq + 1);
%     
%     % Flatten the data for scatteredInterpolant
%     X = X(:);
%     Y = Y(:);
%     V = V(:);
%     
%     % Create the interpolant
%     F = scatteredInterpolant(X, Y, V, type, 'linear');
%     
%     % Interpolation and extrapolation for each month and gauge
%     for g_id = 1:length(gauge)
%         for m = 1:grinding_freq_max
%             table_interpol(g_id, m) = F(m, gauge(g_id));
%             %table_interpol(g_id, m) = pchip(x,y,gauge(g_id))
%             if(table_interpol(g_id, m)<0)
%                 table_interpol(g_id, m) = 0;
%             end
%         end
%     end
% end

