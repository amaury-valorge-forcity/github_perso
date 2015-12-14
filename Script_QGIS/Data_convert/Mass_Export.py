#!/usr/bin/env Python
# -*- coding: utf-8 -*-

import sys
import os
import time
import unicodedata
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import qgis
import unicodedata
import subprocess

''' definition des variables '''
mode = 'full'
# mode 'sld' 
# mode "full' = export shp + qml + sld
epsg = None
# None = pas de reprojection ; 3946 reprojection en 3946


''' creation du repertoire de sortie '''
repertoire0 = '%s/%s/%s%s' % (os.path.expanduser('~'),'temp','export_',time.strftime("%d%m%y_%H%M%S"))
date=time.strftime("%d%m%y")
try:
	os.makedirs('%s/temp/' %os.path.expanduser('~'))
except OSError:
	pass
os.makedirs(repertoire0)

''' recuperation les couches ouvertes dans la session et boucle'''
count=0
for layer in QgsMapLayerRegistry.instance().mapLayers().values():
	''' recuperation du nom du fichier '''
	pathlayer=layer.dataProvider().dataSourceUri()
	(myDirectory,nameFile) = os.path.split(pathlayer)

	try:
		typeformat = None 
		''' test si la couche est au format pg'''
		if "(geom)" in nameFile:
			nameFileDict=dict(x.split('=') for x in nameFile[:-12].split(' '))
			print nameFileDict
		else:
			typeformat = 'tab'
			nameFileDict=dict(x.split('=') for x in nameFile[:-5].split(' '))
		name=nameFileDict['table'].split('.')[1]
		schem=nameFileDict['table'].split('.')[0]
		'''conversion en caracteres ascii '''
		name=unicodedata.normalize('NFKD', name[1:-1]).encode('ASCII', 'ignore')
		schem=unicodedata.normalize('NFKD', schem[1:-1]).encode('ASCII', 'ignore')
	except ValueError:
		schem = None
		try:
			''' test si la couche est au format wfs'''
			typeformat = None 
			nameFileDict=dict(x.split('=') for x in nameFile.split('&'))
			name=nameFileDict['TYPENAME'].split(':')[1]
			name=unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore')
		except KeyError:
			''' test si la couche est au format fichier'''
			if ".dbf" in nameFile or ".csv" in nameFile:
				typeformat = "tab"
			nameext=nameFile.split('|')
			''' conversion en caracteres ascii '''
			name=unicodedata.normalize('NFKD', nameext[0].split('.')[0]).encode('ASCII', 'ignore')

	''' suppression des caracteres de ponctuation et espace '''
	name=name.replace(" ","_")
	list_pct = [",",".","-","?","'","[","]","(",")","{","}","@","=","+","#","~","}","*","!",":",";","/","\\"]
	name=''.join([i if i not in list_pct else '' for i in name ])
	name=name.lower()
	''' si data pg alors creation d'une repertoire au nom du schema'''
	if schem is not None:
		schem=schem.replace(" ","_")
		list_pct = [",",".","-","?","'","[","]","(",")","{","}","@","=","+","#","~","}","*","!",":",";","/","\\"]
		schem=''.join([i if i not in list_pct else '' for i in schem ])
		schem=schem.lower()
		repertoire1 = '%s/%s' % (repertoire0, schem)
		try:
			os.makedirs(repertoire1)
		except OSError:
			pass
	else:
		repertoire1 = repertoire0

	if mode == 'full':
		if typeformat is None:
			if epsg is not None:
				''' recuperation de la projection defini par l'user '''
				exp_crs = QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId)
				output='%s/%s_%s' % (repertoire1, name, date, str(epsg))
			else:
				exp_crs=layer.crs()
				output='%s/%s_%s_%s' % (repertoire1, name, date, str(layer.crs().authid().split(':')[1]))
		elif typeformat == 'tab':
			output='%s/%s_%s' % (repertoire1, name, date)

		if typeformat is None:
			QgsVectorFileWriter.writeAsVectorFormat(layer, output, "utf-8", exp_crs, "ESRI Shapefile")
			''' creation dun index spatial qix '''
			vct = QgsVectorLayer(output, "tmp", "ogr" )
			provider = vct.dataProvider()
			encoding=provider.encoding()
			#vct.setProviderEncoding(u'UTF-8')
			#vct.dataProvider().setEncoding(u'UTF-8')
			provider.createSpatialIndex()
			''' export du qml '''
			layer.saveNamedStyle('%s.qml' % (output))
		else:
			QgsVectorFileWriter.writeAsVectorFormat(layer, output, 'utf-8', None, 'CSV')

	if (mode == 'full' or mode == 'sld') and typeformat is None:
		''' export du sld '''
		layer.saveSldStyle('%s/%s.sld' % (repertoire1,name))

	count+=1
	print name + ' : OK !!!'

print  '%s fichier(s) traite(s) dans %s' % (str(count), repertoire0)

if sys.platform == 'win32':
	repertoire0=repertoire0.replace('/','\\')
	subprocess.Popen('explorer "%s"' %repertoire0)
else: # tester sur linux a propos des slash
	subprocess.Popen(['xdg-open', repertoire0])
