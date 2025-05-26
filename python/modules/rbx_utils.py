8# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 16:16:11 2021

@author: SEKNNO
"""
# %% imports
# imports
import os
import pandas as pd
import geopandas as gpd
import fiona
import copy
from fiona import supported_drivers
from geopandas.tools import sjoin
from geopandas.tools import overlay
from shapely.geometry import Point
from shapely.ops import unary_union
import numpy

def is_rbx_utils_loaded() -> bool:
    '''Check if rbx_utils.py is loaded'''
    print("RBX Utils laddades korrekt")
    return True


# Funktioner som används av SKB.ipynb

# %% FUNCTIONS
# FUNCTIONS
def create_dir(dir_path):
    """Creating directory

    Given the path, the functions creates a directory
    if there is none.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(dir_path + " created.")
    else:
        print(dir_path + " already exists. Not overwritten.")


def buffer_points(points):
    """Buffering points.

    For the given points,
    the function creates a specified sized buffer for these.
    """
    buffer_geom = points.geometry.buffer(0.5, cap_style=1)
    buffered_points = gpd.GeoDataFrame(geometry=buffer_geom)
    return (buffered_points)


def cluster_buffers(buffers):
    """Clustering buffer objects.

    Given the buffered points, the function creates clusters
    which are used to group points and later create polygons.
    """
    # Creating GeoSeries with unions of buffered points.
    buffers_union = gpd.GeoSeries(unary_union(buffers.geometry))
    # Exploding the unions in a new GeoDataFrame.
    clustered_buffers = buffers_union.explode(index_parts=False)
    clustered_buffers = gpd.GeoDataFrame(geometry=clustered_buffers)
    # Resetting indices
    clustered_buffers.reset_index(drop=True, inplace=True)
    # Sorting out geometry columns
    #clustered_buffers.geometry = clustered_buffers.iloc[:, 2]
    #clustered_buffers = clustered_buffers[["geometry"]]
    print(f"Clustered_buffers: {clustered_buffers.head(3)}")
    # Setting coordinate system for GeoDataFrame
    clustered_buffers.set_crs("epsg:3006", inplace=True)
    # Returning cluster GDF.
    return (clustered_buffers)


#def read_points(gdb, LG, line):
def read_points(gdb, LG, line, RBX_gdb_layers):
    """Reading information from file.

    Import points from gdb (which have had false alarms removed
    manually in MicroStation and then exported to gdb
    and Near3D (avst fas) computed)
    """
    # Defining layer name based on line number.
    point_layer = f"{LG}_{line}_RBX_clean"
    # Checking if layer name is relevant.
    if point_layer not in RBX_gdb_layers:
        # no points from which to make clusters: return nothing.
        return ([], [])
    # Reading file.
    points = gpd.read_file(gdb, layer=point_layer)
    # Creating new list with relevant coulmn.
    #points = points[["AVSTAND_FAS", "AVSTAND_HORISONTELLT", "geometry"]] ###### ÄNDRAT 2025-01-14 ######
    points = points[["AVST_F", "AVST_H", "geometry"]] ###### ÄNDRAT 2025-01-14 ######
    # Checking if lists are containing any columns.
    if len(points) == 0:
        # If empty, return empty list.
        return ([], [])
    # Returning points list.
    return (points)


def read_raw_RBX(raw_RBX_file):
    """Reading infomation from file

    Used to get the dz, the height, for points,
    which is not contained in the dgn-file.
    Reading the RAW RBX file and then adding the calculated value to 
    the actual point.
    """
    # Reading file
    raw_RBX = pd.read_csv(raw_RBX_file, header=None,
                          sep=" ", names=["x", "y", "z", "dz"])
    # Creating GeoDataFrame from the imported list and calculating
    # the dz value.
    raw_RBX_points = gpd.GeoDataFrame(
        raw_RBX, geometry=gpd.points_from_xy(
            raw_RBX.x, raw_RBX.y, (raw_RBX.z - raw_RBX.dz)))
    # Dropping the irrelevant information.
    raw_RBX_points.drop(["x", "y"], axis=1, inplace=True)
    # Returning the extended GDF with the dz value.
    return (raw_RBX_points)


