import distance
import datetime
#nltkimport nltk
import dateutil.parser
import networkx as nx
import plotly.graph_objects as go


# pretty printing and niceties
from rich import print
from rich import inspect
from rich.progress import track

def string_to_date(d):
    example = "2020-10-07T11:19:18.000-0400"
    new_date = dateutil.parser.parse(d)
    return(new_date)

def get_time_difference_from_strings(start, end):
    start = string_to_date(start)
    end = string_to_date(end)
    difference = end - start
    return difference

def generate_nx_graph(all_epics_dict, issue_list, group_no_epics):

    already_on_graph = [] # tracks issue keys that are already on the graph
    #G = nx.random_geometric_graph(200, 0.125)
    G = nx.Graph()
    color_map = []  # stores the colors of each node

    # first construct the list of epics in the query, and No Epic
    # then add them first to the graph
    done_epics_temp = []
    print("issue list len(): %s" % len(issue_list))
    for i in issue_list:
        print("i: %s" % i)
        print("doing this key: %s" % i.key)
        if i.epic is not None:
            print("i.epic is not None")
            if all_epics_dict[i.epic] not in done_epics_temp:
                print("all_epics_dict[i.epic] not in done_epics_temp")
                G.add_node(all_epics_dict[i.epic])
                print("done G.add_node(all_epics_dict[i.epic]")
                #G.add_node(i.epic.split("-")[0] + " " + all_epics_dict[i.epic])
                color_map.append(0)
                print("done color_map.append(0)")
                done_epics_temp.append(all_epics_dict[i.epic])

    # go through all the issues and add nodes and edges for epics
    for i in track(issue_list, description="Generating NX graph: adding epics as nodes..."):  # progres
    # for i in issue_list:
        
        if i.epic is not None:
            G.add_node(i.key + " " + i.summary)
            color_map.append(1)
            #G.add_edge(i.key + " " + i.summary, i.epic.split("-")[0] + " " + all_epics_dict[i.epic])
            G.add_edge(i.key + " " + i.summary, all_epics_dict[i.epic])
        else:
            G.add_node(i.key + " " + i.summary)
            color_map.append(1)
            if group_no_epics:
                G.add_edge(i.key + " " + i.summary, "No Epic") # connects to "No Epic"

        if i.key not in already_on_graph:
            already_on_graph.append(i.key)

    # now let's add the issues that were linked but not part of the query
    for i in track(issue_list, description="Generating NX graph: adding linked issues as nodes..."):
        for l in i.linked_issue_keys:
            if l not in already_on_graph:
                G.add_node(l)
                color_map.append(2)
            G.add_edge(i.key + " " + i.summary, l)
            


    # instead of generating a whole graph, just generate posisions
    print("Generating positions (this may take awhile)... ")
    pos=nx.spring_layout(G)
    # then add position data to G object
    nx.set_node_attributes(G, pos, 'pos')

    # for x in G.nodes(data=True):
    for x in track(G.nodes(data=True), description="Converting position data from numpy array to list..."):
        # print(x)
        # print(x[1])
        # print(x[1]['pos'])
        # print(type(x[1]['pos']))
        # print(x[1]['pos'][0])
        # print(x[1]['pos'][1])
        # print("****")
        
        # converting position data from numpy array to list
        x[1]['pos'] = [x[1]['pos'][0], x[1]['pos'][1]]

    #inspect(color_map)

    # all the plotly stuff below
    return G, color_map


def plotly_graph(G, color_map):

    # this is simply plotting the edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)


    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='name',
        mode='lines')

    node_x = []
    node_y = []

    node_text = []

    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)
        node_text.append(str(node))

    node_text_truncated = []
    for n in node_text:
        # before
        # node_text_truncated.append(n[:14] + "...")
        print(n)
        if "Epic: " in n:
            node_text_truncated.append(n[5:])
        else:
            node_text_truncated.append(" ")

    #print(node_text_truncated)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        #mode='markers',
        mode='markers+text',
        hoverinfo='text',
        text=node_text_truncated,
        hovertext=node_text,

        marker=dict(
            showscale=False,
            # https://plotly.com/python/builtin-colorscales/
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Plasma',
            reversescale=True,
            color=[],
            size=7,
            # colorbar=dict(
            #     thickness=15,
            #     title='Node Connections',
            #     xanchor='left',
            #     titleside='right'
            # ),
            line_width=0.5))

    #print(node_trace)
 
    node_adjacencies = []

    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        #node_text.append('# of connections: '+str(len(adjacencies[1])))

    node_trace.marker.color = color_map # node_adjacencies
    node_trace.text = node_text_truncated   # where node text is added

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                    title='',
                    titlefont_size=16,
                    font=dict(
                        family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Oxygen-Sans, Ubuntu, Cantarell, Helvetica Neue, sans-serif",
                        size=8,
                        color="#ccc"
                    ),
                    showlegend=False,
                    hovermode='closest',
                    plot_bgcolor='#000',
                    paper_bgcolor='#000',
                    #plot_bgcolor='#e6e6e6',
                    #paper_bgcolor='#e6e6e6',
                    margin=dict(b=20,l=5,r=5,t=40),
                    # annotations=[ dict(
                    #     text="",
                    #     showarrow=False,
                    #     xref="paper", yref="paper",
                    #     x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    fig.update_traces(textposition='top center')
    #fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.write_html("templates/results.html")


    #plotly.offline.plot(fig, filename = 'plot.html', auto_open=False)

if __name__ == '__main__':
    main()