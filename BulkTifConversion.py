import os
from PIL import Image, ImageSequence


def folder_wise_convert(path,
                        new_path):  # path folder has the TIFs and new_path folder has the converted files in jpegs according to folders.
    os.chdir(path)
    list_of_files_in_folder = [".".join(f.split(".")[:-1]) for f in os.listdir(path) if os.path.isfile(f)]
    for item in list_of_files_in_folder:
        os.chdir(new_path)
        os.mkdir(item)
        new = new_path + str(item)
        os.chdir(path)
        im = Image.open(item + ".tif")
        os.chdir(new)
        for i, page in enumerate(ImageSequence.Iterator(im)):
            print("converting page " + str(i) + " to JPEG")
            page.save(f"{item}%d.jpg" % i)


if __name__ == '__main__':
    folder_wise_convert("C:\\t2\\", "C:\\conv\\")