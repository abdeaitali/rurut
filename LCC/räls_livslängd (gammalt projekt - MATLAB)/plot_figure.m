function plot_figure(wanted_fig, arg)
%PLOT_FIGURE Function for plotting figures
%   Depending on input argument, plot specific figures

% gauge intervals (in mm)
gauge = [1440,1445,1450,1455];

% months
months = linspace(1,12,12);

% Common settings for all plots
lineStyles = {'-', '--', '-.', ':'};

figure;


if strcmp(wanted_fig, 'H_table')
    % Plot H_table
    for i = 1:length(gauge)
        plot(months, arg(i,:), 'LineStyle', lineStyles{i}, 'LineWidth', 2);
        hold on;
    end
    legend(arrayfun(@num2str, gauge, 'UniformOutput', false), 'Location', 'northwest');
    xlabel('Months');
    ylabel('{\it H}-index');
    grid on;

elseif strcmp(wanted_fig, 'H_tables_heatmap')
    % Plot heatmaps for H_table_MB5 and H_table_MB6
    H_table_MB5 = arg{1};
    H_table_MB6 = arg{2};

    for i = 1:2
        subplot(1, 2, i);
        [X, Y] = meshgrid(months, gauge(1:(2 + i)));
        surf(X, Y, arg{i});
        xlabel('Months (since last grinding)');
        ylabel('Gauge (in mm)');
        zlabel('{\it H}-index (increase)');
        set(gca, 'FontSize', 12, 'TickLabelInterpreter', 'none', 'YDir', 'reverse');
        caxis([min(H_table_MB5(:)), max(H_table_MB6(:))]);
        grid on;
    end
    