#def make_RBX_polygons(points, voltage, LG, littera, RBX_class):
def make_RBX_polygons(points, voltage, LG, littera, RBX_class, RBX_distances):
    """Create polygons from the RBX points.

    Get max 3D distance from wire for RBX_class
    """
    RBX_dist = RBX_distances[voltage][RBX_class]
    # extract points within RBX_dist
    # RBX_class_points = points[points["AVSTAND_FAS"] <= RBX_dist] #### ÄNDRAT 2025-01-14
    RBX_class_points = points[points["AVST_F"] <= RBX_dist]
    if len(RBX_class_points) == 0:
        return ([], [])
    # buffer points, create clusters
    buffers = buffer_points(RBX_class_points)
    clusters = cluster_buffers(buffers)
    clusters['LG'] = LG
    clusters['littera'] = littera

    return (clusters, RBX_class_points)


#def set_class(points, voltage, LG, littera, RBX_class, RBX_class_nr):
def set_class(points, voltage, LG, littera, RBX_class, RBX_class_nr, RBX_distances):
    """Set "KLASS_TEMP" value for points.

    Setting value based on distance to line, type of voltage and RBX class.
    """
    # Deciding which distance is to be calculated
    RBX_dist = RBX_distances[voltage][RBX_class]
    # Filtering out points whos distance is less than the acceptable.
    # RBX_class_points = points[points["AVSTAND_FAS"] <= RBX_dist] #### ÄNDRAT 2025-01-14
    RBX_class_points = points[points["AVST_F"] <= RBX_dist]
    # Filtering out points whos distance is not less than the acceptable.
    # Not edited.
    # RBX_no_class_points = points[points["AVSTAND_FAS"] > RBX_dist] #### ÄNDRAT 2025-01-14
    RBX_no_class_points = points[points["AVST_F"] > RBX_dist]
    # Set the value of class for the relevant points.
    RBX_class_points["KLASS_TEMP"] = RBX_class_nr

    # Returning the the full points list, where some points has been changed.
    return (RBX_class_points._append(RBX_no_class_points))


def clip_polygons(clippee, clipper):
    """Clip overlay polygons.

    Using the higher class polygon as template,
    the function makes a cut in the lower class polygon
    so that no overlap exist.
    """
    # Check if the there is a lower class polygon.
    # If not, the returning empty list.
    if len(clippee) == 0:
        return ([], [])
    # Check if there is a higher class polygon,
    # if not, then returning the lower class polygon unclipped.
    if len(clipper) == 0:
        return clippee
    # Clipping the the higher class polygon out of the lower class polygon.
    clipped = overlay(clippee, clipper, how="difference")
    # Returning the clipped lower class polygon
    return clipped


def calculate_RBX_area(RBX):
    """Calculating the area for polygons."""
    # Check if the there is a polygon.
    # If not, the returning empty list.
    if len(RBX) == 0:
        return 0
    # Calculating area
    area = RBX.geometry.area.sum()
    return area


def get_attributes_from_points(polygons, points):
    """

    """
    if str(type(polygons)) != "<class 'geopandas.geodataframe.GeoDataFrame'>":
        return ([], [])
    polygons["polygon_ID"] = polygons.index
    print(f"Nr of points: {len(points)}")
    print(f"Nr of polygons: {len(polygons)}")

    points_with_ID = sjoin(points, polygons, how="inner")
    # sorted_points = points_with_ID.sort_values(by='AVSTAND_FAS') #### ÄNDRAT 2025-01-14
    sorted_points = points_with_ID.sort_values(by='AVST_F')
    closest_points = sorted_points.groupby('polygon_ID').first().reset_index()
    closest_points_full = copy.deepcopy(closest_points)
    # inplace för att ändra den faktiska punkten
    closest_points.drop(["geometry", "LG", "littera"], axis=1, inplace=True)
    print(closest_points[0:5])
    print(f"Number of closest points: {len(closest_points)}")

    # kopplar på information till polygon från closest point
    # tillfällig
    polys_ = polygons.merge(closest_points, on="polygon_ID")
    print(f"Original polygon columns: {polygons.columns}")
    print(f"Merged polygon columns: {polys_.columns}")

    # kolla koppling mellan denna och poly_
    #polys = polys_[["LG", "littera", "AVSTAND_FAS",
    #                "AVSTAND_HORISONTELLT", "geometry", "dz"]] #### ÄNDRAT 2025-01-14
    polys = polys_[["LG", "littera", "AVST_F",
                    "AVST_H", "geometry", "dz"]]
    print(f"Columns: {polys.columns}")

    return (polys, closest_points_full)


