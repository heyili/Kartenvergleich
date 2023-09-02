from sklearn.neighbors import NearestNeighbors, BallTree
import numpy as np
from shapely.geometry import LineString, Point, MultiPoint
import pandas as pd
import rtree
import timeit

def custom_metric(x, y):
    return 2 * np.sum(np.abs(x - y))

def custom_metric_2(array1, array2):
    length1 = array1.shape[0]
    length2 = array2.shape[0]
    # Reshape arrays
    reshaped_array1 = array1.reshape(int(length1/2), 2)
    reshaped_array2 = array2.reshape(int(length2/2), 2)
    total_distance = 0
    for p1 in reshaped_array1:
        for p2 in reshaped_array2:
            total_distance += np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    # for p1, p2 in zip(array1.reshape(int(array1.shape[0]/2) , 2), array2.reshape(int(array2.shape[0]/2), 2)):
    #     total_distance += np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    return total_distance / length2

def find_nearst(DLM, Here, n):
    idx = rtree.index.Index()
    #build DLM tree
    result = []
    for i, line in enumerate(Here):
        idx.insert(i, line.bounds)

    DLM_neigbour = []
    for i, line in enumerate(DLM):
       #first try with one street TODO
       result = list(idx.nearest((DLM[0].bounds), n))
       if result:
           DLM_neigbour.append(result)
       else:
           raise ValueError("The required number of nearst neigbour is too large")
    #print(DLM_neigbour)
    return result
if __name__ == '__main__':
    # line = LineString([(0, 0), (1, 1), (2, 2), (3, 3)])
    # line_2 = LineString([(0, 0), (1, 1), (2, 2), (3, 3)])
    #
    # X = np.array([line,line])
    # nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree', metric= custom_metric).fit(X)
    # distances, indices = nbrs.kneighbors(X)
    # print(distances, indices)
    #
    # data = {
    # 'streets': [np.array([[0, 0], [1, 1], [2, 2]]),
    # np.array([[1, 1], [2, 2], [3, 3]]),
    # np.array([[2, 2], [3, 3], [4, 4]]),
    # np.array([[10, 10], [11, 11], [12, 12]])],
    # 'ref_street': [np.array([[0, 0], [0, 1], [0, 2]]),
    # np.array([[1, 0], [1, 1], [1, 2]]),
    # np.array([[2, 0], [2, 1], [2, 2]]),
    # np.array([[10, 10], [11, 11], [12, 10]])]
    # }
    # df = pd.DataFrame(data)
    #
    start = timeit.default_timer()
    #Your statements here
    # Create 4 linestrings
    line1 = LineString([(0, 0), (1, 1)])
    line2 = LineString([(1, 1), (2, 2), (3, 3)])
    line3 = LineString([(3, 3), (4, 4)])
    line4 = LineString([(0, 1), (1, 0)])

    line5 = LineString([(0, 0), (1, 1),(3, 5)])
    line6 = LineString([(1, 1), (2, 2.8), (3, 3)])
    line7 = LineString([(3, 3), (4, 7.6),(2.3, 4.5)])
    line8 = LineString([(0, 1), (1, 9)])
    # List of all linestrings
    lines = [line1, line2, line3, line4]
    lines_2 = [line5, line6, line7, line8]
    find_nearst(lines, lines_2,2)
    # Create an R-tree index
    idx = rtree.index.Index()

    # Insert linestrings into the R-tree index with their bounding boxes
    # The integer i is an identifier for each linestring
    for i, line in enumerate(lines):
        idx.insert(i, line.bounds)

    # Fetch linestrings that intersect with the bounding box of line1
    result = list(idx.intersection(line1.bounds))

    # Filter out line1 itself
    result = [lines[i] for i in result if lines[i] != line1]

    # If there are candidates, find the one with the smallest Hausdorff distance
    if result:
        hausdorff_distances = [line1.hausdorff_distance(line) for line in result]
        nearest_line = min(result, key=lambda line: line1.hausdorff_distance(line))
        print(f"Nearest line to line1 based on Hausdorff distance: {nearest_line}")

    else:

        print("No neighbors found for line1.")

    print(hausdorff_distances)
    stop = timeit.default_timer()
    print('Time: ', stop - start)
