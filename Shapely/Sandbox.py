
from osgeo import ogr
from shapely.wkb import loads


source1 = ogr.Open("F:\Documents\DATA_Geo\04_BDD\BDD_ejx_v2\BDD_ejx\ENJEU_COMMUNE_S\N_COMMUNE_BDT.shp")
couche1 = source1.GetLayerByName("N_COMMUNE_BDT")
for element in couche:
		geom = loads(element.GetGeometryRef().ExportToWkb())
		if geom.geom_type == 'Point':
		   print geom.type
		   print geom
		if geom.geom_type == 'LineString':   
		   print geom.type
		   print geom
		if geom.geom_type == 'MultiLineString': 
		   print geom.type
		   print geom
		if geom.geom_type == 'MultiPolygon':
		   print geom.type
		   print geom
		if geom.geom_type == 'Polygon':
		   print geom.type
		   print geom


source1 = ogr.Open("testpoly.shp")
couche1 = source1.GetLayerByName("testpoly")