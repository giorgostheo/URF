import geopandas as gpd
from shapely.geometry import LineString, Point
from IPython.display import display, clear_output

def viz(lines, start_p, end_p):
    '''
    Vizualize the route alongisde the starting and the ending point. All routes will be in the same fig with the same color.
    '''
    m = gpd.GeoDataFrame([[i, LineString(line)] for i, line in enumerate(lines)], columns=['id', 'geom'], geometry='geom', crs=4326).explore()
    m = start_p.buffer(0.001).explore(m=m, color='red')
    display(end_p.buffer(0.002).explore(m=m, color='black'))
    # input()
    # clear_output()
    
def sepviz(lines, start_p, end_p):
    '''
    Vizualize the route alongisde the starting and the ending point. Each route will be separatelly shown.
    '''
    for line in lines:
        print(len(line))
        viz([line], start_p, end_p)

def viz_start_stop(start_p, end_p):
    '''
    Vizualize the starting and the ending point of a trip.
    '''
    m = start_p.buffer(0.001).explore(color='red')
    display(end_p.buffer(0.001).explore(m=m, color='black'))