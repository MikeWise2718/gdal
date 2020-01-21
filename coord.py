from osgeo import osr, gdal
import os
import numpy as np
import argparse
import time

def process_geotiff_file(filename,fname,verbose=False,write_elev_file=False,write_elev_idx=False):
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
    dx = maxx-minx
    dy = maxy-miny
    xresmeter = 0
    if width>0:
        xresmeter = dx/width
    yresmeter = 0
    if height>0:
        yresmeter = dy/height

    # get skews 
    ulx, xres, xskew, uly, yskew, yres = ds.GetGeoTransform() 

    # get elevations
    band = ds.GetRasterBand(1)
    elevation = band.ReadAsArray()
    meanelev = np.mean(elevation)
    nxelev = elevation.shape[0]
    nyelev = elevation.shape[1]
    latmin = latlongminmin[0]
    latmax = latlongmaxmax[0]
    lngmin = latlongminmin[1]
    lngmax = latlongmaxmax[1]

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
        print(f"  xresmeter:{xresmeter} yresmeter:{yresmeter} ")
        print(f"  xskew:{xskew} yskew:{yskew} ")
        print(f"  elevation.shape:{elevation.shape}")
        print(f"  elevation mean:{meanelev}")

    # for row caol https://gis.stackexchange.com/a/221430/53850
    if (write_elev_file):
        print(elevation)
        start = time.time()
        nline = 0
        efilename ="output/"+ os.path.splitext(fname)[0]+".csvc"
        f = open(efilename,"w")
        f.write(f"# geotiff file with elevation data in csvc format")
        f.write(f"# csvc format is an extention of a CSV file with #-comments and embedded metadata")
        f.write(f"## fname:{fname}\n")
        f.write(f"## nrow:{nxelev}, ncol:{nyelev}, minx:{minx},maxx:{maxx},miny:{miny},maxy:{maxy}\n")
        f.write(f"## xres:{xres}, yres:{yres}, xskew:{xskew}, yskew:{yskew}\n")
        f.write(f"## latmin:{latmin}, latmax:{latmax}, lngmin:{lngmin}, lngmax:{lngmax}, ulx:{ulx}, uly:{uly}\n")
        f.write(f"## elevation.mean:{meanelev}\n")
        if write_elev_idx:
            f.write(f"row,col,elev\n")
        else:
            f.write(f"elev\n")
        for row in range(nxelev):
            for col in range(nyelev):
                nline += 1
                elv = "{0:.2f}".format(elevation[row][col])
                if write_elev_idx:
                    f.write(f"{row},{col},{elv}\n")
                else:
                    f.write(f"{elv}\n")
        f.close()  
        elap = time.time() - start
        print(f"wrote {nline} lines to {efilename} in {elap} secs")

    llmn = latlongminmin
    llmx = latlongmaxmax
    line = f"{fname},{width},{height},{minx},{maxx},{miny},{maxy},{llmn[0]},{llmx[0]},{llmn[1]},{llmx[1]},{ulx},{uly},{xres},{yres},{xskew},{yskew},{nxelev},{nyelev},{meanelev}"
    return line


def process_geotiff_dir(dirname,summary_file_name="tifinfo.csv",write_summary_file=False,write_elev_file=False,fext=".tif",write_elev_idx=False):
    ll = []
    header = "filename,width,height,minx,maxx,miny,maxy,latmin,latmax,lngmin,lngmax,ulx,uly,xes,yres,xskew,yskew,nxelev,nyelev,meanelev"
    ll.append(header)
    files = [f for f in os.listdir(dirname)]
    for f in files:
        fullname = dirname + "/" + f
        if fullname.endswith(fext):
            l = process_geotiff_file(fullname,f,verbose=True,write_elev_file=write_elev_file,write_elev_idx=write_elev_idx)
            ll.append(l)
    print(f"process_dir found {len(files)} files in {dirname}")

    if (write_summary_file):
        f = open(summary_file_name,"w")
        f.write("\n".join(ll))
        f.close()
        print(f"wrote {len(ll)} lines to {summary_file_name}")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process geotiff files into a csv or csvc format')

    parser.add_argument("--foo", action='store_true')
    parser.add_argument('-wsf',"--write_geotiff_summary", help='write geotiff summary csv',  action='store_true')
    parser.add_argument('-wef',"--write_elevation_files", help='write elevation files as csvc', action='store_true')
    parser.add_argument('-widx',"--write_elevation_idx", help='write index to elevation files', action='store_true')
    parser.add_argument('-gd',"--geotiff_directory",default="Geotiff/batch1-1", type=str, help='Geotiff directory',metavar="")
    parser.add_argument('-gbd',"--geotiff_big_directory",help='Geotiff big directory (Geotff/batch1)', action='store_true')

    args = parser.parse_args()
    foo = args.foo
    wsf = args.write_geotiff_summary
    wef = args.write_elevation_files
    widx = args.write_elevation_idx
    geodir = args.geotiff_directory 
    gbd = args.geotiff_big_directory
    if gbd:
        geodir = "Geotiff/batch1"
    print(f"args - wsf:{wsf} wef:{wef} gbd:{gbd} widx:{widx} geodir:{geodir}")
    process_geotiff_dir(geodir,write_summary_file=wsf,write_elev_file=wef,write_elev_idx=widx)