def set_z_to_points(points, raw_rbx_file):
    """Setting ground level z to clean points

    Z value is changed from the original \\
    z value (z + dz value of the clean point) \\
    to the z value from the same raw_rbx point (z - dz, ground level)

    Keyword arguments: \\
    points -- dataframe of verified rbx points \\
    raw_rbx -- dataframe of all rbx points \\
    raw_rbx_file -- text document containing information about the raw points

    out : dataframe(
        AVSTAND_FAS, \\
        AVSTAND_HORISONTELLT, \\
        geometry(x, y, z(ground level))
    )
    """
    # Checking if the input data is as GeoDataFrame
    # If not, returning empty list
    if str(type(points)) != "<class 'geopandas.geodataframe.GeoDataFrame'>":
        return ([], [])
    raw_rbx = pd.read_csv(raw_rbx_file, header=None,
                          sep=" ", names=["x", "y", "z",
                                          "dz", "LG", "littera"]
                          )

    # adding columns to points dataframe for x, y values.
    points["x"] = points.centroid.map(lambda p: p.x)
    points["y"] = points.centroid.map(lambda p: p.y)

    # creating container for numeric x, y, z values.

    # 2023-02-06
    points["dz"] = numpy.float64

    pointlst = []
    point_lst_dz = []
    no_ref_points = []
    # for each point in sorted db, getting the index for further comparison
    for ind1 in range(0, len(points)):
        checklst = []
        # for each point in the raw_rbx db,
        # getting the index for further comparison
        for ind2 in range(0, len(raw_rbx)):
            # validating if the x values and the y values are the same
            # for the clean_point and raw_point resp.
            if (round(points.x[ind1], 2) == raw_rbx.x[ind2]
                    and round(points.y[ind1], 2) == raw_rbx.y[ind2]):
                # if statement is true,
                # then the points are the same in x, y direction,
                # which means the z value can be changed
                # from dz (sorted point)
                # to z (raw_rbx_point, ground level).
                pointlst.append(
                    [
                        "", "", points.x[ind1], points.y[ind1],
                        round((raw_rbx.z[ind2] - raw_rbx.dz[ind2]), 1),
                        raw_rbx.dz[ind2]
                    ]
                )
                point_lst_dz.append(raw_rbx.dz[ind2])
                checklst.append(raw_rbx.dz[ind2])
                break
            else:
                continue
        # 2023-02-06
        if not checklst:
            no_ref_points.append(points.iloc[ind1])
        # 2022
        # else:
        #    continue
    # creating a dataframe, setting headers.
    #pointlst_df = pd.DataFrame(
    #    pointlst, columns=[
    #        "AVSTAND_FAS", "AVSTAND_HORISONTELLT",
    #        "x", "y", "z", "dz"]) ###### ÄNDRAT 2025-01-14
    pointlst_df = pd.DataFrame(
        pointlst, columns=[
            "AVSTAND_FAS", "AVST_H",
            "x", "y", "z", "dz"])    

    # creating points from the numeric values in the dataframe.
    newpointlst = gpd.GeoDataFrame(pointlst_df, geometry=gpd.points_from_xy(
        pointlst_df["x"], pointlst_df["y"], pointlst_df["z"]), crs="epsg:3006"
    )
    # checking that the length of points list (list in)
    # is equal to the length of the generated list (list out)
    if len(newpointlst) != len(points):
        return None

    # adding the old information to the new dataframe.
    #newpointlst["AVSTAND_FAS"] = points["AVSTAND_FAS"]
    #newpointlst["AVSTAND_HORISONTELLT"] = points["AVSTAND_HORISONTELLT"] #### ÄNDRAT 2025-01-14
    newpointlst["AVST_F"] = points["AVST_F"]
    newpointlst["AVST_H"] = points["AVST_H"]

    
    # removing the columns for the numeric x, y, z values
    newpointlst.drop(["x", "y", "z"], axis=1, inplace=True)

    # returning the new dataframe
    return newpointlst


