import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import datetime
from shapely.geometry import LineString, Point
from IPython.display import display, clear_output
from misc import viz
from fastdtw import fastdtw

def _candidates(a, b, roads, current_route):

    '''
    This is the function that finds the candidates for the next point in the route.

    Parameters
    ----------
    a : Point - the current point
    b : Point - the ending point
    roads : GeoDataFrame - the roads dataframe
    current_route : list - the current route
    '''
    # find the roads that intersect with buffered a
    inter_roads = roads[roads.buffer(2e-4).intersects(a.buffer(2e-4))][['trafdir', 'geometry']]
    endps = []

    # this is used to find the endpoints of the roads based on road direction
    for _,road in inter_roads.iterrows():
        if road.trafdir == 'FT':
            endps.append(road.geometry.boundary[1])
        elif road.trafdir == 'TF':
            endps.append(road.geometry.boundary[0])
        elif road.trafdir == 'TW':
            endps.append(road.geometry.boundary[0])
            endps.append(road.geometry.boundary[1])
        else:
            pass # this is a non vehicle road

    res = []
    for point in endps:

        if LineString([a,point]).length==0:
            continue
        if len(current_route)>1 and LineString(current_route).buffer(1e-4).intersects(point.buffer(1e-4)):
            continue

        # return all the candidates that do not intersect with the current route
        res.append((Point(point), Point(point).distance(b)))

    return res


def route(a,b, roads, max_queue_len=-1, result_len=1, routedif=0.001):
    '''
    Find a route from a to b. The route is a list of points that can easily form a linestring. 

    Parameters
    ----------
    a : Point - the starting point
    b : Point - the ending point
    roads : GeoDataFrame - the roads dataframe
    max_queue_len : int - the maximum length of the routes queue. If -1, then the queue is infinite.
    result_len : int - the number of results you want. If -1, then fetch all (will take a long time)
    routedif : float - the max DTW distance between two routes to be considered as the similar.

    '''
    routes = [([a], np.inf)] # priority queue for the routes
    results = []

    while len(routes)>0 and len(results)<result_len:
        
        route, score = routes.pop(0)
        pnt = route[-1]

        if pnt.distance(b)<0.002:
            # if route is complete, add it to the results and remove all other routes that are too similar
            results.append(route)
            routes = [sroute for sroute in routes if fastdtw([(a.x, a.y) for a in sroute[0]],[(a.x, a.y) for a in route])[0]>routedif]
            continue

        new_pnts = _candidates(pnt, b, roads, route)

        for new_p, new_score in new_pnts[::-1]:
            routes.insert(0, (route+[new_p], new_score))

        routes.sort(key=lambda a: a[1])
        clear_output()

        print(len(routes), len(results), routes[0][1], flush=True)
        routes = routes[:max_queue_len]
    return results
