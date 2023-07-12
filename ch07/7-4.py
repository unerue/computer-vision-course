import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from tensorflow.keras.optimizers import SGD, Adam

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train.astype(np.float32) / 255.0
x_test = x_test.astype(np.float32) / 255.0
y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

model_sgd = tf.keras.Sequential([
    tf.keras.layers.Dense(512, activation="tanh", input_shape=(784,)),
    tf.keras.layers.Dense(10, activation="softmax"),
])
# mlp_sgd = Sequential()
# mlp_sgd.add(Dense(units=512, activation="tanh", input_shape=(784,)))
# mlp_sgd.add(Dense(units=10, activation="softmax"))

model_sgd.compile(loss="MSE", optimizer=SGD(learning_rate=0.01), metrics=["accuracy"])
hist_sgd = model_sgd.fit(
    x_train,
    y_train,
    batch_size=128,
    epochs=50,
    validation_data=(x_test, y_test),
    verbose=2,
)
print("SGD 정확률=", model_sgd.evaluate(x_test, y_test, verbose=0)[1] * 100)

model_adam = tf.keras.Sequential([
    tf.keras.layers.Dense(512, activation="tanh", input_shape=(784,)),
    tf.keras.layers.Dense(10, activation="softmax"),
])
# mlp_adam.add(Dense(units=512, activation="tanh", input_shape=(784,)))
# mlp_adam.add(Dense(units=10, activation="softmax"))

model_adam.compile(loss="MSE", optimizer=Adam(learning_rate=0.001), metrics=["accuracy"])
hist_adam = model_adam.fit(
    x_train,
    y_train,
    batch_size=128,
    epochs=50,
    validation_data=(x_test, y_test),
    verbose=2,
)
print("Adam 정확률=", model_adam.evaluate(x_test, y_test, verbose=0)[1] * 100)


plt.plot(hist_sgd.history["accuracy"], "r--")
plt.plot(hist_sgd.history["val_accuracy"], "r")
plt.plot(hist_adam.history["accuracy"], "b--")
plt.plot(hist_adam.history["val_accuracy"], "b")
plt.title("Comparison of SGD and Adam optimizers")
plt.ylim((0.7, 1.0))
plt.xlabel("epochs")
plt.ylabel("accuracy")
plt.legend(["train_sgd", "val_sgd", "train_adam", "val_adam"])
plt.grid()
plt.show()
