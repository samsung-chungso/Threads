from imutils import paths 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
import cv2
import os 
import numpy as np
import random 
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report

imagePaths = list(paths.list_images('/home/thr/Downloads/arrow'))
random.shuffle(imagePaths)
print(imagePaths)

data = [] 
labels = []

for (i, imagePath) in enumerate(imagePaths):
    image = cv2.imread(imagePath)
    image = cv2.resize(image, (64, 64))
    data.append(image)
    label = imagePath.split(os.path.sep)[-2]
    labels.append(label)
    
data = np.array(data)
labels = np.array(labels)
print(data.shape)
print(labels.shape)
# print(labels)
# print(data[0])
# print(labels[0])
# cv2.imshow('win', data[0])
# cv2.waitKey(0)

data = data.astype("float")/255.0

(trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=0.25, random_state=42, shuffle=True)

# 기존 코드에서 LabelBinarizer 대신 to_categorical 사용
# lb = LabelBinarizer()
# trainY = lb.fit_transform(trainY)
# testY = lb.transform(testY)

# LabelEncoder를 사용해 문자열 레이블을 정수로 변환
le = LabelEncoder()
trainY = le.fit_transform(trainY)
testY = le.transform(testY)

# 변환된 정수 레이블을 원-핫 인코딩으로 변환
trainY = to_categorical(trainY, num_classes=2)
testY = to_categorical(testY, num_classes=2)

#opt = SGD(lr=0.004)
opt = SGD(learning_rate=0.01, decay=0.01 / 40, momentum=0.9, nesterov=True)

model = Sequential()
# 1 CONV
model.add(Conv2D(32, (3,3), padding="same", input_shape=(64, 64, 3)))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=-1))
model.add(Conv2D(32, (3,3), padding="same"))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))

# 2 CONV
model.add(Conv2D(64, (3,3), padding="same"))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=-1))
model.add(Conv2D(64, (3,3), padding="same"))
model.add(Activation("relu"))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))

# FC
model.add(Flatten())
model.add(Dense(512))
model.add(Activation("relu"))
model.add(BatchNormalization())
model.add(Dropout(0.5))

# Class
model.add(Dense(2))
model.add(Activation("softmax"))

# Model compile 
model.compile(loss="categorical_crossentropy",optimizer=opt, metrics=["accuracy"])

H = model.fit(trainX, trainY, validation_data=(testX, testY), batch_size=2, epochs=100, verbose=1)

predictions = model.predict(testX, batch_size=2)
print(classification_report(testY.argmax(axis=1),
	predictions.argmax(axis=1),
	target_names=[str(x) for x in le.classes_]))

model.save("vgg_arrow.h5")

plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, 100), H.history["loss"], label="train_loss")
plt.plot(np.arange(0, 100), H.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, 100), H.history["accuracy"], label="train_acc")
plt.plot(np.arange(0, 100), H.history["val_accuracy"], label="val_acc")
plt.title("Training Loss and Accuracy on arrow image")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend()
plt.savefig("vgg_arrow.png")
plt.show()
