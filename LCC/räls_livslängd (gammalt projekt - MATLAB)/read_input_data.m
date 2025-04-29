function [H_table_MB5,H_table_MB6, nat_wear_MB5, nat_wear_MB6, risk_MB5, ...
    risk_MB6, gauge_widening, RCF_residual_MB5, RCF_residual_MB6, ...
    RCF_depth_MB5, RCF_depth_MB6] = read_input_data(sheet)
%READ_INPUT_DATA Reads simulation results
%   Based on simulation results, this function reads resulting tables

%%% Set the filename and rows
filename = "./Wear/mistra_results.xlsx";
xlRange_MB5 = "B3:M6"; % MB5, H-index values
xlRange_MB6 = "B8:M9"; % MB6, H-index values

xlRange_MB5_natWear = "B12:M15"; % MB5, natural wear values
xlRange_MB6_natWear = "B17:M18"; % MB6, natural wear values

xlRange_MB5_RCF_residual = "B21:M24"; % MB5, RCF residual values
xlRange_MB6_RCF_residual = "B26:M27"; % MB6, RCF residual values

xlRange_MB5_RCF_depth = "B30:M33"; % MB5, RCF depth values
xlRange_MB6_RCF_depth = "B35:M36"; % MB6, RCF depth values

%%% read H-index values from table with mechanical simulation results
H_table_MB5 = xlsread(filename,sheet,xlRange_MB5);
H_table_MB6_ex = xlsread(filename,sheet,xlRange_MB6);
H_table_MB6 = [H_table_MB5(1:2,:);H_table_MB6_ex];

%%% read natural wear values
nat_wear_MB5 = xlsread(filename,sheet,xlRange_MB5_natWear);
nat_wear_MB6_ex = xlsread(filename,sheet,xlRange_MB6_natWear);
nat_wear_MB6 = [nat_wear_MB5(1:2,:);nat_wear_MB6_ex];

%%% read RCF residual values
RCF_residual_MB5 = xlsread(filename,sheet,xlRange_MB5_RCF_residual);
RCF_residual_MB6_ex = xlsread(filename,sheet,xlRange_MB6_RCF_residual);
RCF_residual_MB6 = [RCF_residual_MB5(1:2,:);RCF_residual_MB6_ex];

%%% read RCF depth values
RCF_depth_MB5 = xlsread(filename,sheet,xlRange_MB5_RCF_depth);
RCF_depth_MB6_ex = xlsread(filename,sheet,xlRange_MB6_RCF_depth);
RCF_depth_MB6 = [RCF_depth_MB5(1:2,:);RCF_depth_MB6_ex];

%%% read average yearly gauge widening for different initial widenings (1, 2 or 3 mm)
gauge_widening = xlsread(filename,"gauge","B2:D9");

%%% manually set input data (for derailement risk, i.e., max. lifetime)
risk_MB5 = zeros(4,12);
risk_MB6 = zeros(2,12);
if(strcmp(sheet,"H_30t"))
    % MB5
    risk_MB5(1,:) = 1.0e+07 * [    0.0722    0.0744    0.0915    0.1124    0.1264    0.1445    0.1686 ...
        0.2216    0.2890    0.4014    0.6262    1.3005];
    risk_MB5(2,:) = 1.0e+07 * [    0.1485    0.1708    0.1927    0.2301    0.2529    0.2821    0.3211 ...
        0.4046    0.5298    0.7386    1.1560    2.4565];
    risk_MB5(3,:) = 1.0e+07 * [    0.2047    0.2146    0.2312    0.2569    0.3071    0.3372    0.3853 ...
        0.4720    0.6262    0.8670    1.3487    2.7455];
    risk_MB5(4,:) = 1.0e+07 * [    0.2489    0.2540    0.2890    0.3265    0.3612    0.4197    0.4817 ...
        0.5876    0.7586    1.0275    1.5413    3.1790];
    % MB6
    risk_MB6(1,:) = 1.0e+07 * [    0.1565    0.1576    0.1878    0.2194    0.2529    0.2890    0.3372 ...
        0.4335    0.5900    0.8349    1.3005    2.6492];
    risk_MB6(2,:) = 1.0e+07 * [    0.2328    0.2408    0.2697    0.2729    0.3191    0.3509    0.4094 ...
        0.4624    0.6262    0.8670    1.3487    2.7455];
elseif(strcmp(sheet,"H_32t"))
    % MB5
    risk_MB5(1,:) = 1.0e+07 * [
        0.0803    0.0963    0.0963    0.1177    0.1264    0.1514    0.1766 ...
        0.2216    0.2890    0.4174    0.6502    1.3487];
    risk_MB5(2,:) = 1.0e+07 * [
        0.2007    0.1970    0.2119    0.2301    0.2589    0.2890    0.3291 ...
        0.4142    0.5539    0.7707    1.2042    2.4565];
    risk_MB5(3,:) = 1.0e+07 * [
        0.2288    0.2452    0.2601    0.2729    0.3251    0.3647    0.4174 ...
        0.5298    0.6743    0.9312    1.4209    2.9382];
    risk_MB5(4,:) = 1.0e+07 * [
        0.2609    0.2671    0.2986    0.3425    0.3793    0.4266    0.4977 ...
        0.5780    0.7345    1.0115    1.5413    3.1308];
    % MB6
    risk_MB6(1,:) = 1.0e+07 * [
        0.1365    0.1664    0.1878    0.2194    0.2589    0.3028    0.3372 ...
        0.4431    0.5780    0.8188    1.2764    2.6492];
    risk_MB6(2,:) = 1.0e+07 * [
        0.1525    0.2102    0.2312    0.2462    0.2890    0.3372    0.3773 ...
        0.4528    0.6141    0.8509    1.3246    2.7455];
end
end