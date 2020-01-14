from osgeo import osr, gdal
import os


def process_file(filename):
    # get the existing coordinate system
    ds = gdal.Open(filename)
    old_cs= osr.SpatialReference()
    old_cs.ImportFromWkt(ds.GetProjectionRef())

    # create the new coordinate system
    wgs84_wkt = """
    GEOGCS["WGS 84",
        DATUM["WGS_1984",
            SPHEROID["WGS 84",6378137,298.257223563,
                AUTHORITY["EPSG","7030"]],
            AUTHORITY["EPSG","6326"]],
        PRIMEM["Greenwich",0,
            AUTHORITY["EPSG","8901"]],
        UNIT["degree",0.01745329251994328,
            AUTHORITY["EPSG","9122"]],
        AUTHORITY["EPSG","4326"]]"""
    new_cs = osr.SpatialReference()
    new_cs .ImportFromWkt(wgs84_wkt)

    # create a transform object to convert between coordinate systems
    transform = osr.CoordinateTransformation(old_cs,new_cs) 

    #get the point to transform, pixel (0,0) in this case
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5] 

    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5] 
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3] 

    #get the coordinates in lat long
    latlongminmin = transform.TransformPoint(minx,miny) 
    latlongmaxmax = transform.TransformPoint(maxx,maxy) 
    totpix = width*height
    print(f"file:{filename}")
    print(f"  width:{width} height:{height} totpix{totpix}")
    print(f"  gt:{gt}")
    print(f"  minx:{minx} miny:{miny}")
    print(f"  maxx:{maxx} maxy:{maxy}")
    print(f"  latlongminmin:{latlongminmin}")
    print(f"  latlongmaxmax:{latlongmaxmax}")

def process_dir(dirname,fext):
    files = [f for f in os.listdir(dirname)]
    for f in files:
        fullname = dirname + "/" + f
        if fullname.endswith(fext):
            process_file(fullname)
    print(f"process_dir found {len(files)} files in {dirname}")

process_dir("Geotiff/batch1",".tif")
# process_file('Geotiff/be_09040831.tif')