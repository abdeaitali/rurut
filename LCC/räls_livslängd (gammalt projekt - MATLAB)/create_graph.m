function [G] = create_graph(table)
%CREATE_GRAPH Create graph from lookip tables
%   Using lookup tables, create a graph with different paths-maintenance
%   strategies


% average yearly gauge widening (in mm/year)
avg_yearly_gauge_widening = 0.2;

% maintenance frequency
nb_yearly_grinding = 1;
nb_yearly_tamping = 1;


% create empy graph
G = digraph();

% add the inital node (brand new rail)
G = addnode(G, {'init'});

% add the last node indicating the need for renewal
G = addnode(G, {'renew'});





% plot the graph
plot(G)

end

