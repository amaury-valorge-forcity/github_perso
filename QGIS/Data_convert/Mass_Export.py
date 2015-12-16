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

""" Infos
mode = 'full' => export shp + qml + sld
mode = 'sld' => export sld only
epsg = None => no reprojection
epsg = 2154 => reprojection to 2154
"""

""" Variables a modifier """
mode = 'full'
#mode = 'sld'
epsg = None


""" creation du repertoire de sortie """
repertoire0 = '%s/%s/%s%s' % (os.path.expanduser('~'),'temp','export_',time.strftime("%d%m%y_%H%M%S"))
date=time.strftime("%d%m%y")
# on essaie de creer le repertoire temporaire temp
try:
	os.makedirs('%s/temp/' %os.path.expanduser('~'))
#s'il existe on passe
except OSError:
	pass
#dans tout les cas on genere le repertoire qui va accueillir les donnees exportees
os.makedirs(repertoire0)

""" recuperation les couches ouvertes dans la session et boucle"""
count=0
#pour chaque couche ouverte dans qgis (defini par QgsMapLayerRegistry.instance().mapLayers().values() )
for layer in QgsMapLayerRegistry.instance().mapLayers().values():
	""" recuperation du nom du fichier """
	# recuperation du repertoire
	pathlayer=layer.dataProvider().dataSourceUri()
	#dans 2 variables = recup du repertoire puis du nom du fichier
	(myDirectory,nameFile) = os.path.split(pathlayer)

	""" divers essais pour detecter le format de la donnees
	la detection est faite a l'arrache...
	"""
	try:
		# cette variable permet d'eviter les bug... c'est degueu
		typeformat = None 
		""" test si la couche est au format pg"""
		# dans le cas d'une couche pg, on a un nom de fichier degueu ! mais on note que dans celui-ci on retrouve tjrs le string (geom) ce qui nous permet de dire que c'est une couche pg
		if "(geom)" in nameFile:
			# on cree un dictionnaire afin de pouvoir recuperer le nom du fichier plus tard
			# lancer la boucle integree dans le dico pour comprendre
			nameFileDict=dict(x.split('=') for x in nameFile[:-12].split(' '))
			print nameFileDict
		else:
			""" sinon nous avons une table (sans geom) au format postgres"""
			typeformat = 'tab'
			nameFileDict=dict(x.split('=') for x in nameFile[:-5].split(' '))
		#on recup le nom du fichier a l'aide du dico ainsi que le schema
		name=nameFileDict['table'].split('.')[1]
		schem=nameFileDict['table'].split('.')[0]
		"""conversion en caracteres ascii """
		name=unicodedata.normalize('NFKD', name[1:-1]).encode('ASCII', 'ignore')
		schem=unicodedata.normalize('NFKD', schem[1:-1]).encode('ASCII', 'ignore')
	# si ca ne fonctionne pas on a une ValueError... du coup...
	except ValueError:
		# None car nous n'avons pas de schema, cad ce n'est pas du postgis
		schem = None
		# on fais d'autres essais
		try:
			""" test si la couche est au format wfs"""
			typeformat = None 
			nameFileDict=dict(x.split('=') for x in nameFile.split('&'))
			#une couche au format WFS a un TYPENAME !
			name=nameFileDict['TYPENAME'].split(':')[1]
			name=unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore')
		# si pas wfs alors on a une erreur KeyError
		except KeyError:
			""" test si la couche est au format fichier"""
			# on verifie si c'est du dbf ou csv
			if ".dbf" in nameFile or ".csv" in nameFile:
				typeformat = "tab"
			# on cree une liste afin de pouvoir recuperer le nom du fichier
			nameext=nameFile.split('|')
			""" conversion en caracteres ascii """
			name=unicodedata.normalize('NFKD', nameext[0].split('.')[0]).encode('ASCII', 'ignore')

	""" suppression des caracteres de ponctuation et espace """
	name=name.replace(" ","_")
	list_pct = [",",".","-","?","'","[","]","(",")","{","}","@","=","+","#","~","}","*","!",":",";","/","\\"]
	name=''.join([i if i not in list_pct else '' for i in name ])
	name=name.lower()
	""" si data = pg alors creation d'une repertoire au nom du schema"""
	if schem is not None:
		# correction du nom du schema
		schem=schem.replace(" ","_")
		list_pct = [",",".","-","?","'","[","]","(",")","{","}","@","=","+","#","~","}","*","!",":",";","/","\\"]
		schem=''.join([i if i not in list_pct else '' for i in schem ])
		schem=schem.lower()
		# creation du sous repertoire avec le nom du schema dans le repertoire cree plus haut
		repertoire1 = '%s/%s' % (repertoire0, schem)
		#on fait un try au cas ou le repertoire existerait deja meme si c'est improbable
		try:
			os.makedirs(repertoire1)
		except OSError:
			# pass permet d'arreter l'essai et d'enchainer sur la suite
			pass
	else:
		# RAS permet ici d'harmoniser les variables, on pourrait ameliorer ici
		repertoire1 = repertoire0

	if mode == 'full':
		# on regarde le format dectecte
		if typeformat is None:
			# si aucun epsg defini alors...
			if epsg is not None:
				""" recuperation de la projection defini par l'user """
				exp_crs = QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId)
				output='%s/%s_%s' % (repertoire1, name, date, str(epsg))
			else:
				# sinon recuperation de lespg = exp_crs
				exp_crs=layer.crs()
				output='%s/%s_%s_%s' % (repertoire1, name, date, str(layer.crs().authid().split(':')[1]))
		
		elif typeformat == 'tab':
			#si on a u tab alors...
			output='%s/%s_%s' % (repertoire1, name, date)

		#si le format est null alors
		if typeformat is None:
			#export en shp avec l'encodage en utf8
			QgsVectorFileWriter.writeAsVectorFormat(layer, output, "utf-8", exp_crs, "ESRI Shapefile")
			
			""" creation dun index spatial qix """
			vct = QgsVectorLayer(output, "tmp", "ogr" )
			provider = vct.dataProvider()
			provider.createSpatialIndex()

			""" export du qml """
			layer.saveNamedStyle('%s.qml' % (output))

		else:
			# sinon export au format csv
			QgsVectorFileWriter.writeAsVectorFormat(layer, output, 'utf-8', None, 'CSV')

	#en fonction du mode precise et le type de format, on va exporter le sld
	if (mode == 'full' or mode == 'sld') and typeformat is None:
		""" export du sld """
		layer.saveSldStyle('%s/%s.sld' % (repertoire1,name))

	#permet de suivre levolution du process pendant le traitement
	count+=1
	print name + ' : OK !!!'

print  '%s fichier(s) traite(s) dans %s' % (str(count), repertoire0)


# ouverture du repertoire selon le systeme utilise
if sys.platform == 'win32':
	repertoire0=repertoire0.replace('/','\\')
	subprocess.Popen('explorer "%s"' %repertoire0)
else:
	# TODO tester sur linux a propos des slash
	subprocess.Popen(['xdg-open', repertoire0])
