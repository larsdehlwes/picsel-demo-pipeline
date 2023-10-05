import xarray as xr
import numpy as np
from matplotlib.colors import rgb2hex, LinearSegmentedColormap
import matplotlib.pyplot as plt 
import geopandas as gp
from geojson import Feature, LineString, FeatureCollection, Polygon
import geojson
import shapely

from io import BytesIO
from datetime import datetime

import boto3
s3 = boto3.client('s3')
bucket = boto3.resource('s3').Bucket('picsel-demo-input')

def validate_filename(filenamestring, fmt='data/era5land_%Y-%m-%d.nc'):
    try:
        return datetime.strptime(filenamestring, fmt)
    except ValueError:
        return False

for file in bucket.objects.filter(Prefix='data/'):
    print(file.key)
    date_object = validate_filename(file.key)
    if date_object:
        tempFile = BytesIO()
        #s3.download_fileobj('picsel-demo-input', file.key, tempFile)
        file.Object().download_fileobj(tempFile)
        tempFile.seek(0)
        
        ds = xr.open_dataset(tempFile, engine="scipy")
        print(ds)
        ds["t2m"] = ds["t2m"] - 273.15
        t2marr = ds.t2m.mean(dim=["time"], skipna=True)
        
        figure = plt.figure()
        ax = figure.add_subplot(111)
        levels = range(15,37,2)
        contours = t2marr.plot.contourf(ax=ax, levels=levels, cmap=plt.cm.jet)
        outputPlotBuffer = BytesIO()
        plt.savefig(outputPlotBuffer, format='png')
        outputPlotBuffer.seek(0)
        s3.put_object(Body=outputPlotBuffer, Bucket='picsel-demo-output', Key=f'plots/temperature_contours_{date_object.strftime("%Y-%m-%d")}.png', ContentType= 'image/png')
        
        polygons = []
        
        print(dir(type(contours)))
        print(len(contours.collections))
        features = []
        for i, col in enumerate(contours.collections):
        #for level, col in zip(contours.levels[1:], contours.collections):
            # Loop through all polygons that have the same intensity level
            color = col.get_facecolor()
            #print(dir(type(col)))
            approx_temp = (contours.levels[i])
            for contour_path in col.get_paths(): 
                # Create the polygon for this intensity level
                # The first polygon in the path is the main one, the following ones are "holes"
                for ncp,cp in enumerate(contour_path.to_polygons()):
                    x = cp[:,0]
                    y = cp[:,1]
                    new_shape = shapely.geometry.Polygon([(i[0], i[1]) for i in zip(x,y)])
                    if ncp == 0:
                        poly = new_shape
                    else:
                        # Remove the holes if there are any
                        poly = poly.difference(new_shape)
                        # Can also be left out if you want to include all rings
        
                # do something with polygon
                #print(poly)
                polygons.append(poly)
                properties = {
                    "fill": rgb2hex(color[0]),
                    "approxTemperature": f"{round(approx_temp)}°C",
                }
                features.append(Feature(geometry=poly, properties=properties))
        
        print(len(features))
        
        feature_collection = FeatureCollection(features)
        geojson_dump = geojson.dumps(feature_collection, sort_keys=True)
        s3.put_object(Body=bytes(geojson_dump.encode('UTF-8')), Bucket='picsel-demo-output', Key=f'contours/temperature_contours_{date_object.strftime("%Y-%m-%d")}.geojson')
        
        tparr = ds.tp.sum(dim=["time"], skipna=True)
        tparr = 1000*tparr
        
        figure = plt.figure()
        ax = figure.add_subplot(111)
        levels = [0,5,10,20,40,80,160,320,640,1280]
        contours = tparr.plot.contourf(ax=ax, levels=levels, cmap=plt.cm.cool)
        outputPlotBuffer = BytesIO()
        plt.savefig(outputPlotBuffer, format='png')
        outputPlotBuffer.seek(0)
        s3.put_object(Body=outputPlotBuffer, Bucket='picsel-demo-output', Key=f'plots/precipitation_contours_{date_object.strftime("%Y-%m-%d")}.png', ContentType= 'image/png')
        
        polygons = []
        
        print(dir(type(contours)))
        print(len(contours.collections))
        features = []
        for i, col in enumerate(contours.collections):
        #for level, col in zip(contours.levels[1:], contours.collections):
            # Loop through all polygons that have the same intensity level
            color = col.get_facecolor()
            #print(dir(type(col)))
            upper_bound_precipitation = contours.levels[i+1]
            for contour_path in col.get_paths(): 
                # Create the polygon for this intensity level
                # The first polygon in the path is the main one, the following ones are "holes"
                for ncp,cp in enumerate(contour_path.to_polygons()):
                    x = cp[:,0]
                    y = cp[:,1]
                    new_shape = shapely.geometry.Polygon([(i[0], i[1]) for i in zip(x,y)])
                    if ncp == 0:
                        poly = new_shape
                    else:
                        # Remove the holes if there are any
                        poly = poly.difference(new_shape)
                        # Can also be left out if you want to include all rings
        
                # do something with polygon
                #print(poly)
                polygons.append(poly)
                properties = {
                    "fill": rgb2hex(color[0]),
                    "upperBoundPrecipitation": f"<{round(upper_bound_precipitation)}mm",
                }
                features.append(Feature(geometry=poly, properties=properties))
        
        print(len(features))
        
        feature_collection = FeatureCollection(features)
        geojson_dump = geojson.dumps(feature_collection, sort_keys=True)
        s3.put_object(Body=bytes(geojson_dump.encode('UTF-8')), Bucket='picsel-demo-output', Key=f'contours/precipitation_contours_{date_object.strftime("%Y-%m-%d")}.geojson')



