import os
import numpy as np
import rasterio
from PIL import Image

def process_water_masks(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Get a list of all mask files in the input folder
    mask_files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]
    
    # Load all masks into a list
    masks = []
    profiles = []
    for file in mask_files:
        file_path = os.path.join(input_folder, file)
        with rasterio.open(file_path) as src:
            masks.append(src.read(1))
            profiles.append(src.profile)
    
    # Convert the list of masks to a 3D numpy array (stack of 2D arrays)
    masks = np.array(masks)
    
    # Process each mask
    for i, file in enumerate(mask_files):
        # Get the current mask
        mask = masks[i]
        
        # Create a stack of masks excluding the current one
        other_masks = np.delete(masks, i, axis=0)
        
        # Find the pixels that are classified as water in at least one of the other masks
        any_water_elsewhere = np.any(other_masks == 1, axis=0)
        
        # Create a new mask where water pixels not classified as water in any other mask are set to 0
        new_mask = np.where(any_water_elsewhere, mask, 0)
        
        # Convert to uint8 scaled to intensity of 255
        new_mask = np.round(new_mask).astype(np.uint8) * 255
        
        # Convert numpy array back to image
        new_mask_image = Image.fromarray(new_mask)
        
        # Save the new mask to the output folder as an image
        output_file_path = os.path.join(output_folder, file.replace('.tif', '.png'))
        new_mask_image.save(output_file_path)

# Example usage
input_folder = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_results\Brahmaputra_Pandu\output\Brahmaputra_Pandu\mask"
output_folder = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_results\Brahmaputra_Pandu\output_clean"
process_water_masks(input_folder, output_folder)

