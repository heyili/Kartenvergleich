import math
from shapely.geometry import LineString, Point, MultiPoint


def cal_orthogonal(p1_long,p1_lat,p2_long,p2_lat):
    """
    calculate the orthogonal line of two given points
    :return start point, end point
    """
    angel = get_bearing_in_grad_utm(p1_long,p1_lat,p2_long,p2_lat)
    start_point = get_point_from_bearing_and_distance_utm2(p2_long, p2_lat, angel + 90, 20)
    end_point = get_point_from_bearing_and_distance_utm2(p2_long, p2_lat, angel - 90, 20)
    return start_point, end_point


def get_distance_in_m_utm(lon1, lat1, lon2, lat2):
    distance = math.sqrt(((lon1 - lon2) ** 2) + ((lat1 - lat2) ** 2))
    return distance


def get_point_from_bearing_and_distance_utm2(lon1, lat1, grad, distance_in_m):
    distance = distance_in_m
    bearing =  grad
    angle =     90 - bearing
    bearing = math.radians(bearing)
    angle =   math.radians(angle)
    #polar coordinates
    dist_x, dist_y = \
        (distance * math.cos(angle), distance * math.sin(angle))
    xfinal, yfinal = (lon1 + dist_x, lat1 + dist_y)
    return (xfinal, yfinal)

def get_bearing_in_grad_utm(lon1, lat1, lon2, lat2):
    # print('in get_grad-------------------------------')
    h1 = lon2 - lon1
    h2 = lat2 - lat1
    try:
        if h1 >= 0 and h2 >= 0:
            grad = math.atan(h1/h2) * 180/3.14
        elif h1 >= 0 and h2 <= 0:
            grad = math.atan(h1/h2) * 180/3.14 + 180
        elif h1 <= 0 and h2 <= 0:
            grad = math.atan(h1/h2) * 180/3.14 + 180
        else:
            grad = math.atan(h1/h2) * 180/3.14 + 360
    except Exception as e:
        #print('Error in get_grad: ', e)
        if h1 > 0:
            grad = 90
        elif h1 < 0:
            grad = 270
        else:
            grad = 0
    return grad

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

def condense_route(route, factor):
    condensed_route = LineString()
    init_point = []
    init_point = get_points_from_linestring(route)
    start, end = Point(init_point[0]), Point(init_point[1])
    distance = start.distance(end)
    step = distance/factor
    angel = get_bearing_in_grad_utm(init_point[0][0], init_point[0][1],init_point[1][0], init_point[1][1])
    result = []
    result.append(init_point[0])
    start_x, start_y = init_point[0][0], init_point[0][1]
    for i in range(round(step)-1):
        x,y = get_point_from_bearing_and_distance_utm2(start_x,start_y, angel, factor)
        start_x, start_y = x,y
        result.append([x,y])
    result.append(init_point[1])
    return result

