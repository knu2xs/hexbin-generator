# import installed modules
import arcpy
import os.path
from math import floor, fsum, sqrt, pow

# import an included helper module function
from hexbin_generator.get_business_analyst_data_paths import get_usa_data_path


def get_extent_length_height_list_sorted(polygon_feature_class):
    """
    Get a list of the height and width values for all the features sorted from smallest to largest.
    :param polygon_feature_class: Input feature class of polygons.
    :return: List of numeric values containing both the height and width of every feature.
    """
    # list to store the values
    size_list = []

    # iterate the feature class
    for feature in arcpy.da.SearchCursor(polygon_feature_class, 'SHAPE@'):

        # add the height and width of this feature to the list
        size_list.append(feature[0].extent.height)
        size_list.append(feature[0].extent.width)

    # sort the list
    size_list.sort()

    # give it back
    return size_list


def get_mean(value_list):
    """
    Simple - get the flippin'  mean - the average.
    :param value_list: List of numeric values.
    :return: Floating point number representing the average of the numeric input values in the list.
    """
    # get the count of values
    value_count = len(value_list)

    # get the sum of values and divide it by the count of values
    return fsum(value_list) / value_count


def get_median(value_list):
    """
    Get the flippin' median - the middle number when all the numbers are arranged in order.
    :param value_list: List of numeric values.
    :return: The median number.
    """
    # get the count of values
    value_count = len(value_list)

    # if the cont of values is divisible by two - thus is even
    if value_count % 2 == 0:

        # get the integer of the count divided by two, the middle number in the list
        median_index = value_count / 2

        # return the exact middle number in the list
        return value_list[median_index - 1]

    # otherwise, if the count of values is odd
    else:

        # get the integer of the count plus one divided by two, the number below the middle in the list
        median_index = (value_count + 1) / 2

        # sum the two middle numbers, and divide the result by two
        return (value_list[median_index - 1] + value_list[median_index]) / 2


def get_lower_upper_quartile(value_list):
    """
    Get the lower and upper quartiles for a list of numbers.
    :param value_list: List of numeric values.
    :return: Two numbers, the lower and the upper quartile values.
    """
    # get the count of values
    value_count = len(value_list)

    # get the count location where the bottom quarter is, add just over a third, 5/12, then round down to the closest
    #    integer
    q1_index = floor(value_count/4 + 5/12)

    # get the value between the previous calculation, and the integer it was rounded down to
    h = value_count/4 + 5/12 - q1_index

    # get the bottom quartile
    q1 = (1 - h) * value_list[q1_index - 1] + h * value_list[q1_index]

    # calculate the index of the upper quarter
    k = int(value_count - q1_index + 1)

    # get the top quartile
    q2 = (1 - h) * value_list[k + 1] + h * value_list[k]

    # return the quartiles
    return q1, q2


def winsorize_value(X, quartile_values):
    """
    Determine if input value is an outlier by comparing to lower and upper quartiles.
    :param X: Number.
    :param quartile_values: Pair of values, the lower and upper quartiles
    :return: Value, if an outlier, Winsorized.
    """
    # if the value is in the lower quartile, a low outlier, raise up to the lower quartile
    if X < quartile_values[0]:
        return quartile_values[0]

    # if the value is in the upper quartile, a high outlier, lower to the upper quartile
    elif X > quartile_values[1]:
        return quartile_values[1]

    # otherwise the value is not an outlier - return it unchanged
    else:
        return X


def get_winsorized_list(X):
    """
    Winsorize the input list to remove outliers.
    :param X: List of numeric values.
    :return: Winsorized list of values.
    """
    # get the upper and lower quartiles
    quartile_values = get_lower_upper_quartile(X)

    # create new list by windsorizing the values
    return [winsorize_value(value, quartile_values) for value in X]


