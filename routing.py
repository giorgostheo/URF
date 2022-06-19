import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import datetime
from shapely.geometry import LineString, Point, MultiPoint, Polygon
from IPython.display import display, clear_output
from misc import viz
from fastdtw import fastdtw
import networkx as nx
from tqdm.auto import tqdm
from sklearn.cluster import DBSCAN

def meanpoints(lst, default=Point((0.0, 0.0))):
    '''
    Get mean point of a list of points.

    Parameters
    ----------
    lst : list
        list of points
    default : Point   
        default value if list is empty

    Returns
    -------
    Point
        mean point
    '''
    if len(lst)==0:
        print('same')
        return default
    else:
        return Point(np.mean([[a.x, a.y] for a in lst], axis=0))


def create_graph( roads, reps, save=False ,fname="road_graph.gpickle"):
    '''
    Create road network graph based on the linestring roads (for the edges) and the reps (for the nodes).

    Parameters
    ----------

    roads : gpd.GeoDataFrame
        roads dataframe
    reps : gpd.GeoDataFrame
        nodes dataframe
    save : bool
        if True, save the graph to a file
    fname : str
        file name to save the graph to
    
    Returns
    -------
    nx.Graph
        road network graph
    '''
    G = nx.DiGraph()
    G.add_nodes_from(range(len(reps)))
    for a,b,c in roads[['start_id','end_id', 'weights']].values:
        G.add_edge(a, b, weight=c)
    if save:
        nx.write_gpickle(G, fname)
    else:
        return G
    

def create_node_info(roads_path='data/nyc_roads/geo_export_05dcab6d-50ed-427f-aae3-61ecc2069210.shp', save=False, road_nodes_fname='roadsfornx.pkl', reps_fname='reps.pkl'):
    '''
    Create node information for the road network.

    Parameters
    ----------
    roads_path : str
        path to the roads shapefile
    save : bool
        if True, save the node information to a file
    road_nodes_fname : str
        file name to save the road network graph to
    reps_fname : str
        file name to save the node information to

    Returns
    -------
    roads : gpd.GeoDataFrame
        roads dataframe
    reps : gpd.GeoDataFrame
        nodes dataframe

    '''
    path_to_data = gpd.datasets.get_path("nybb")
    gdf = gpd.read_file(path_to_data)
    manh = gdf.loc[gdf.BoroName=='Manhattan'].to_crs(4326)

    roads = gpd.read_file(roads_path, mask=manh)[['trafdir', 'geometry']]

    print('Road directions - starts/stops')
    notw = roads[roads.trafdir!='TW']
    tw = roads[roads.trafdir=='TW']
    tw['trafdir'] = 'TF'
    tw2 = tw.copy()
    tw2['trafdir'] = 'FT'
    roadsv2 = pd.concat([notw, tw, tw2])
    roadsv2 = roadsv2.loc[roadsv2.trafdir!='NV'].reset_index(drop=True)
    sps = []
    eps = []
    for _,road in roadsv2.iterrows():
        if road.trafdir == 'FT':
            sps.append(road.geometry.boundary[0]) 
            eps.append(road.geometry.boundary[1]) 

        elif road.trafdir == 'TF':
            sps.append(road.geometry.boundary[1]) 
            eps.append(road.geometry.boundary[0]) 

    starts = gpd.GeoDataFrame(geometry=sps, crs=4326)
    starts['label'] = 'start'
    stops = gpd.GeoDataFrame(geometry=eps, crs=4326)
    stops['label'] = 'end'

    sall = pd.concat([starts, stops])
    print('Clustering')
    X = sall.geometry.apply(lambda a: np.array([a.x, a.y]))
    X = np.vstack([val for val in X.values])

    clustering = DBSCAN(eps=1e-4, min_samples=2).fit(X)
    sall['cls'] = clustering.labels_

    print('creating nodes')
    pnts = gpd.GeoSeries(sall.groupby('cls').apply(lambda a: meanpoints(a.geometry.tolist(),0))[1:], crs=4326)

    for i in tqdm(range(len(roadsv2))):
        start_p = sall.loc[i].iloc[0].cls
        end_p = sall.loc[i].iloc[1].cls
        # break
        roadsv2.loc[i, 'start2'] = start_p
        roadsv2.loc[i, 'end2'] = end_p

    rds = roadsv2.loc[(roadsv2.start2!=-1) & (roadsv2.end2!=-1)]
    rds['weights'] = rds.apply(lambda a: pnts[a.start2].distance(pnts[a.end2]), axis=1)


    rds = rds.drop(['geometry'], axis=1)
    rds.rename({'start2':'start_id', 'end2':'end_id'}, axis=1, inplace=True)
    if save:
        print('saving...')
        rds.to_pickle(road_nodes_fname)
        pnts.to_pickle(reps_fname)
    else:
        return rds, pnts


def Groute(G, a, b, reps):
    st, ed = reps.distance(a).argmin(), reps.distance(b).argmin()
    # print(nx.shortest_path(G, source=st, target=ed, weight='weight'))
    return LineString(reps.loc[nx.shortest_path(G, source=st, target=ed, weight='weight')].geometry.tolist())