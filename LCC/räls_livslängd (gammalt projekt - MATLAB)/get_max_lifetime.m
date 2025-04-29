function [max_lifetime] = get_max_lifetime(risk, strict)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

% set parameter for threeshold (in months) for 1455mm
param_threshold_month= 4; 
param_threshold_gauge = 0; % 1 is 1450 mm, and 0 is 1455 mm
% strict if 1, set 3 months @ 1450
if(strict == 1)
    param_threshold_month = 3;
    param_threshold_gauge = 1;
end

% find the max lifetime for the others
max_life = zeros(size(risk,1),1);
max_life(end) = param_threshold_month;
for g=1:size(risk,1)-1
    for m=param_threshold_month:12
        if(risk(g,m)<=risk(end-param_threshold_gauge,param_threshold_month))
            max_life(g) = m;
        else
            break;
        end
    end
end


% return the maximal lifetime
max_lifetime = max_life(end-param_threshold_gauge,1);
end

