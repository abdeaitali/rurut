V = [ ...
    1.029   1.000   1.060   1.048   nan	    nan	    nan
    1.049   1.014   1.038   1.092   1.075   nan	    nan
    nan	    1.039   1.079   1.036   1.029   1.003   nan
    nan	    nan	    1.042   1.072   1.000   0.998   1.028
    nan	    nan	    nan	    1.038   1.024   1.076   1.022
    nan	    nan	    nan	    nan	    1.082   0.997   1.011]


X = [8 10 15    25   35    45   52]; % using the X and Y from your code rather than
Y = [5 10 16.25 22.5 28.75 35];      % from your image, which are 5 less
% make a scatteredInterpolant of the points where V is non-NaN
[XX,YY] = meshgrid(X,Y);
idx = ~isnan(V(:));
I = scatteredInterpolant(XX(idx),YY(idx),V(idx));
% interpolate/extrapolate to all points
Z = reshape(I(XX,YY),numel(Y),[])


% visualization
x_lim = [min(X) max(X)];
y_lim = [min(Y) max(Y)];
z_lim = [min(Z(:)) max(Z(:))];
temp = {V Z};
names = {'V' 'Z'};
for ii = [1 2]
    subplot(2,1,ii)
    surface(XX,YY,temp{ii},'FaceColor','interp')
    set(gca(),'YDir','reverse')
    view(2)
    xlim(x_lim);
    ylim(y_lim);
    xlabel('X');
    ylabel('Y');
    colorbar();
    caxis(z_lim);
    title(names{ii});
end