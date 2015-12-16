#/user/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from qgis.core import *
import subprocess # pour utiliser subprocess.call()
import time
from PyQt4.Qt import *


def CreateFile(self):
	"""creer un fichier"""
	# open(self, 'parametre') permet en fonction du parametre de creer un fichier
	create = open(self, "w")
	create.close()

def WriteFile(self,texte):
	"""ecrire dans un fichier"""
	# open(self, 'parametre') permet en fonction du parametre d'ecrire dans un fichier
	writing = open(self, 'a')
	#la variable texte permet d'indiquer la valeur a ecrire. de plus on ajoute un retour a la ligne
	writing.write(texte+'\n')
	writing.close()

"""##########################"""
""" variables a modifier """
""" Config Postgis """
url='localhost'
db='mug'
port = 5432
login='postgres'
mdp='amaury'
repertoire=r"D:\00_Corbeille\keolis"
shem='bati'

""" variables a modifier si utilise sur windows
Chemin d'acces a postgis et qgis """
pathpg = r"C:\Program Files\PostgreSQL\9.4\bin"
pathAppsQgis = r"C:\Program Files\QGIS Lyon\apps\qgis"

"""##########################"""

# indication du repertoire contenant l'installation de qgis
if sys.platform == 'win32':
	QgsApplication.setPrefixPath(pathAppsQgis, True)
elif sys.platform == 'linux2':
	app = QApplication(sys.argv)
	QgsApplication.setPrefixPath('/usr', True)

""" Initialisation de QGIS """
#RAS faut l'initialiser pour que le script soit autonome, mais o peux le virer sans probleme a priori
QgsApplication.initQgis()

""" creation du fichier texte """
# recup dans une variable du jour_mois_annee
date = time.strftime("%d_%m_%Y", time.localtime())
# on ecrit dans le repertoire ou se trouve les donnees source un fichier txt qui va resumer les caracteristiques des fichiers
FichierTxt='%s/resume_%s.txt' % (repertoire,date)
CreateFile(FichierTxt)

# on affecte aux variable d'environnement les valeurs suivantes
os.environ['PGHOST'] = url
os.environ['PGPORT'] = str(port)
os.environ['PGUSER'] = login
os.environ['PGPASSWORD'] = mdp
os.environ['PGDATABASE'] = db

#on recupere dans une variable le repertoire defini plus haut ! inutile en effet :p
base_dir = repertoire
# os.walk permet de, comme son nom l'indique de naviguer dans un repertoire donne en l'occurence dans celui defini plus haut
full_dir = os.walk(base_dir)
# creation d'une liste qui va contenir tout les chemins d'acces aux donnees
shapefile_list = []
# on decoupe en trois variables le resultat de l'os.walk dans une boucle
#file_ permet de recuperer le nom de chaque fichier
for source, dirs, files in full_dir:
	for file_ in files:
		# on cherche ici a recupere les fichiers avec l'extension shp. [-3:] permet de recup uniquement les trois derniers caracteres du nom de fichiers
		if file_[-3:] == 'shp':
			# on recree le chemin de la donnees complet (repertoire + fichier)
			shapefile_path = os.path.join(base_dir, file_)
			# ajout dans la liste precedemment creee
			shapefile_list.append(shapefile_path)

# das la liste nouvellement creee
for shape_path in shapefile_list:
	#dans le cas d'un systeme windows, on va lire l'encodage du shp avec pyqgis
	if sys.platform == 'win32':
		# on initialise le layer a partir de son chemin d'acces ; tmp correspon au nom de la couche (peux etre vide), ogr est le driver
		vct = QgsVectorLayer(shape_path, "tmp", "ogr" )
		# on appelle le provider pour appeler la valeur d'encoage ensuite
		provider = vct.dataProvider()
		encoding = provider.encoding()
	# dans le cas d'un systeme unix o va lire le fichier cpg contenat l'infos de l'encodage. pyqgis ne fonctionne pas super bien sur linux.. :(
	elif sys.platform == 'linux2':
		# on recup dans une variable le nom des fichiers cpg. nous avons deja les shp, il suffit donc de modifier lextension dans une variable
		cpgFile = r'%scpg' % shape_path[:-3]
		#try = litterallement on essaie ici d'ouvrir le fichier cpg (open()) et de lire ce qu'il y a dedans 
		try:
			with open(cpgFile) as f:
				# f.readlines permet de lire le fichier et de creer une liste = une entree pour chaque ligne
				encoding = f.readlines()
				#la premiere ligne nous interesse donc on indique la valeur 0
				encoding = encoding[0]
		# si pb on obtient une IOError, du coup on affecte a la varialbe encoing la valeur None
		except IOError:
			encoding = None

	# si l'encodage est bien de l'utf8 alors....
	if encoding == 'UTF-8' or encoding == 'utf-8':
		provider_name = "ogr"
		# recuperation des infos du fichier shp
		fileInfo = QFileInfo(shape_path)
		# iitialisation du fichier (appel a partir du repertoire + nom du fichier, provider(ogr))
		layer = QgsVectorLayer(shape_path, fileInfo.fileName(), provider_name)
		# layer.crs().authid() permet de recuperer les infos sur la projection
		# .split(":") permet de transformer la variable en liste afin de recuperer la valeur de l'epsg (1)
		exp_crs=str(layer.crs().authid().split(':')[1])
		#variable qui servira a dire que l'importation a tete valide dans le futur fichier txt
		imp='oui'

		if sys.platform == 'win32':
			#a partir du chemin d'acces a la donnees, on recupere le nom du fichier
			namefile=shape_path.split('\\')[len(shape_path.split('\\'))-1].split('.')[0]
			#on indique le nom du repertoire ou se trouve postgis
			os.environ['PATH'] = pathpg
			#on cree une variable avec la commane qui va bien pour utiliser shp2pgsql ; les valers de | psql ont deja ete preciser dans les variables d'envrionement
			cmds = 'shp2pgsql.exe -I -s %s: "%s" %s.%s | psql ' % (exp_crs, shape_path, shem, namefile)
			#permet de lancer la commande
			subprocess.call(cmds, shell=True)
		elif sys.platform == 'linux2':
			#meme principe
			namefile=shape_path.split('/')[len(shape_path.split('/'))-1].split('.')[0]
			cmds = 'shp2pgsql -I -s %s: "%s" %s.%s | psql ' % (exp_crs, shape_path, shem, namefile)
			subprocess.call(cmds, shell=True)
	# si l'encodage n'est pas de l'UTF8
	elif encoding is None or encoding != 'UTF-8':
		print 'Fichier %s n''est pas en UTF-8' %shape_path
		imp='NON- VERIFIER ENCODAGE (UTF-8 OBLIGATOIRE - .cpg probablement ABSENT)'
	#apres la fin de la boucle on ecrit le repertoire de la couche puis la valeur imp = oui ou non
	WriteFile(FichierTxt,"{0},{1}" .format(shape_path,imp))

#ouverture du txt selon le systeme d'exploitation
if sys.platform == 'win32':
	os.popen("%s" %FichierTxt)
elif sys.platform == 'linux2':
	os.system('gnome-open %s' %FichierTxt)