def get_hex_area_from_short_diagonal(short_diagonal):
    """
    Get the hexagon area from the short diagonal of the hexagon.
    :param short_diagonal: Short diagonal dimension for the hexagon.
    :return: Area in square units for the hexagon.
    """
    return 1.5 * sqrt(3) * pow(short_diagonal / sqrt(3), 2)


def get_hex_area(block_group_feature_class):
    """
    Get the hexagon area using the winsorized width and height values from the spatial extents of the input block
    group polygons.
    :param block_group_feature_class: Feature class or feature layer of block groups delineating the area of interest.
    :return: Area in square units for the hexagon.
    """
    return get_hex_area_from_short_diagonal(
        get_mean(
            get_winsorized_list(
                get_extent_length_height_list_sorted(block_group_feature_class)
            )
        )
    )


def get_hexbins_full_extent(block_groups, output_hexbin_feature_class):
    """
    Get hexbins covering the full rectangular extent of the area of interest.
    :param block_groups: Block groups covering the area of interest.
    :param output_hexbin_feature_class: Output path to the feature class to store the hexbins.
    :return: Path to the output hexbin feature class.
    """
    # get a describe object of the block groups
    describe = arcpy.Describe(block_groups)

    # use the generate tesselation tool to build the hexbins
    return arcpy.GenerateTessellation_management(
        Output_Feature_Class=output_hexbin_feature_class,
        Extent=describe.extent,                             # get the extent from the describe object
        Shape_Type='HEXAGON',
        Size=get_hex_area(block_groups),                    # using the logic above to get the hexagon area
        Spatial_Reference=describe.spatialReference         # use the same spatial reference as the input block groups
    )[0]


def get_hexbins_from_block_groups(block_groups, output_hexbin_feature_class):
    """
    Get hexbins covering the geometric area of interest defined by the block groups.
    :param block_groups: Block groups defining the area of interest.
    :param output_hexbin_feature_class: Output path to the feature class to store the hexbins.
    :return: Path to the output hexbin feature class.
    """
    # create layers for both the block groups and the hexbins convering the full rectangular extent of the area of
    # interest
    block_group_layer = arcpy.MakeFeatureLayer_management(block_groups, 'block_group_layer')
    hexbin_layer = arcpy.MakeFeatureLayer_management(
        get_hexbins_full_extent(block_groups, output_hexbin_feature_class),  # builds the hexbins feature class
        'hexbins_layer'
    )

    # select the hexbins not intersecting the geometry defined as the area of interest
    arcpy.SelectLayerByLocation_management(
        in_layer=hexbin_layer,
        overlap_type='INTERSECT',
        select_features=block_group_layer,
        selection_type='NEW_SELECTION',
        invert_spatial_relationship='INVERT'
    )

    # delete the hexbins not intersecting the geometry of the area of interest
    arcpy.DeleteFeatures_management(hexbin_layer)

    # return the hexbin feature class
    return output_hexbin_feature_class


def get_hexbins_by_cbsa(layer_with_cbsa_selected, output_hexbin_feature_class):
    """
    Based on a single CBSA selected, get the hexbins based on the size of the block groups in the CBSA.
    :param layer_with_cbsa_selected: Layer object with a single CBSA selected.
    :param output_hexbin_feature_class: Path to where hexbin feature class will be stored.
    :return: Feature class of hexbins covering the area of interest.
    """
    # get the data path to where the Business Analyst data is located
    block_group_feature_class = os.path.join(get_usa_data_path(), r'Data\Demographic Data\esri_bg.bds')

    # create a layer for the block group data
    block_group_layer = arcpy.MakeFeatureLayer_management(block_group_feature_class, 'block_group_lyr')

    # select the block groups in the CBSA
    arcpy.SelectLayerByLocation_management(
        in_layer=block_group_layer,
        overlap_type='INTERSECT',
        select_features=layer_with_cbsa_selected,
        selection_type='NEW_SELECTION'
    )

    # get the hexbins
    return get_hexbins_from_block_groups(block_group_layer, output_hexbin_feature_class)

