from PIL import Image
import glob


def resize_without_loosing_quality():
    for file in list(glob.glob('C:\\DocScan\\*.jpg')):
        print("compressing file...")
        foo = Image.open(file)
        foo = foo.resize(foo.size, Image.ANTIALIAS)
        foo.save(file, optimize=True, quality=30)


def resize_on_the_go(path):
    print(f"\n---\nStarting processing for file: {path}")
    try:
        print("Opening the image file...")
        image = Image.open(path)
        original_size = image.size
        print(f"Original image size: {original_size}")

        # Define the new size for the image
        new_size = (100, 127)
        print(f"Resizing image to new dimensions: {new_size} using high-quality downsampling filter...")
        image = image.resize(new_size, Image.ANTIALIAS)
        print("Resizing completed.")

        # Save the image with specific compression settings
        print("Saving the image with optimization enabled and quality set to 85...")
        image.save(path, optimize=True, quality=85)
        print("Image saved successfully.")
    except Exception as e:
        print(f"Error processing file {path}: {e}")
