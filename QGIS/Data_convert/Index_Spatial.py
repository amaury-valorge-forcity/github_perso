#!/usr/bin/env Python
# -*- coding: cp1252 -*-

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

''' recuperation les couches (valeurs qgis) ouvertes dans la session et boucle'''
count=0
for layer in QgsMapLayerRegistry.instance().mapLayers().values():
	''' recuperation du nom du fichier '''
	pathlayer=layer.dataProvider().dataSourceUri()
	pathlayer=pathlayer.split('|')
	output=pathlayer[0]
	''' creation dun index spatial qix '''
	vct = QgsVectorLayer(output, "tmp", "ogr" )
	provider = vct.dataProvider()
	provider.createSpatialIndex()
	count+=1

print str(count) + ' shapeFile(s) ont ete traites'