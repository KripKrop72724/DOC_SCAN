from PIL import Image
import glob


def resize_without_loosing_quality():
    for file in list(glob.glob('C:\\DocScan\\*.jpg')):
        print("compressing file...")
        foo = Image.open(file)
        foo = foo.resize(foo.size, Image.ANTIALIAS)
        foo.save(file, optimize=True, quality=30)


def resize_on_the_go(path):
    foo = Image.open(path)
    foo = foo.resize((100, 127), Image.ANTIALIAS)
    foo.save(path, optimize=True, quality=85)
