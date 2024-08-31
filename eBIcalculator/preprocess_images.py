import os
import argparse
from PIL import Image
import numpy as np
import rasterio
from rasterio.windows import Window

# Function to delete blank images
def delete_blank_images(folder_path):
    deleted_files = 0
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.tif'):
            file_path = os.path.join(folder_path, file_name)
            image = Image.open(file_path)
            if np.all(np.array(image) == 0):
                os.remove(file_path)
                deleted_files += 1
    return deleted_files

# Function to crop images to reference
def crop_image_to_reference(image_path, reference_path):
    with rasterio.open(reference_path) as ref_src:
        ref_bounds = ref_src.bounds

    with rasterio.open(image_path) as src:
        window = src.window(*ref_bounds)
        transform = src.window_transform(window)
        data = src.read(window=window)
        meta = src.meta.copy()
        meta.update({
            "driver": "GTiff",
            "height": window.height,
            "width": window.width,
            "transform": transform
        })

    return data, meta

# Function to scale images for better viewing experience in windows
def scale_images(cropped_folder, output_folder):
    mask_files = [os.path.join(cropped_folder, f) for f in os.listdir(cropped_folder) if f.endswith('.tif')]

    # Create output folder for PreparedImagery
    os.makedirs(output_folder, exist_ok=True)

    # Process each mask image
    for mask_file in mask_files:
        mask_image = Image.open(mask_file)
        mask_array = np.array(mask_image)

        # Convert to uint8 scaled to intensity of 255
        mask_array = np.round(mask_array).astype(np.uint8) * 255

        mask_image = Image.fromarray(mask_array)

        # Save image to output folder
        file_name = os.path.splitext(os.path.basename(mask_file))[0] + '_thresh.tif'
        output_file = os.path.join(output_folder, file_name)
        mask_image.save(output_file)

    print(f"All images scaled and saved to {output_folder}.")

# Function to first crop images and then scale them
def process_river_folder(base_dir, river_name, crop_images=False, scale_images_flag=False):
    river_path = os.path.join(base_dir, river_name)

    # Dynamically find the cropped reference image based on the river station name
    cropped_reference_image = None
    for file_name in os.listdir(river_path):
        if file_name.endswith('_cropped.tif'):
            cropped_reference_image = os.path.join(river_path, file_name)
            break

    if not cropped_reference_image:
        return

    # Process both output_annual and output_subannual folders
    output_folders = [
        os.path.join(river_path, "output_annual", river_name),
        os.path.join(river_path, "output_subannual", river_name)
    ]

    for output_folder in output_folders:
        if crop_images:
            # Define mask folders
            mask_folders = [
                os.path.join(output_folder, "mask")
            ]

            for mask_folder in mask_folders:
                if os.path.exists(mask_folder):
                    # Delete blank images before cropping
                    delete_blank_images(mask_folder)

                    # Define save folder for cropped masks
                    save_folder = os.path.join(output_folder, "mask_cropped")
                    os.makedirs(save_folder, exist_ok=True)

                    # Crop each mask image
                    for mask_file in os.listdir(mask_folder):
                        if mask_file.endswith('.tif'):
                            mask_path = os.path.join(mask_folder, mask_file)
                            cropped_data, cropped_meta = crop_image_to_reference(mask_path, cropped_reference_image)
                            cropped_mask_path = os.path.join(save_folder, mask_file)
                            
                            with rasterio.open(cropped_mask_path, 'w', **cropped_meta) as dest:
                                dest.write(cropped_data)
                    
                    print(f"All images cropped and saved to {save_folder}.")

        if scale_images_flag:
            cropped_folder = os.path.join(output_folder, "mask_cropped")
            if os.path.exists(cropped_folder):
                prepared_imagery_folder = os.path.join(output_folder, "PreparedImagery_annual") if "output_annual" in output_folder else os.path.join(output_folder, "PreparedImagery_subannual")
                scale_images(cropped_folder, prepared_imagery_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocess DSWE images for a given river site.')
    parser.add_argument('river_name', type=str, help='Name of the river to preprocess images for')
    parser.add_argument('--crop', action='store_true', help='Crop images before processing')
    parser.add_argument('--scale', action='store_true', help='Scale images for better viewing experience in windows')
    args = parser.parse_args()

    base_dir = r"C:\Users\Feifei\Box\BR_remote_sensing\ebi_results"
    
    process_river_folder(base_dir, args.river_name, crop_images=args.crop, scale_images_flag=args.scale)



# python preprocess_images.py AmuDarya_Kerki --crop --scale
