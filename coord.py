from osgeo import osr, gdal
import os
import numpy as np

def process_file(filename,fname,verbose=False):
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

    # get skews 
    ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform() 

    # get elevations
    band = ds.GetRasterBand(1)
    elevation = band.ReadAsArray()
    meanelev = np.mean(elevation)
    nxelev = elevation.shape[0]
    nyelev = elevation.shape[1]

    if (verbose):
        print(f"file:{filename}")
        print(f"  width:{width} height:{height} totpix{totpix}")
        print(f"  gt:{gt}")
        print(f"  minx:{minx} miny:{miny}")
        print(f"  maxx:{maxx} maxy:{maxy}")
        print(f"  latlongminmin:{latlongminmin}")
        print(f"  latlongmaxmax:{latlongmaxmax}")
        print(f"  ulx:{ulx} uly:{uly} ")
        print(f"  xres:{xres} yres:{yres} ")
        print(f"  xskew:{xskew} yskew:{yskew} ")
        print(f"  elevation.shape:{elevation.shape}")
        print(f"  elevation mean:{meanelev}")


    llmn = latlongminmin
    llmx = latlongmaxmax
    line = f"{fname},{width},{height},{minx},{maxx},{miny},{maxy},{llmn[0]},{llmx[0]},{llmn[1]},{llmx[1]},{ulx},{uly},{xres},{yres},{xskew},{yskew},{nxelev},{nyelev},{meanelev}"
    return line


def process_dir(dirname,fext,olistfname="tifinfo.csv",writefile=False):
    ll = []
    header = "filename,width,height,minx,maxx,miny,maxy,latmin,latmax,lngmin,lngmax,ulx,uly,xes,yres,xskew,yskew,nxelev,nyelev,meanelev"
    ll.append(header)
    files = [f for f in os.listdir(dirname)]
    for f in files:
        fullname = dirname + "/" + f
        if fullname.endswith(fext):
            l = process_file(fullname,f,True)
            ll.append(l)
    print(f"process_dir found {len(files)} files in {dirname}")

    if (writefile):
        f = open(olistfname,"w")
        f.write("\n".join(ll))
        f.close()
        print(f"wrote {olistfname}")



process_dir("Geotiff/batch1",".tif",writefile=True)
# process_file('Geotiff/be_09040831.tif')