## entropic Braiding Index (eBI) calculator
#### This code prepares and processes river channel masks, draws perpendicular transects across the river reach, and calculates eBI for each river channel mask. Rivgraph requires that all river channel masks must be (1) a rectangle polygon and (2) have clear exit sides (i.e., not exiting into a corner). To calculate eBI, first run the preprocess_images function which deletes blank masks, crops each mask to reduce edge effects in rivgraph and (optionally) scales the mask to render correctly in windows file explorer, allowing the user to quickly identify low quality channel masks. river_name is the folder name containing all of the channel masks.

```markdown
preprocess_images.py river_name --crop --scale
```

#### Next run mesh_maker.ipynb which generates the transects that eBI will be calculated for each mask. This step is very difficult to automate, so I use a jupyter notebook to adjust the parameters by loading links, nodes, and mesh into qgis. Mesh file generated from rivgraph file must be saved in a "rivgraph" folder.

#### Finally, the function rivgraph_eBI.py calculates the eBI statistics for all masks in the folder. The outputs include two .csv files - one with eBI statistics and one with the eBI value for each transect in each mask. To run, river_name is folder name containing all of the channel masks, and exit_sides are the cardinal directions of where the river exits (e.g., east/west, or EW)

```markdown
rivgraph_eBI.py --river_name river_name --exit_sides EW --timescale subannual

```