def round_values(gdf):
    """Rounding up values.

    When getting a GeoDataFrame,
    the funtion is rounding the value up to one decimal
    for the "AVSTAND_FAS" and "AVSTAND_HORISONTELLT"
    """
    # Sorting out the relevant columns
    #rndvals = ['AVSTAND_FAS', 'AVSTAND_HORISONTELLT', 'dz'] ##### ÄNDRAT 2025-01-14
    rndvals = ['AVST_F', 'AVST_H', 'dz']
    columns = gdf.columns
    # Rounding up the value per column
    for col in rndvals:
        if col in columns:
            gdf[col] = round(gdf[col], 1)
    # Returning updated GeoDataFrame
    return gdf


def sort_columns(gdf):
    """Sorting GeoDataFrame for consistency

    Given the output GeoDataFrame,
    the function sorts the relevant columns in right order.
    """
    # Creating list of how the GDF is going to be sorted
#    order = ['geometry', 'AVSTAND_FAS', 'AVSTAND_HORISONTELLT',
#             'dz', 'LG', "littera", 'KLASS_TEMP'] #### ÄNDRAT 2025-01-14
    order = ['geometry', 'AVST_F', 'AVST_H',
             'dz', 'LG', "littera", 'KLASS_TEMP']
    # Creating empty GDF
    out_gdf = gpd.GeoDataFrame()
    # Get all columns
    columns = gdf.columns
    # Sorting per column
    for col in order:
        if col in columns:
            out_gdf[col] = gdf[col]
    # Return sorted GDF
    return out_gdf


