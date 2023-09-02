import sqlite3
import timeit

import fiona
import geopandas as gpd
import helper as h
import shapely
from shapely.geometry import LineString, Point, MultiPoint
import numpy as np
import find_nearst as fn


#paul fragen wegen  ball tree
# verdichten 5 m
# runtime tracking
# intersection länge vergleich
def load():
    # Read the shapefile
    DLM = gpd.read_file('Data/DLM_Strasse_Fahrbahnachse.shp')
    Here = gpd.read_file('Data/Here_Strasse_Buffer_neu.shp')

    geo_DLM = DLM.geometry
    geo_Here = Here.geometry

    DLM_street, Here_street = [], []

    for LineS in geo_DLM:
        res = get_points_from_linestring(LineS)
        DLM_street.append(res)

    for LineS in geo_Here:
        Here_street.append(LineS)


    hereS_ID = []

    for street in DLM_street:
        #iterate through all points in one DLM street
        temp_id = []
        for idx in range(0, len(street)-1):
             start, end = h.cal_orthogonal(street[idx][0],street[idx][1],street[idx+1][0],street[idx+1][1])
             ref_line = LineString([start,end])
             #default if no here street is matched
             here_idx = -1
             min_value = float('inf')

             # for one point of a DLM street find the distance between it and all herestreets +
             for here_street in Here_street:
                 intersection_point = ref_line.intersection(here_street)
                 if intersection_point.is_empty == False:
                     distance = h.get_distance_in_m_utm(start[0],start[1], intersection_point.x,intersection_point.y)
                     if distance < min_value:
                            min_value = distance
                            here_idx = Here_street.index(here_street)
             temp_id.append(here_idx)
        hereS_ID.append(temp_id)

    return hereS_ID
    ####example####
    # street1 = (1,2), (2,3), (3,4)
    # street2 = (2,2), (3,3)
def card_comparsion(lon_1, lat_1,lon_2, lat_2, here_streets):
    start, end = h.cal_orthogonal(lon_1, lat_1,lon_2, lat_2)
    orthogonal = LineString(start, end)
    result = []
    for street in here_streets:
        intersection = orthogonal.intersection(street)
        distance = 0
        result.append(distance)

def get_points_from_linestring(ref_route):
    """
    get all points from a given linestring
    :param ref_route: route in Linestring
    :type ref_route: Linestring
    :return: all points from the route
    :rtype: array
    """
    ref_x, ref_y = ref_route.xy
    ref_arr = []
    for idx, x in enumerate(ref_x):
        ref_arr.append([x,ref_y[idx]])
    return ref_arr

if __name__ == '__main__':
    gdb_path = "Data/DLM_STRASSEN.gdb"
    street_path = "Data/2301_strassen_here.gpkg"
    layers = fiona.listlayers(street_path)

    print(layers)

    start = timeit.default_timer()

    # chunk_size = 50000  # Define a reasonable chunk size based on your memory availability
    # offset = 0
    # conn = sqlite3.connect('mydata.db')
    # while True:
    #     try:
    #         # Read a chunk of data
    #         chunk = gpd.read_file(gdb_path, layer='DLM_STRASSEN', rows=chunk_size, skiprows=offset)
    #
    #         # If the chunk is empty, we've reached the end of the file
    #         if not len(chunk):
    #             break
    #
    #         # Write the chunk to the database
    #         chunk.to_sql('my_table', conn, if_exists='append', index=False)
    #
    #         # Update the offset
    #         offset += chunk_size
    #
    #     except MemoryError:
    #         print("Memory error occurred!")
    #         break
    #

    columns_to_load = ['geometry']
    with fiona.open(gdb_path, layer='DLM_STRASSEN') as src:
     num_rows = len(src)
    print(num_rows)


    with fiona.open(street_path, layer ="2301_strassen_here") as src:
     num_rows = len(src)
    print(num_rows)

    #DLM has Multilinestring
    start = timeit.default_timer()
    DLM = gpd.read_file(gdb_path,  layer='DLM_STRASSEN', rows= 2)
    stop = timeit.default_timer()
    print('Time for DLM street: ', stop - start)

    start = timeit.default_timer()
    Herestreet = gpd.read_file(street_path, layer ="2301_strassen_here", rows = 200)
    stop = timeit.default_timer()
    print('Time for Herestreet: ', stop - start)
    layers = fiona.listlayers(gdb_path)

    # DLM.to_file("DLM.shp")
    # Herestreet.to_file("HERE.shp")
    #
    # start = timeit.default_timer()
    # DLM_shp = gpd.read_file("DLM.shp")
    # stop = timeit.default_timer()
    # print('Time for dlm shp: ', stop - start)
    #
    # start = timeit.default_timer()
    # Here_shp = gpd.read_file("HERE.shp")
    # stop = timeit.default_timer()
    # print('Time for Here shp: ', stop - start)


    DLM_street = DLM.geometry
    #DLM_street_Linestring = [lambda x: DLM_street list[x]]
    DLM_street_Linestring = []
    Here_street = list(Herestreet.geometry)
    for street in DLM_street:

        DLM_street_Linestring.append(list(street.geoms)[0])

    fn.find_nearst(DLM_street_Linestring, Here_street,1)

    # Print layers (you can choose the one you need from here)
   #  for layer in layers:
   #      print(layer)
   #
   #  with fiona.open(street_path, layer='strassen_neu') as src:
   #   #Get the schema of the data, which contains the column names (properties)
   #     schema = src.schema
   #     columns = list(schema['properties'].keys())
   #  print(columns)
   # #street = gpd.read_file("Data/DLM_STRASSEN.gdb", layer = "strassen_neu")
   #  with fiona.open(gdb_path, layer='DLM_STRASSEN') as src:
   #  # Get the schema of the data, which contains the column names (properties)
   #      schema = src.schema
   #      columns = list(schema['properties'].keys())
   #
   #  print(columns)
#     gdf = gpd.read_file(gdb_path, layer='DLM_STRASSEN')
#     print("sdsd")
#     # Filter to only linestring geometries (if needed)
#     linestrings_gdf = gdf[gdf.geometry.geom_type == "LineString"]
#     linestrings_gdf.to_file("linestrings.shp")
#     #database = gpd.read_file("Data/strassen_neu_10753080473457119842.gpkg", layer = "strassen_neu", driver = "GPKG")
#     print("sdsd")
#     streets = [
#         [0,0,1,1,2,2,3,4],
#         [1, 1, 2, 2, 3, 3],
#         [2, 2, 3, 3, 4, 4],
#         [10, 10, 11, 11, 12, 12]
#     ]
#    # print(load())
#
# # See PyCharm help at https://www.jetbrains.com/help/pycharm/
