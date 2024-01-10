Scripts for quality control of delivered point cloulds (las), ortho photos etc

Ideas:

- Are tiles (point cloud .las and ortho photo .tif) delivered and do they contain data?
  Input data: 
    shape file / gdb feature class with tiling schema (polygons)
    shape file / gdb feature class with powerline centerline (line)
    folder with delivered tiles
  Method:
    Buffer centerline to create area of interest for analysis (probably 65 m on each side = 130 m corridor)
    List the tiles that overlap the area of interest
    Check that these tiles exist and that file size > 0
  
- Do point density and coverage meet the criteria (at least x pt/m2, counting only last and single returns, in at least y % of all 5*5 m squares on ground)? Do all 5*5 m squares on ground (except water) have returns, i.e. no empty 5*5 m squares on land?
  Input data:
    GeoTiffs with number of points per m2 (1 m squares or 5 m squares?) exported from TerraScan
    Area of interest (buffered centerline as described above)
    Polygon layer with water bodies?
  Method:
    If GeoTiff has 1 m pixels, aggregate to 5 m. Clip those squares that are within the area of interest but outside water bodies. 
    Count number of 5 m pixels with >= twice the required point density, >= required point density, >= half the required point density, zero points.
    Compute percentage of 5 m pixels with < required point density
