from keras_preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
import os
from multiprocessing import Pool as ProcessPool


def image_processor(image):
    datagen = ImageDataGenerator(
        rotation_range=10,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.1,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.2, 1.2],
        fill_mode='nearest')
    j = 0
    filename = "C:\\Users\\Shifa\\Desktop\\BIN\\train\\1\\" + image
    j = j + 1
    img = load_img(filename)  # this is a PIL image
    x = img_to_array(img)  # this is a Numpy array with shape (3, 150, 150)
    x = x.reshape((1,) + x.shape)
    i = 0
    print("Augmenting " + filename)
    for batch in datagen.flow(x, batch_size=1,
                              save_to_dir='C:\\Users\\Shifa\\Desktop\\BIN\\aug', save_prefix='KERAS_AUG',
                              save_format='JPG'):
        print("Gen: " + str(i))
        i += 1
        if i > 2:
            break


if __name__ == "__main__":
    desired_file_list = [file_name for file_name in os.listdir("C:\\Users\\Shifa\\Desktop\\BIN\\train\\1")]

    with ProcessPool(processes=5) as pool:
        results = pool.map(image_processor, desired_file_list)

    print(results)