'''def RBX_polys_stats(row):
    """Main function of RBX_polygons.py"""

    # Fecthing values, row by row, from the line dataframe.
    LG = row["LG"]
    line = row["line"]
    littera = row["Littera"]
    voltage = row["Spänning"]

    # Prompting which line is handled
    print(f"Doing {LG}_{line}")

    # the cleaned RBX points that where imported from dgn to gdb
    points = read_points(working_gdb, LG, line)
    if str(type(points)) != "<class 'geopandas.geodataframe.GeoDataFrame'>":
        print("No points in list")
        return ([], [])

    # the raw RBX points from the txt file.
    # Needed because they have dZ attribute
    raw_RBX_file = os.path.join(
        powerlines_folder, LG,
        f"line_{line}", "RBX", str("RBX_raw.txt"))

    # Using "set_z_points" function to add z value to all points.
    points = set_z_to_points(points, raw_RBX_file)

    # Creating polygons from distance to line.
    if len(points) > 0:
        red_polygons, red_points = make_RBX_polygons(
            points, voltage, LG, littera, "red")
        orange_polygons, orange_points = make_RBX_polygons(
            points, voltage, LG, littera, "orange")
        yellow_polygons, yellow_points = make_RBX_polygons(
            points, voltage, LG, littera, "yellow")

    # Creating a default value and column for "KLASS_TEMP".
    points["KLASS_TEMP"] = 0
    # Using the "set_class" function for setting relevant "KLASS_TEMP" value
    # for all points.
    if len(points) > 0:
        points = set_class(
            points, voltage, LG, littera, "yellow", 1)
        points = set_class(
            points, voltage, LG, littera, "orange", 2)
        points = set_class(
            points, voltage, LG, littera, "red", 3)

    # Getting all the closest points from the unclipped yellow polygons.
    # The unclipped yellow polygons are used to cluster all points in groups,
    # sort them as descending by "AVSTAND_FAS" and get the point with smallest
    # distance for each group.
    yellow_polygons["polygon_ID"] = yellow_polygons.index
    closest_points = sjoin(yellow_points, yellow_polygons, how="inner")
    # closest_points = closest_points.sort_values(by='AVSTAND_FAS') #### ÄNDRAT 2025-01-14
    closest_points = closest_points.sort_values(by='AVST_F')
    closest_points = closest_points.groupby('polygon_ID')

    # Sorting out the closest point for each group.
    all_closest_points_lst = []
    for spt in closest_points:
        for i in spt:
            if type(i) is not int:
                all_closest_points_lst.append(i.iloc[0])

    # Cutting the polygons.
    _yellow_RBX = clip_polygons(yellow_polygons, orange_polygons)
    _orange_RBX = clip_polygons(orange_polygons, red_polygons)
    _red_RBX = red_polygons

    # Adding values to polygons from points.
    # Returning polygons and all points in groups.
    yellow_RBX_all = get_attributes_from_points(
        _yellow_RBX, yellow_points)
    orange_RBX_all = get_attributes_from_points(
        _orange_RBX, orange_points)
    red_RBX_all = get_attributes_from_points(_red_RBX, red_points)

    # Sorting relevant data from get_attributes_from_point.
    if len(yellow_RBX_all[:-1]) > 0:
        yellow_RBX = yellow_RBX_all[:-1][0]
    else:
        yellow_RBX = []
    if len(orange_RBX_all[:-1]) > 0:
        orange_RBX = orange_RBX_all[:-1][0]
    else:
        orange_RBX = []
    if len(red_RBX_all[:-1]) > 0:
        red_RBX = red_RBX_all[:-1][0]
    else:
        red_RBX = []

    RBX_all_lines["yellow"].append(yellow_RBX)
    RBX_all_lines["orange"].append(orange_RBX)
    RBX_all_lines["red"].append(red_RBX)

    # Placing "KLASS_TEMP" and "Area" values for polygons
    all_RBX_list = []
    for cnt, gdf in enumerate([yellow_RBX, orange_RBX, red_RBX]):
        if len(gdf) > 0:
            gdf['KLASS_TEMP'] = cnt+1
            gdf['area'] = gdf.geometry.area
            all_RBX_list.append(gdf)

    # for each color, calculate RBX_area and number of clusters,
    # and append to summary.
    yellow_area = calculate_RBX_area(yellow_RBX)
    orange_area = calculate_RBX_area(orange_RBX)
    red_area = calculate_RBX_area(red_RBX)

    nr_yellow = len(yellow_RBX)
    nr_orange = len(orange_RBX)
    nr_red = len(red_RBX)

    area_summary.append([LG, line, littera, yellow_area,
                        orange_area, red_area, nr_yellow, nr_orange, nr_red])

    # Creating Geodataframe out of a list
    all_RBX = gpd.GeoDataFrame(
        pd.concat(all_RBX_list, ignore_index=True), crs="epsg:3006")

    ###################################### 2024-12-18: ORDNA FÄLT HÄR NEDANFÖR? ####################################
    all_RBX["LG"] = all_RBX["LG"]
    all_RBX.drop(
        ["area", "LG", "littera"],  # , "Shape_Length", "Shape_Area"
        axis=1,
        inplace=True)

    # Rounding up values for heights and distances.
    all_RBX = round_values(all_RBX)
    all_RBX_out = sort_columns(all_RBX)
    all_RBX_out.to_file(os.path.join(
        RBX_shape_folder, f"{LG}_{line}_RBX.shp"), crs="epsg:3006")

    # Handling all the closest points.
    # Adding KLASS_TEMP values and rounding values up.
    # Creating a dataframe and writing it to a .shp-file.
    all_closest_points = gpd.GeoDataFrame(
        all_closest_points_lst, crs="epsg:3006").reset_index()
    # Creaing default value and column for "KLASS_TEMP"
    all_closest_points["KLASS_TEMP"] = int(0)
    # Using the "set_class" function for setting relevant "KLASS_TEMP" value
    # for all closest points.
    if len(all_closest_points) > 0:
        all_closest_points = set_class(
            all_closest_points, voltage, LG, littera, "yellow", 1)
        all_closest_points = set_class(
            all_closest_points, voltage, LG, littera, "orange", 2)
        all_closest_points = set_class(
            all_closest_points, voltage, LG, littera, "red", 3)
    # Cleaning up GeoDataFrame from information that is not relevant.
    all_closest_points.drop(
        ["index", "index_right", "polygon_ID", "LG", "littera"],
        axis=1,
        inplace=True)
    # Rounding up values for relevant columns.
    all_closest_points = round_values(all_closest_points)
    # Sorting columns for consistency.
    all_closest_points_out = sort_columns(all_closest_points)
    all_closest_points_out.to_file(os.path.join(
        RBX_shape_folder, f"{LG}_{line}_closest_points.shp"), crs="epsg:3006")

    # Handling all the clean RBX points.
    points = round_values(points)
    points_out = sort_columns(points)
    # points["LG"] = points["LG"].convert_dtypes('int64')
    points_out.to_file(os.path.join(
        RBX_shape_folder, f"{LG}_{line}_all_points.shp"), crs="epsg:3006")
'''