elseif strcmp(wanted_fig, 'LCC_heatmap')
    % visualize the LCC results as a heatmap
    ANN = arg{1};
    [nb_months_grinding,nb_months_tamping] = size(ANN);
    months_grinding = linspace(1,nb_months_grinding,nb_months_grinding);
    months_tamping = linspace(1,nb_months_tamping,nb_months_tamping);
    
    [X,Y] = meshgrid(months_tamping,months_grinding);
    surf(X,Y,ANN)
    %colorbar
    ylabel('Grinding interval (in months)','Rotation',-30, 'FontSize', 14)
    xlabel('Gauge correction interval (in months)','Rotation',20, 'FontSize', 14)
    zlabel('Annuity per meter (in SEK/year)', 'FontSize', 14)
    %title(append('Annuity of different maintenance strategies'))  
    
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels
    
    if strcmp(arg{2}, 'contours')
        figure;

        % Visualize the LCC results as a 2D contour plot       
        [X, Y] = meshgrid(months_tamping, months_grinding);
        
        % Find the minimum value and its location
        min_ANN = min(ANN(:));
        
        % Define contour levels around the minimum value
        % Adjust the range depending on the variability you want to capture
        contour_levels = linspace(min_ANN, min_ANN + min_ANN*.4, 5); % Example: 10 levels up to 50 units above minimum
        
        % Plot the 2D contour
        contour(X, Y, ANN, contour_levels, 'ShowText', 'on')
        
        % Set axis labels and title
        ylabel('Grinding interval (in months)', 'FontSize', 14)
        xlabel('Gauge correction interval (in months)', 'FontSize', 14)
        zlabel('Annuity per meter (in SEK/year)', 'FontSize', 14)
        %title('Annuity of different maintenance strategies - Contour Plot')
        
        % Highlight the minimum point on the plot
        hold on
        [min_row, min_col] = find(ANN == min_ANN);
        plot(months_tamping(min_col), months_grinding(min_row), 'r*', 'MarkerSize', 10)
        text(months_tamping(min_col), months_grinding(min_row), sprintf('Min: %.2f', min_ANN), ...
            'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'right')
        hold off       
        grid on

        ax = gca;
        ax.TickLength = [0.02 0.02]; % Increase tick length
        ax.FontSize = 12; % Increase font size of tick labels
    end
    
elseif strcmp(wanted_fig, 'historic')
    % Plot historical data for H-index, RCF residual, and gauge current history
    H_curr_historic = arg{1};
    rail_lifetime_months = 12 * arg{2}-1;
    RCF_historic = arg{3};
    gauge_curr_historic = arg{4};

    subplot(2, 1, 1);
    yyaxis left;
    plot(H_curr_historic, '-b', 'LineWidth', 2);
    ylabel('{\it H}-index (mm)', 'FontSize', 14);
    ylim([0, max(H_curr_historic) * 1.9]);
    yyaxis right;
    plot(RCF_historic, '-r', 'LineWidth', 2);
    ylabel('RCF residual (mm)', 'FontSize', 14);
    % Add some padding to the y-limits
    ylim([0, max(RCF_historic) * 1.9]);
    legend({'{\it H}-index (left values)', 'RCF residual (right values)'}, 'Location', 'northwest', 'FontSize', 12);
    xlabel('Rail age (months)', 'FontSize', 14);
    xlim([1, rail_lifetime_months]);
    grid on;
    %title('H-index and accumulated RCF Residual over the rail lifetime');
    % Increase tick size for top subplot
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels

    subplot(2, 1, 2);
    plot(gauge_curr_historic, '-k', 'LineWidth', 2);
    ylim([1440, 1455]);
    xlim([1, rail_lifetime_months]);
    ylabel('Track gauge (mm)', 'FontSize', 14);
    xlabel('Rail age (months)', 'FontSize', 14);
    grid on;
    legend({'Track gauge'}, 'Location', 'northwest', 'FontSize', 12);
    %title('Track gauge over the rail lifetime');
    % Increase tick size for bottom subplot
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels

% elseif strcmp(wanted_fig, 'interpolation')
%     % Plot interpolated H-tables
%     for i = 1:length(gauge)
%         plot(months, arg(i,:), 'LineStyle', lineStyles{i}, 'LineWidth', 2);
%         hold on;
%     end
%     legend(arrayfun(@num2str, gauge, 'UniformOutput', false), 'Location', 'northwest');
%     xlabel('Months');
%     ylabel('{\it H}-index');
%     set(gca, 'FontSize', 12);
%     grid on;

elseif strcmp(wanted_fig, 'interpolation')
    % Plot interpolated H-tables as heatmap
    H_table = arg{1};
    if size(H_table, 1) == 2
        gauge = gauge(3:4);
    end
    nb_months = size(H_table, 2);
    months = linspace(1, nb_months, nb_months);
    [X, Y] = meshgrid(months, gauge);
    surf(X, Y, H_table);
    xlabel('Months (since last grinding)', 'Rotation', 17,'FontSize', 14);
    ylabel('Track gauge (mm)', 'Rotation', -30, 'FontSize', 14);
    zlabel(strcat(arg{2}, ' (mm)'), 'FontSize', 14);
    %title(sprintf('Interpolated %s look-up table for %s', arg{2}, arg{3}));
    grid on;

%     % Visualize average monthly deterioration in H-index
%     figure;
%     x = repmat(1:nb_months, length(gauge), 1);
%     y = arg ./ x;
%     surf(y);
%     xlabel('Months (since last grinding)');
%     ylabel('Gauge (in mm)');
%     zlabel('Monthly increase in {\it H}-index');
%     grid on;

elseif strcmp(wanted_fig, 'sensitivity analysis - gauge widening')
    % Sensitivity analysis - gauge widening
    plotSensitivityAnalysisGaugeWidening(arg);

elseif strcmp(wanted_fig, 'sensitivity analysis - renewal costs')
    % Sensitivity analysis - renewal costs
    plotSensitivityAnalysisRenewalCosts(arg);

elseif strcmp(wanted_fig, 'sensitivity analysis - maintenance costs')
    % Sensitivity analysis - maintenance costs
    plotSensitivityAnalysisMaintenanceCosts(arg);

elseif strcmp(wanted_fig, 'sensitivity analysis - renewal costs & gauge widening')
    % Sensitivity analysis - renewal costs & gauge widening
    plotSensitivityAnalysisRenewalCostsGaugeWidening(arg);
end
end

% Sub-functions for specific sensitivity analysis plots
function plotSensitivityAnalysisGaugeWidening(arg)
    % Extract input arguments
    opt_grinding = arg{1};
    opt_tamping = arg{2};
    ANNs = arg{3};
    lifetimes = arg{4};
    gauge_widening_values = [1, 2, 3]; % in mm/y

    % Plot optimal lifetimes and ANNs
    yyaxis left;
    bar(gauge_widening_values, lifetimes, 0.2, 'FaceColor', 'b');
    ylabel('Optimal lifetime');
    yyaxis right;
    bar(gauge_widening_values + 0.3, ANNs, 0.2, 'FaceColor', 'r');
    ylabel('Annuity per meter (SEK per year)', 'FontSize', 14);
    xlabel('Initial gauge widening (mm/y)', 'FontSize', 14);
    xticks(gauge_widening_values);
    grid on;
    legend({'Lifetime', 'Annuity'}, 'Location', 'best', 'FontSize', 12);
    
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels
    
    % Plot optimal grinding and tamping intervals
    figure;
    yyaxis left;
    bar(gauge_widening_values, opt_grinding, 0.2, 'FaceColor', 'b');
    ylabel('Optimal grinding interval (months)', 'FontSize', 14);
    yyaxis right;
    bar(gauge_widening_values + 0.3, opt_tamping, 0.2, 'FaceColor', 'r');
    ylabel('Optimal gauge correction interval (months)', 'FontSize', 14);
    xlabel('Initial gauge widening (mm/y)', 'FontSize', 14);
    xticks(gauge_widening_values);
    grid on;
    legend({'Rail grinding', 'Gauge correction'}, 'Location', 'best', 'FontSize', 12);
    
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels
end

function plotSensitivityAnalysisRenewalCosts(arg)
    % Extract input arguments
    opt_grinding = arg{1};
    opt_tamping = arg{2};
    ANNs = arg{3};
    lifetimes = arg{4};
    rc_rate = 100 * arg{5};

    % Plot optimal lifetimes and ANNs
    figure;
    yyaxis left;
    plot(rc_rate, lifetimes, '-o', 'Color', 'b', 'LineWidth', 2);
    ylabel('Optimal rail lifetime (years)');
    yyaxis right;
    plot(rc_rate, ANNs, '-x', 'Color', 'r', 'LineWidth', 2);
    ylabel('Annuity (SEK per year and meter)', 'FontSize', 14);
    xlabel('Renewal cost factor (percent)', 'FontSize', 14);
    grid on;
    legend({'Lifetime', 'Annuity'}, 'Location', 'best', 'FontSize', 12);
    
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels

    % Plot optimal grinding and tamping intervals
    figure;
    yyaxis left;
    plot(rc_rate, opt_grinding, '-o', 'Color', 'b', 'LineWidth', 2);
    ylabel('Optimal grinding interval (months)', 'FontSize', 14);
    yyaxis right;
    plot(rc_rate, opt_tamping, '-x', 'Color', 'r', 'LineWidth', 2);
    ylabel('Optimal gauge correction interval (months)', 'FontSize', 14);
    xlabel('Renewal cost factor (percent)', 'FontSize', 14);
    grid on;
    legend({'Rail grinding', 'Gauge correction'}, 'Location', 'best', 'FontSize', 12);
    
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels
end

function plotSensitivityAnalysisMaintenanceCosts(arg)
    % Extract input arguments
    opt_grinding = arg{1};
    opt_tamping = arg{2};
    ANNs = arg{3};
    lifetimes = arg{4};
    tc = 100 * arg{5};

    % Plot optimal lifetimes and ANNs
    yyaxis left;
    plot(tc, lifetimes, '-o', 'Color', 'b', 'LineWidth', 2);
    ylabel('Optimal lifetime (years)');
    yyaxis right;
    plot(tc, ANNs, '-x', 'Color', 'r', 'LineWidth', 2);
    ylabel('Annuity per meter (SEK per year)', 'FontSize', 14);
    xlabel('Maintenance cost factor (percent)', 'FontSize', 14);
    grid on;
    legend({'Lifetime', 'Annuity'}, 'Location', 'best', 'FontSize', 12);
    
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels

    % Plot optimal grinding and tamping intervals
    figure;
    yyaxis left;
    plot(tc, opt_grinding, '-o', 'Color', 'b', 'LineWidth', 2);
    ylabel('Optimal grinding interval (months)', 'FontSize', 14);
    yyaxis right;
    plot(tc, opt_tamping, '-x', 'Color', 'r', 'LineWidth', 2);
    ylabel('Optimal gauge correction interval (months)', 'FontSize', 14);
    xlabel('Maintenance cost factor (percent)', 'FontSize', 14);
    grid on;
    legend({'Rail grinding', 'Gauge correction'}, 'Location', 'best', 'FontSize', 12);
    
    ax = gca;
    ax.TickLength = [0.02 0.02]; % Increase tick length
    ax.FontSize = 12; % Increase font size of tick labels
end

function plotSensitivityAnalysisRenewalCostsGaugeWidening(arg)
    % Extract input arguments
    opt_grinding = arg{1};
    opt_tamping = arg{2};
    ANNs = arg{3};
    lifetimes = arg{4};
    rc_rate = 100 * arg{5};
    gauge_widening_values = [1, 2, 3]; % in mm/y

    % Plot optimal lifetimes and ANNs
    figure;
    for i = 1:length(gauge_widening_values)
        subplot(3, 1, i);
        yyaxis left;
        plot(rc_rate, lifetimes(i,:), '-o', 'Color', 'b', 'LineWidth', 2);
        ylabel('Optimal Lifetime (years)', 'FontSize', 14);
        yyaxis right;
        plot(rc_rate, ANNs(i,:), '-x', 'Color', 'r', 'LineWidth', 2);
        ylabel('Annuity (SEK per year and meter)', 'FontSize', 14);
        xlabel('Increase in renewal costs (in percent)', 'FontSize', 14);
        grid on;
        legend({'Optimal Lifetime', 'ANN'}, 'Location', 'best', 'FontSize', 12);
        title(['Initial gauge widening = ', num2str(gauge_widening_values(i)), ' mm/y']);
    end

    % Plot optimal grinding and tamping intervals
    figure;
    for i = 1:length(gauge_widening_values)
        subplot(3, 1, i);
        yyaxis left;
        plot(rc_rate, opt_grinding(i,:), '-o', 'Color', 'b', 'LineWidth', 2);
        ylabel('Optimal Grinding Interval (months)');
        yyaxis right;
        plot(rc_rate, opt_tamping(i,:), '-x', 'Color', 'r', 'LineWidth', 2);
        ylabel('Optimal Tamping Interval (months)');
        xlabel('Increase in renewal costs (in percent)');
        grid on;
        legend({'Optimal Grinding Interval', 'Optimal Tamping Interval'}, 'Location', 'best');
        title(['Initial gauge widening = ', num2str(gauge_widening_values(i)), ' mm/y']);
    end
end


% function plot_figure(wanted_fig, arg)
% %PLOT_FIGURE Function for plotting figures
% %   Depending on input argument, plot specific figures
% 
% % gauge intervals (in mm)
% gauge = [1440,1445,1450,1455];
% 
% % months
% months = linspace(1,12,12);
% 
% figure
% if(strcmp(wanted_fig,'H_table'))
%     % visualize the H_table
%     plot(months, arg(1,:), 'LineStyle',"-")
%     hold on
%     plot(months, arg(2,:), 'LineStyle',"--")
%     plot(months, arg(3,:), 'LineStyle',"-.")
%     plot(months, arg(4,:), 'LineStyle',":")
%     legend('1440','1445','1450','1455','Location',"northwest")
%     xlabel('Months')
%     ylabel('{\it H}-index')
% elseif(strcmp(wanted_fig,'H_tables_heatmap'))
%     H_table_MB5 = arg{1};
%     H_table_MB6 = arg{2};
%     
%     % Plot the first heat map
%     subplot(1, 2, 1);
%     [X1, Y1] = meshgrid(months, gauge);
%     surf(X1, Y1, H_table_MB5)
%     xlabel('Months (since last grinding)')
%     ylabel('Gauge (in mm)')
%     zlabel('{\it H}-index (increase)')
%     
%     % Modify font size and tick labels for the first heat map
%     set(gca, 'FontSize', 12)
%     set(gca, 'TickLabelInterpreter', 'none')
%     set(gca, 'YDir', 'reverse')
%     
%     % Set the same color axis limits for both heat maps
%     caxis([min(H_table_MB5(:)), max(H_table_MB6(:))])
%     
%     % Plot the second heat map
%     subplot(1, 2, 2);
%     [X2, Y2] = meshgrid(months, gauge(3:4));
%     surf(X2, Y2, H_table_MB6)
%     xlabel('Months (since last grinding)')
%     ylabel('Gauge (in mm)')
%     zlabel('{\it H}-index (increase)')
%     
%     % Modify font size and tick labels for the second heat map
%     set(gca, 'FontSize', 12)
%     set(gca, 'TickLabelInterpreter', 'none')
%     set(gca, 'YDir', 'reverse')
% 
% elseif(strcmp(wanted_fig, 'historic'))
%     
%     H_curr_historic = arg{1};
%     rail_lifetime_months = 12*arg{2};
%     RCF_historic = arg{3};
%     gauge_curr_historic = arg{4};
%     
%     figure;
%     % First subplot for H-index and RCF residual
%     subplot(2, 1, 1);
%     yyaxis left;
%     plot(H_curr_historic, '-b', 'LineWidth', 2);
%     ylabel('H-index');
%     xlabel('Age in Months');
%     xlim([1, rail_lifetime_months])
%     grid on;
%     yyaxis right;
%     plot(RCF_historic, '-r', 'LineWidth', 2);
%     ylabel('RCF residual');
%     legend({'H-index', 'RCF residual'}, 'Location', 'best');
%     % Second subplot for gauge current historic
%     subplot(2, 1, 2);
%     plot(gauge_curr_historic, '-g', 'LineWidth', 2);
%     ylim([1440, 1455])
%     xlim([1, rail_lifetime_months])
%     ylabel('Gauge Value');
%     xlabel('Age in Months');
%     grid on;
%     legend({'Gauge Value'}, 'Location', 'best');
%     % Adjusting the subplot layout
%     subplot(2, 1, 1); % Ensuring the first subplot is active to add any further customizations
%     title('H-index and RCF Residual over Age in Months');
%     subplot(2, 1, 2); % Ensuring the second subplot is active to add any further customizations
%     title('Gauge Value over Age in Months');
%     
% elseif(strcmp(wanted_fig,'H_table5_heatmap'))
%     % as a heat map
%     [X,Y] = meshgrid(months,gauge);
%     surf(X,Y,arg)
%     colorbar
%     xlabel('Months (since last grinding)')
%     ylabel('Gauge (in mm)')
%     zlabel('{\it H}-index (increase)')
%     title('Maintenance table for MB5-H350LTH (inner rail)')
% elseif(strcmp(wanted_fig,'H_table6_heatmap'))
%     % as a heat map
%     [X,Y] = meshgrid(months,gauge(3:4));
%     surf(X,Y,arg)
%     colorbar
%     xlabel('Months (since last grinding)')
%     ylabel('Gauge (in mm)')
%     zlabel('{\it H}-index (increase)')    
%     title('Maintenance table for MB6-R400HT (inner rail)')
% elseif(strcmp(wanted_fig(1:end-4),'LCC_heatmap'))
%     % visualize the interpolated H_tables as a heatmap
%     % as a heat map
%     [nb_months_grinding,nb_months_tamping] = size(arg);
%     months_grinding = linspace(1,nb_months_grinding,nb_months_grinding);
%     months_tamping = linspace(1,nb_months_tamping,nb_months_tamping);
%     
%     [X,Y] = meshgrid(months_tamping,months_grinding);
%     surf(X,Y,arg)
%     colorbar
%     ylabel('Grinding interval (in months)','Rotation',-30)
%     xlabel('Gauge correction interval (in months)','Rotation',20)
%     zlabel('Annuity per meter (in SEK/year)')
%     title(append('Annuity of different maintenance strategies for ',wanted_fig(end-2:end)))
% elseif(strcmp(wanted_fig,'LCC_heatmaps'))
%     
%     LCC_MB5 = arg{1};
%     LCC_MB6 = arg{2};
%     
%     % Plot the first heat map
%     subplot(1, 2, 1);
%     [X1, Y1] = meshgrid(months, months);
%     surf(X1, Y1, LCC_MB5)
%     xlabel({'Gauge correction interval';'(in months)'},'Rotation',20)
%     ylabel({'Grinding interval';'(in months)'},'Rotation',-30)
%     zlabel('Total LCC (in SEK/meter)')
%     
%     % Modify font size and tick labels for the first heat map
%     set(gca, 'FontSize', 12)
%     set(gca, 'TickLabelInterpreter', 'none')
%     set(gca, 'YDir', 'reverse')
%     
%     % Set the same color axis limits for both heat maps
%     caxis([min(LCC_MB5(:)), max(LCC_MB6(:))])
%     
%     % Plot the second heat map
%     subplot(1, 2, 2);
%     [X2, Y2] = meshgrid(months, months);
%     surf(X2, Y2, LCC_MB6)
%     xlabel({'Gauge correction interval';'(in months)'},'Rotation',20)
%     ylabel({'Grinding interval';'(in months)'},'Rotation',-30)
%     zlabel('Total LCC (in SEK/meter)')
%     
%     % Modify font size and tick labels for the second heat map
%     set(gca, 'FontSize', 12)
%     set(gca, 'TickLabelInterpreter', 'none')
%     set(gca, 'YDir', 'reverse')
% 
% elseif(strcmp(wanted_fig,'interpolation'))
%     % visualize the interpolated H_tables
%     figure
%     plot(months, arg(1,:), 'LineStyle',"-")
%     hold on
%     plot(months, arg(2,:), 'LineStyle',"--")
%     plot(months, arg(3,:), 'LineStyle',"-.")
%     plot(months, arg(4,:), 'LineStyle',":")
%     legend('1440','1445','1450','1455','Location',"northwest")
%     set(gca, 'FontSize', 12)
%     xlabel('Months')
%     ylabel('{\it H}-index')
% elseif(strcmp(wanted_fig(end-12:end),'interpolation'))
%     % visualize the interpolated H_tables as a heatmap
%     % as a heat map
%     if(size(arg,1)==2)
%         gauge = gauge(3:4);
%     end
%     [~,nb_months] = size(arg);
%     months = linspace(1,nb_months,nb_months);
%     [X,Y] = meshgrid(months,gauge);
%     surf(X,Y,arg)
%     colorbar
%     xlabel('Months (since last grinding)')
%     ylabel('Gauge (in mm)')
%     zlabel('{\it H}-index (interpolated increase)')
%     title(wanted_fig)
%     %%% visualize average monthly deterioration in H-index
%     figure
%     x=[1:nb_months;1:nb_months;1:nb_months;1:nb_months];
%     y = arg./x;
%     surf(y)
%     xlabel('Months (since last grinding)')
%     ylabel('Gauge (in mm)')
%     zlabel('Monthly increase in {\it H}-index')
% elseif(strcmp(wanted_fig, 'sensitivity analysis - gauge widening'))
%     
%     opt_grinding = arg{1};
%     opt_tamping = arg{2};
%     ANNs = arg{3};
%     lifetimes = arg{4};
%     
%     % Define the initial gauge widening values
%     gauge_widening_values = [1, 2, 3]; % in mm/y
%     
%     % Plot the variation of optimal lifetimes and ANNs as bar charts
%     figure;
%     yyaxis left;
%     bar(gauge_widening_values, lifetimes, 0.2, 'FaceColor', 'b');
%     ylabel('Optimal Lifetime');
%     yyaxis right;
%     bar(gauge_widening_values + 0.3, ANNs, 0.2, 'FaceColor', 'r');
%     ylabel('Annuity (SEK per year and meter)');
%     xlabel('Initial gauge widening (mm/y)');
%     grid on;
%     legend({'Optimal Lifetime', 'ANN'}, 'Location', 'bestoutside');
%     
%     % Plot the variation of optimal grinding and tamping intervals as bar charts
%     figure;
%     yyaxis left;
%     bar(gauge_widening_values, opt_grinding, 0.2, 'FaceColor', 'b');
%     ylabel('Optimal Grinding Interval (months)');
%     yyaxis right;
%     bar(gauge_widening_values + 0.3, opt_tamping, 0.2, 'FaceColor', 'r');
%     ylabel('Optimal Tamping Interval (months)');
%     xlabel('Initial gauge widening (mm/y)');
%     grid on;
%     legend({'Optimal Grinding Interval', 'Optimal Tamping Interval'}, 'Location', 'bestoutside');
%     
% elseif(strcmp(wanted_fig, 'sensitivity analysis - renewal costs'))
%     
%     opt_grinding = arg{1};
%     opt_tamping = arg{2};
%     ANNs = arg{3};
%     lifetimes = arg{4};
%     rc_rate = 100*(arg{5}-1);
%     
%     % Plot the variation of optimal lifetimes and ANNs
%     figure;
%     yyaxis left;
%     plot(rc_rate, lifetimes, '-o', 'Color', 'b', 'LineWidth', 2);
%     ylabel('Optimal Lifetime (years)');
%     yyaxis right;
%     plot(rc_rate, ANNs, '-x', 'Color', 'r', 'LineWidth', 2);
%     ylabel('Annuity (SEK per year and meter)');
%     xlabel('Increase in renewal costs  (in percent)');
%     grid on;
%     legend({'Optimal Lifetime', 'ANN'}, 'Location', 'bestoutside');
%     
%     % Plot the variation of optimal grinding and tamping intervals
%     figure;
%     yyaxis left;
%     plot(rc_rate, opt_grinding, '-o', 'Color', 'b', 'LineWidth', 2);
%     ylabel('Optimal Grinding Interval (months)');
%     yyaxis right;
%     plot(rc_rate, opt_tamping, '-x', 'Color', 'r', 'LineWidth', 2);
%     ylabel('Optimal Tamping Interval (months)');
%     xlabel('Increase in renewal costs  (in percent)');
%     grid on;
%     legend({'Optimal Grinding Interval', 'Optimal Tamping Interval'}, 'Location', 'bestoutside');
%     
% elseif(strcmp(wanted_fig, 'sensitivity analysis - tamping costs'))
%     
%     opt_grinding = arg{1};
%     opt_tamping = arg{2};
%     ANNs = arg{3};
%     lifetimes = arg{4};
%     tc = 100*(arg{5}-1);
%     
%     % Plot the variation of optimal lifetimes and ANNs
%     figure;
%     yyaxis left;
%     plot(tc, lifetimes, '-o', 'Color', 'b', 'LineWidth', 2);
%     ylabel('Optimal Lifetime (years)');
%     yyaxis right;
%     plot(tc, ANNs, '-x', 'Color', 'r', 'LineWidth', 2);
%     ylabel('Annuity (SEK per year and meter)');
%     xlabel('Increase in tamping/grinding costs (in percent)');
%     grid on;
%     legend({'Optimal Lifetime', 'ANN'}, 'Location', 'bestoutside');
%     
%     % Plot the variation of optimal grinding and tamping intervals
%     figure;
%     yyaxis left;
%     plot(tc, opt_grinding, '-o', 'Color', 'b', 'LineWidth', 2);
%     ylabel('Optimal Grinding Interval (months)');
%     yyaxis right;
%     plot(tc, opt_tamping, '-x', 'Color', 'r', 'LineWidth', 2);
%     ylabel('Optimal Tamping Interval (months)');
%     xlabel('Increase in tamping/grinding costs (in percent)');
%     grid on;
%     legend({'Optimal Grinding Interval', 'Optimal Tamping Interval'}, 'Location', 'bestoutside');
%     
% elseif(strcmp(wanted_fig, 'sensitivity analysis - renewal costs & gauge widening'))
%     
%     ANNs = arg{1};
%     lifetimes = arg{2};
%     rc_rate = 100*(arg{3}-1);
%     
%     %%% Define variables for plotting
%     renewal_costs_rate = rc_rate;
%     gauge_widening_labels = {'Gauge Widening from 1mm/y', 'Gauge Widening from 2mm/y', 'Gauge Widening from 3mm/y'};
%     colors = {'b', 'g', 'r'};
%     
%     %%% plot the minimal annuity
%     % Plot ANN vs Renewal Costs
%     figure;
%     hold on;
%     for gw = 1:3
%         plot(renewal_costs_rate, ANNs(:, gw), 'DisplayName', gauge_widening_labels{gw}, 'Color', colors{gw}, 'Marker', 'o');
%     end
%     xlabel('Increase in renewal costs  (in percent)');
%     ylabel('Minimal annuity (SEK per year and meter)');
%     title('ANN vs Renewal Costs for Different Gauge Widenings');
%     legend show;
%     grid on;
%     hold off;
%     
%     %%% plot the lifetime
%     % Plot Lifetime vs Renewal Costs
%     figure;
%     hold on;
%     for gw = 1:3
%         plot(renewal_costs_rate, lifetimes(:, gw), 'DisplayName', gauge_widening_labels{gw}, 'Color', colors{gw}, 'Marker', 'o');
%     end
%     xlabel('Increase in renewal costs  (in percent)');
%     ylabel('Optimal lifetime (in years)');
%     title('Lifetime vs Renewal Costs for Different Gauge Widenings');
%     legend show;
%     grid on;
%     hold off;
%     
% end
% 
% end
% 