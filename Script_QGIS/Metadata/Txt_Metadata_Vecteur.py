#!/usr/bin/env Python
# -*- coding: utf8 -*-

import sys
import os
import time #ok
from PyQt4.QtCore import * #ok
from PyQt4.QtGui import * 
import ogr
import qgis


def CreateFile(self):
	"""creer un fichier"""
	create = open(self, "w")
	create.close()

def WriteFile(self,texte):
	"""ecrire dans un fichier"""
	writing = open(self, 'a')
	writing.write(texte+'\n')
	writing.close()

#selection de la couche en cours
LayerUSED = qgis.utils.iface.activeLayer().dataProvider().dataSourceUri()
path=LayerUSED.split('|')[0]
fileInfo = QFileInfo(path)
baseName = fileInfo.baseName()

# creation du fichier texte
date1 = time.strftime("%d_%m_%Y", time.localtime()) #_%H_%M_%S
FichierTXT=path+'_'+date1+'.txt'
CreateFile(FichierTXT)

# driver = ogr.GetDriverByName("ESRI Shapefile")

driverlist=["MapInfo File","ESRI Shapefile"]
for i in driverlist:
	driver = ogr.GetDriverByName(i)
	if isinstance(driver.Open(path),type(None)) is False:
		datasource = driver.Open(path)
		layer = datasource.GetLayer()
		formatfile = i

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
		WriteFile(FichierTXT,"#\tCOUCHE VECTEUR")
		date2 = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
		WriteFile(FichierTXT,"#\tFiche générée le {0}".format(date2))
		WriteFile(FichierTXT,"#")
		WriteFile(FichierTXT,"############################################")
		WriteFile(FichierTXT,"")

		# recuperation du nom de la couche
		WriteFile(FichierTXT,"+ NOM DE LA COUCHE:")
		WriteFile(FichierTXT,"\t{0}".format(layer.GetName()))
		WriteFile(FichierTXT,"")
		
		# recuperation du type de fichier raster
		WriteFile(FichierTXT,"+ FORMAT DE FICHIER :")
		WriteFile(FichierTXT,"\t{0}".format(formatfile))
		WriteFile(FichierTXT,"")
		
		# Commentaire court
		WriteFile(FichierTXT,"+ COMMENTAIRE :")
		WriteFile(FichierTXT,"")

		# Creation
		WriteFile(FichierTXT,"+ DATE CREATION DE LA DONNEE :")
		WriteFile(FichierTXT,"+ DATE(s) MODIFICATION DE LA DONNEE :")
		WriteFile(FichierTXT,"")

		# projection et etendue geographique

		spatialref=layer.GetSpatialRef()
		proj=spatialref.GetAttrValue('projcs')
		WriteFile(FichierTXT,"+ PROJECTION :")
		WriteFile(FichierTXT,"\t{0}".format(proj))
		extent=layer.GetExtent()
		WriteFile(FichierTXT,"+ EXTENSION GEOGRAPHIQUE :")
		WriteFile(FichierTXT,"\t-Xmin (ouest) : {0}".format(extent[0]))
		WriteFile(FichierTXT,"\t-Ymin (sud): {0}".format(extent[1]))
		WriteFile(FichierTXT,"\t-Xmax (est): {0}".format(extent[2]))
		WriteFile(FichierTXT,"\t-Ymax (nord): {0}".format(extent[3]))
		WriteFile(FichierTXT,"")

		# Nombre d'objet geometrique
		nbobjet=layer.GetFeatureCount()
		VerifGeom=layer.GetGeomType() # pas operationnel
		if VerifGeom == '4':
			geomt = 'point(s)'
		elif VerifGeom == '2':
			geomt = 'ligne(s)'
		elif VerifGeom == '3' or VerifGeom == '4':
			geomt = 'polygone(s)'
		# else:
			# geomt = 'entite(s) indeterminee(s)'
		WriteFile(FichierTXT,"+ TYPE ET NOMBRE D'OBJETS GEOMETRIQUE :")
		WriteFile(FichierTXT,"\t{0} {1}".format(nbobjet,'entitée(s)'))
		# Champs
		champs=layer.GetLayerDefn()
		WriteFile(FichierTXT,"")
		WriteFile(FichierTXT,"+ Données attributaires :")
		WriteFile(FichierTXT,"\t{0} champs présents".format(champs.GetFieldCount()))
		WriteFile(FichierTXT,"\t --------")
		WriteFile(FichierTXT,"")
		# WriteFile(FichierTXT,"\t Nom\t Type\t Longueur\t Precision\t Description")

		WriteFile(FichierTXT,"NUM_CHAMPS\tNOM_CHAMPS_SHP\tTYPE\tLONGUEUR\tPRECISION\tVALEURS_UNIQUES\tUNITE\tDESCRIPTION")
		for i in range(champs.GetFieldCount()):
			NomChamps =  champs.GetFieldDefn(i).GetName()
			
			CodeTypeChamps = champs.GetFieldDefn(i).GetType()
			
			TypeChamps = champs.GetFieldDefn(i).GetFieldTypeName(CodeTypeChamps)
			
			LongChamps = champs.GetFieldDefn(i).GetWidth()
			
			Precision = champs.GetFieldDefn(i).GetPrecision()
			
			if TypeChamps=='String':
				layer = iface.activeLayer()
				valuesatt = set()
				for feature in layer.getFeatures():
					valuesatt.add(feature[NomChamps])
				# conversion du set en liste
				valuesatt=list(valuesatt)
				listatt=[]
				for f in valuesatt:
					if f:
						listatt.append(f.encode('ascii','replace'))
						#listatt.append(unicodedata.normalize('NFKD', f).encode('utf-8', 'ignore'))
				if len(listatt) > 20:
					listatt = 'Valeurs uniques trop nombreuses'
				elif len(listatt) == 0:
					listatt = '[ / ]'
			else:
				listatt = 'Pas de valeurs qualitatives'

			WriteFile(FichierTXT,"{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t\t...COMPLETER...".format(str(i+1),NomChamps,TypeChamps,str(LongChamps),str(Precision),str(listatt)))
os.popen("{0}".format(FichierTXT))

