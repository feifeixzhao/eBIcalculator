from rivgraph.classes import river
from rivgraph import im_utils as iu
import matplotlib.pyplot as plt
from rivgraph.classes import rivnetwork
from rivgraph import mask_to_graph as m2g
from rivgraph.rivers import river_utils as ru
from rivgraph import geo_utils as gu
import os
from datetime import datetime
import csv
import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry import LineString, Polygon
from rivgraph import ln_utils as lnu
from rivgraph import io_utils as io
import networkx as nx
from scipy.ndimage import distance_transform_edt



# Define the path to the georeferenced binary image.
mask_path = r'C:\Users\Feifei\GEE_watermasks-master\ebi\Brahmaputra_Pandu\rivgraph\Brahm_cropped.tif'
# Results will be saved with this name
name = 'Brahm' 

# Where to store RivGraph-generated geotiff and geovector files.
results_folder = r'C:\Users\Feifei\GEE_watermasks-master\ebi\Brahmaputra_Pandu\rivgraph'

# Set the exit sides of the river relative to the image. 
es = 'WE' # The first character is the upstream side

# Boot up the river class! We set verbose=True to see progress of processing.
Brahm= river(name, mask_path, results_folder, exit_sides=es, verbose=True) 


# plot
plt.imshow(Brahm.Imask)
Brahm.Imask= iu.largest_blobs(Brahm.Imask, nlargest=1, action='keep')
Imask_blob, pads = m2g.cap_river_im(Brahm.Imask, es, capsize=5)

# Fill small holes in the mask. 
Brahm.Imask=iu.fill_holes(Brahm.Imask, maxholesize=5)

#compute mesh - done once per river
Brahm.compute_mesh(buf_halfwidth=5000, smoothing=0.5, grid_spacing=1000)
Brahm.to_geovectors('centerline', ftype='json')
Brahm.to_geovectors('mesh', ftype='json')

# compute links and nodes 
#Naryn.compute_network()
#Naryn.prune_network()
#Naryn.compute_link_width_and_length()
#Naryn.to_geovectors('network', ftype='json')



