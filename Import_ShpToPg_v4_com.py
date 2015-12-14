#/user/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from qgis.core import *
#from qgis.gui import *
import subprocess
import time
# from PyQt4.QtSql import *

from PyQt4.Qt import *


def CreateFile(self):
	"""creer un fichier"""
	create = open(self, "w")
	create.close()

def WriteFile(self,texte):
	"""ecrire dans un fichier"""
	writing = open(self, 'a')
	writing.write(texte+'\n')
	writing.close()

######### variables a modifier
#app = QApplication(sys.argv)
# variables concernant la connection postgis
url='localhost'
db='mug'
port = 5432
login='postgres'
mdp='amaury'
repertoire=r"D:\00_Corbeille\keolis"
shem='bati'

# variables concernant le repertoire de pgadmin et qgis pour windows
pathpg = r"C:\Program Files\PostgreSQL\9.4\bin"
pathAppsQgis = r"C:\Program Files\QGIS Lyon\apps\qgis"


######### variables a modifier


if sys.platform == 'win32':
	QgsApplication.setPrefixPath(pathAppsQgis, True)
elif sys.platform == 'linux2':
	app = QApplication(sys.argv)
	QgsApplication.setPrefixPath('/usr', True)

# Initialisation de QGIS.
QgsApplication.initQgis()

# creation du fichier texte
date1 = time.strftime("%d_%m_%Y", time.localtime()) #_%H_%M_%S
FichierTxt='%s/resume_%s.txt' % (repertoire,date1)
CreateFile(FichierTxt)


os.environ['PGHOST'] = url
os.environ['PGPORT'] = str(port)
os.environ['PGUSER'] = login
os.environ['PGPASSWORD'] = mdp
os.environ['PGDATABASE'] = db


# uri = QgsDataSourceURI()
# uri.setConnection(url, str(port), db, login, mdp)

# db = QSqlDatabase.addDatabase("QPSQL");
# db.setDatabaseName(uri.database())
# db.setPort(int(uri.port()))
# db.setUserName(uri.username())
# db.setPassword(uri.password())
# if db.open() is True:
#     query = db.exec_("""select * from teststrati""")

#         query = db.exec_("""select * from users""")
#         while query.next(): 
#             record = query.record()
#             print record.value(0)





base_dir = repertoire
full_dir = os.walk(base_dir)
shapefile_list = []
for source, dirs, files in full_dir:
	for file_ in files:
		if file_[-3:] == 'shp':
			shapefile_path = os.path.join(base_dir, file_)
			shapefile_list.append(shapefile_path)

for shape_path in shapefile_list:
	if sys.platform == 'win32':
		vct = QgsVectorLayer(shape_path, "tmp", "ogr" )
		provider = vct.dataProvider()
		encoding = provider.encoding()
	elif sys.platform == 'linux2':
		cpgFile = r'%scpg' % shape_path[:-3]
		try:
			with open(cpgFile) as f:
				encoding = f.readlines()
				encoding = encoding[0]
		except IOError:
			encoding = None

	if encoding == 'UTF-8' or encoding == 'utf-8':
		provider_name = "ogr"
		fileInfo = QFileInfo(shape_path)
		layer = QgsVectorLayer(shape_path, fileInfo.fileName(), provider_name)
		exp_crs=str(layer.crs().authid().split(':')[1])
		imp='oui'

		if sys.platform == 'win32':
			namefile=shape_path.split('\\')[len(shape_path.split('\\'))-1].split('.')[0]
			#shape_path=shape_path.replace("\\","/")
			os.environ['PATH'] = pathpg
			cmds = 'shp2pgsql.exe -I -s %s: "%s" %s.%s | psql ' % (exp_crs, shape_path, shem, namefile)
			#cmd = subprocess.Popen(cmds, stdout=subprocess.PIPE)
			#cmd_out, cmd_err = cmd.communicate()
			subprocess.call(cmds, shell=True)
			#os.system(cmds)
			print cmds
		elif sys.platform == 'linux2':
			namefile=shape_path.split('/')[len(shape_path.split('/'))-1].split('.')[0]
			cmds = 'shp2pgsql -I -s %s: "%s" %s.%s | psql ' % (exp_crs, shape_path, shem, namefile)
			subprocess.call(cmds, shell=True)
			print cmds
	elif encoding is None or encoding != 'UTF-8':
		print 'Fichier %s n''est pas en UTF-8' %shape_path
		imp='NON- VERIFIER ENCODAGE (UTF-8 OBLIGATOIRE - .cpg probablement ABSENT)'
	WriteFile(FichierTxt,"{0},{1}" .format(shape_path,imp))

if sys.platform == 'win32':
	os.popen("%s" %FichierTxt)
elif sys.platform == 'linux2':
	os.system('gnome-open %s' %FichierTxt)