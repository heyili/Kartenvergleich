import timeit
import geopandas as gpd
from shapely.geometry import LineString, Point, MultiPoint
import find_nearst as fn
import helper
import helper as h


def load():
    # Read the shapefile
    DLM = gpd.read_file('Data/DLM_Strasse_Fahrbahnachse.shp')
    Here = gpd.read_file('Data/Here_Strasse_Buffer_neu.shp')

    geo_DLM = DLM.geometry
    geo_Here = Here.geometry

    DLM_street, Here_street = [], []

    for LineS in geo_DLM:
        route = helper.condense_route(LineS, 5)
        #res = get_points_from_linestring(route)
        DLM_street.append(route)

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
    print(hereS_ID)
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


def match_here_to_DLM(DLM, Here, Here_id):

     hereS_ID = []
     DLM = list(DLM.coords)
     #iterate through all points in one DLM street
     temp_id = []
     for idx in range(0, len(DLM)-1):
          start, end = h.cal_orthogonal(DLM[idx][0],DLM[idx][1],DLM[idx+1][0],DLM[idx+1][1])
          ref_line = LineString([start,end])
          #default if no here street is matched
          here_idx = -1
          min_value = float('inf')
          # for one point of a DLM street find the distance between it and all herestreets +
          for here_street in Here:
              intersection_point = ref_line.intersection(here_street)
              if intersection_point.is_empty == False:
                  distance = float('inf')
                  if type(intersection_point) == Point:
                    distance = h.get_distance_in_m_utm(start[0],start[1], intersection_point.x,intersection_point.y)
                  if type(intersection_point) == MultiPoint:
                    distance = h.get_distance_in_m_utm(start[0],start[1], intersection_point.geoms[0].x,intersection_point.geoms[0].y)
                  if distance < min_value:
                         min_value = distance
                         here_idx = Here.index(here_street)
          if here_idx != -1:
              temp_id.append(Here_id[here_idx])
          else:
              temp_id.append(here_idx)
     return temp_id

def Karten_vergleich():
    #load streets
    gdb_path = "Data/DLM_STRASSEN.gdb"
    street_path = "Data/2301_strassen_here.gpkg"
    start = timeit.default_timer()
    #rows can be modified
    DLM = gpd.read_file(gdb_path,  layer='DLM_STRASSEN', rows= 20000)
    stop = timeit.default_timer()
    print('Time for DLM street: ', stop - start)

    start = timeit.default_timer()
    Herestreet = gpd.read_file(street_path, layer ="2301_strassen_here", rows = 400000)
    stop = timeit.default_timer()
    print('Time for Herestreet: ', stop - start)


    DLM_street = DLM.geometry
    DLM_street_Linestring = []
    Here_street = list(Herestreet.geometry)

    for street in DLM_street:
        #condense DLM street with every 5 meters
        #res = helper.condense_route(list(street.geoms)[0], 10)
        # DLM_street_Linestring.append(LineString(res))

        # with out condense
        DLM_street_Linestring.append(list(street.geoms)[0])

    # n -> number of nearst neigbours
    nearst_here_streets = fn.find_nearst(DLM_street_Linestring, Here_street,20)
    nearst_linestring = []
    #  get the corresponding linstring
    for near in nearst_here_streets:
        temp = []
        for idx in near:
           temp.append(Here_street[idx])
        nearst_linestring.append(temp)

    mapping_result = []
    for idx, DLM in enumerate(DLM_street_Linestring):
        mapping_result.append(match_here_to_DLM(DLM, nearst_linestring[idx], nearst_here_streets[idx]))
    print(mapping_result)


if __name__ == '__main__':
    #load()
    Karten_vergleich()
