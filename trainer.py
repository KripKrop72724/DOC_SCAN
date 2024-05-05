import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, EarlyStopping
import matplotlib.pyplot as plt

dimention = 299
trdata = ImageDataGenerator()
traindata = trdata.flow_from_directory(directory="C:\\Users\\Shifa\\Desktop\\DATASET\\train", target_size=(dimention, dimention), class_mode="categorical")
tsdata = ImageDataGenerator()
testdata = tsdata.flow_from_directory(directory="C:\\Users\\Shifa\\Desktop\\DATASET\\test", target_size=(dimention, dimention), class_mode="categorical")

model = tf.keras.applications.InceptionV3(
    include_top=True,
    weights=None,
    input_tensor=None,
    input_shape=False,
    pooling=None,
    classes=8,
)

model.summary()
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy'],
)

checkpoint = ModelCheckpoint("InceptionV3.h5", monitor='val_accuracy', verbose=1, save_best_only=True,
                             save_weights_only=False,
                             mode='auto', period=1)
early = EarlyStopping(monitor='val_accuracy', min_delta=0, patience=20, verbose=1, mode='auto')
history = model.fit(traindata, steps_per_epoch=34, validation_data=testdata, validation_steps=34, epochs=100,
                    callbacks=[checkpoint, early])
print(history.history.keys())

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('InceptionV3 model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('InceptionV3 model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()