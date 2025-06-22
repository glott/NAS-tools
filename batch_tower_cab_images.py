import os

url = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'		# ArcGIS
# url = 'https://ecn.t3.tiles.virtualearth.net/tiles/a{q}.jpeg?g=1'											# Bing Aerial
# url = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'													# Google Satellite
# url = 'https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}'													# Google Maps
# url = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'													# Google Satellite Hybrid
# url = 'https://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}'													# Google Terrain
# url = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'								# Mapzen Global Terrain
# url = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'														# OpenStreetMap
# url = 'https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/tile/{z}/{y}/{x}'	# USGS NAIP

airports = ['MIA', 'TPA', 'RSW', 'PBI', 'NQX', 'APF', 'BCT', 'BKV', 'BOW', 'EYW', 'FLL', 'FMY', 'FPR', 'FXE', 'HST', 'HWO', 'LAL', 'MCF', 'OPF', 'PGD', 'PIE', 'PMP', 'SPG', 'SRQ', 'SUA', 'TMB', 'VRB', '06FA']

for airport in airports:
	os.system(os.path.join(os.getcwd(), 'TowerCabImageGenerator.exe') + ' ' + airport + ' ' + url)