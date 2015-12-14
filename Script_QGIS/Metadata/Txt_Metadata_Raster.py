4. #!/usr/bin/env Python
# -*-coding:Utf-8 -*

import sys #ok
import os
import time
from PyQt4.QtCore import * #ok
from PyQt4.QtGui import * 
import qgis
import gdal
import osr
 
def CreateFile(self):
	"""creer un fichier"""
	create = open(self, "w")
	create.close()

def WriteFile(path,texte):
	"""ecrire dans un fichier"""
	writing = open(path, 'a')
	writing.write(texte+'\n')
	writing.close()


#selection de la couche vecteur en cours
LayerUSED = qgis.utils.iface.activeLayer().dataProvider().dataSourceUri()
path=LayerUSED.split('|')[0]
fileInfo = QFileInfo(path)
baseName = fileInfo.baseName()
layer = gdal.Open(path)

# creation du fichier texte
date1 = time.strftime("%d_%m_%Y_%H_%M_%S", time.localtime())
FichierTXT=path+'_'+date1+'.txt'
CreateFile(FichierTXT)

# Infos general sur le fichier (forcity, date etc)
WriteFile(FichierTXT,"############################################")
WriteFile(FichierTXT,"#")
WriteFile(FichierTXT,"#\t _____           ____ _ _")        
WriteFile(FichierTXT,"#\t|  ___|__  _ __ / ___(_) |_ _   _ ")
WriteFile(FichierTXT,"#\t| |_ / _ \| '__| |   | | __| | | |")
WriteFile(FichierTXT,"#\t|  _| (_) | |  | |___| | |_| |_| |")
WriteFile(FichierTXT,"#\t|_|  \___/|_|   \____|_|\__|\__, |")
WriteFile(FichierTXT,"#\t                            |___/ ")
WriteFile(FichierTXT,"#")
WriteFile(FichierTXT,"#\tMETADONNEE SIMPLIFIEE")
WriteFile(FichierTXT,"#\tCOUCHE RASTER")
date2 = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
WriteFile(FichierTXT,"#\tFiche générée le {0}".format(date2))
WriteFile(FichierTXT,"#")
WriteFile(FichierTXT,"############################################")
WriteFile(FichierTXT,"")


# recuperation du nom de la couche
WriteFile(FichierTXT,"+ NOM :")
WriteFile(FichierTXT,"\t{0}".format(baseName))  # extension
WriteFile(FichierTXT,"")
# recuperation du type de fichier raster
WriteFile(FichierTXT,"+ FORMAT :")
WriteFile(FichierTXT,"\t{0} / {1}".format(layer.GetDriver().ShortName,layer.GetDriver().LongName))
WriteFile(FichierTXT,"")

# Commentaire court
# commentaire = '... à compléter...'
WriteFile(FichierTXT,"+ COMMENTAIRE :")
WriteFile(FichierTXT,"")

# Creation
WriteFile(FichierTXT,"+ DATE CREATION DE LA DONNEE :")
# DateDonneeMAJ = '... à compléter...'
WriteFile(FichierTXT,"+ DATE(s) MODIFICATION DE LA DONNEE :")
WriteFile(FichierTXT,"")

# projection et etendue geographique
spatialref=layer.GetProjection()
projwt=osr.SpatialReference(wkt=spatialref) #regarder wtk en detail conversion au format wtk ?
if projwt.IsProjected:
	proj=projwt.GetAttrValue('projcs')
	WriteFile(FichierTXT,"+ PROJECTION :")
	WriteFile(FichierTXT,"\t{0}".format(proj))
	WriteFile(FichierTXT,"")
geotransform = layer.GetGeoTransform()
if not geotransform is None:
	WriteFile(FichierTXT,"+ POINT D'ORIGINE :")
	WriteFile(FichierTXT,"\t{0}, {1}".format(geotransform[0],geotransform[3]))
	WriteFile(FichierTXT,"+ RESOLUTION :")
	WriteFile(FichierTXT,"\t{0}, {1}".format(geotransform[1],geotransform[5]))
WriteFile(FichierTXT,"+ TAILLE :")
WriteFile(FichierTXT,"\t{0} x {1} x {2}".format(layer.RasterXSize,layer.RasterYSize,layer.RasterCount))
WriteFile(FichierTXT,"")

# les bandes
WriteFile(FichierTXT,"+ FORMAT DE VALEURS :")

for i in range(layer.RasterCount):
	i+=1
	try:
		bande = layer.GetRasterBand(i)
	except RuntimeError, e:
		WriteFile(FichierTXT,"\tAucune bande trouvée")
		WriteFile(FichierTXT,"")
		os.popen("{0}".format(FichierTXT))
		sys.exit(1) 
	
	WriteFile(FichierTXT,"\t+BANDE N°{0}".format(i))
	WriteFile(FichierTXT,"\t\t{0}".format(gdal.GetDataTypeName(bande.DataType)))
	min = bande.GetMinimum()
	max = bande.GetMaximum()
	nodata = bande.GetNoDataValue()
	scale = bande.GetScale()
	Unit = bande.GetUnitType()
	if min is None or max is None:
		(min,max) = bande.ComputeRasterMinMax(1) #voir signification
	WriteFile(FichierTXT,"\t\tVALEUR MIN= {0} / VALEUR MAX= {1}".format(min,max))
	WriteFile(FichierTXT,"\t\tNO DATA= {0}".format(nodata))
	WriteFile(FichierTXT,"\t\tECHELLE= {0} / UNITE= {1}".format(scale,Unit))
	
	# stats = srcband.GetStatistics( True, True )
	# if stats is None:
		# continue

	# print "[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % ( \
		# stats[0], stats[1], stats[2], stats[3] )
	
	# pyramides
	#revoir exactement ce que c'est
	if bande.GetOverviewCount() > 0:
		WriteFile(FichierTXT,"\t\t{0} overviews".format(bande.GetOverviewCount()))
	else:
		WriteFile(FichierTXT,"\t\tAucune overviews")
	
	# Table de couleurs VOIR autre...
	colortable = bande.GetColorTable()
	if not colortable is None:
		WriteFile(FichierTXT,"\t\tTable de couleurs :")
		ct = colortable.GetColorEntry(i)
		WriteFile(FichierTXT,"\t'{0}'".format(colortable.GetColorEntryAsRGB( i, ct)))
	else:
		WriteFile(FichierTXT,"\t\tAucune table des couleurs")
	WriteFile(FichierTXT,"")

os.popen("{0}".format(FichierTXT))