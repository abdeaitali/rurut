function y = get_lifetime(H_table, yearly_tamping)
%GET_LIFETIME Summary of this function goes here
%   Detailed explanation goes here


% gauge intervals (in mm)
gauge = [1440,1445,1450,1455];
Xq = gauge;

% months
months = 1:12;
Yq= months;

% average yearly gauge widening (in mm/year)
avg_yearly_gauge_widening = .2;

% maximum H (criterion for rail renewal)
H_max = 14;

% find the corresponding lifetime in years
y = 0;
H_curr = 0;
gauge_curr = 1440;
for m=yearly_tamping:yearly_tamping:156 % over 13 years maximum or 156 months
    % gauge increase after yearly_tamping months
    gauge_curr = gauge_curr+ avg_yearly_gauge_widening*yearly_tamping/12;
    % corresponding increase in H measure
    H_curr = H_curr + interp2(Xq, Yq, H_table(:,Yq)', gauge_curr, yearly_tamping,'linear');
    % stop if we need to renew the rail or if we are beyond the maximal gauge limit
    if(H_curr>=H_max || gauge_curr>1455)
        break;
    end
    y = m; % in months
end
y = floor(y/12);% in years
end

