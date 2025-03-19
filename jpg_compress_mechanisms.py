from PIL import Image
import glob

# Determine the correct resampling filter based on Pillow version
try:
    resample_filter = Image.Resampling.LANCZOS
except AttributeError:
    resample_filter = Image.ANTIALIAS


def resize_without_losing_quality():
    file_list = glob.glob('C:\\DocScan\\*.jpg')
    print(f"Found {len(file_list)} file(s) in 'C:\\DocScan\\' to process.")

    for file in file_list:
        print(f"\n---\nStarting processing for file: {file}")
        try:
            print("Opening the image file...")
            image = Image.open(file)
            original_size = image.size
            print(f"Original image size: {original_size}")

            print("Resizing image to its original dimensions (no change in size) using the chosen resampling filter...")
            image = image.resize(original_size, resample_filter)
            print("Resizing completed.")

            print("Saving the image with optimization enabled and quality set to 30...")
            image.save(file, optimize=True, quality=30)
            print("Image saved successfully.")
        except Exception as e:
            print(f"Error processing file {file}: {e}")


def resize_on_the_go(path):
    print(f"\n---\nStarting processing for file: {path}")
    try:
        print("Opening the image file...")
        image = Image.open(path)
        original_size = image.size
        print(f"Original image size: {original_size}")

        new_size = (100, 127)
        print(f"Resizing image to new dimensions: {new_size} using the chosen resampling filter...")
        image = image.resize(new_size, resample_filter)
        print("Resizing completed.")

        print("Saving the image with optimization enabled and quality set to 85...")
        image.save(path, optimize=True, quality=85)
        print("Image saved successfully.")
    except Exception as e:
        print(f"Error processing file {path}: {e}")
