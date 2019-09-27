import numpy as np
import os, glob
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array, array_to_img
from keras.utils import to_categorical

img_ext = 'png'
img_size = (24,24)
circle = glob.glob('shapes/circle' + '/*' + img_ext)
rectangle = glob.glob('shapes/rectangle' + '/*' + img_ext)
triangle = glob.glob('shapes/triangle' + '/*' + img_ext)
img_names = circle + rectangle + triangle
img_names = [names.replace('\\', '/') for names in img_names]
np.random.shuffle(img_names)
train = img_names[:-12]
valid = img_names[-12:]
print("Found {} images.".format(len(img_names)))
print(" - train : {}".format(len(train)))
print(" - valid : {}".format(len(valid)))
labels = ['circle', 'rectangle', 'triangle']
batch_size = 1

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=(img_size[0],img_size[1],3)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(len(labels), activation='softmax'))
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

def crop_center(img):
    if type(img) == np.ndarray:
        #print('USE Numpy') 
        y, x, c = img.shape
        sx = x // 2-(min(x, y) // 2)
        sy = y // 2-(min(x, y) // 2)
        img = img[sy:sy+min(x,y), sx:sx+min(x,y)]
    else:
        #print('Use PIL')
        x, y = img.width, img.height
        sx = x // 2-(min(x, y) // 2)
        sy = x // 2-(min(x, y) // 2)
        img = img.crop((sx, sy, sx+min(x, y), sy+min(x, y)))
    return img
    
def resize_img(img, size):
    #size = (x, y)
    if type(img) == np.ndarray:
        img = array_to_img(img)
    return img.resize(size)

def train_generator():
    while True:
        for start in range(0, len(train), batch_size):
            x_batch = []
            y_batch = []
            end = min(start + batch_size, len(train))
            ids = train[start:end]
            for path in ids:
                img = load_img(path, color_mode='rgb', target_size=(24,24))
                img = img_to_array(img)
                label = path.split('/')[1]
                label = to_categorical(labels.index(label), len(labels))
                x_batch.append(img)
                y_batch.append(label)
            x_batch = np.array(x_batch, np.float32) / 255
            y_batch = np.array(y_batch, np.float32)
            yield (x_batch, y_batch)

def valid_generator():
    while True:
        for start in range(0, len(valid), batch_size):
            x_batch = []
            y_batch = []
            end = min(start + batch_size, len(valid))
            ids = valid[start:end]
            for path in ids:
                img = load_img(path, color_mode='rgb', target_size=(24,24))
                img = img_to_array(img)
                label = path.split('/')[1]
                label = to_categorical(labels.index(label), len(labels))
                x_batch.append(img)
                y_batch.append(label)
            x_batch = np.array(x_batch, np.float32) / 255
            y_batch = np.array(y_batch, np.float32)
            yield (x_batch, y_batch)

model.fit_generator(
        train_generator(),
        steps_per_epoch=len(train),
        epochs=5,
        validation_data=valid_generator(),
        validation_steps=len(valid)
)

def predict(img_path, model):
    img = load_img(img_path, color_mode='rgb', target_size=(24,24))
    img = img_to_array(img)/255
    img = np.expand_dims(img, axis=0)
    return model.predict(img)

test_path = [circle[0], triangle[1], rectangle[5]]
a = [predict(test, model) for test in test_path]
for result in a:
    print('Prediction : {}'.format(labels[np.argmax(result)]))
