import tensorflow as tf
import config_keras
import config
from keras.utils import to_categorical
# Deep learning
# Keras-related imports
from keras.models import Sequential
from keras.layers import Lambda, Dense, Dropout, Activation, Flatten, LSTM
from keras.layers import Convolution1D, MaxPooling2D, Convolution2D
from keras import backend as K
# K.set_image_dim_ordering('th')
from keras.callbacks import ModelCheckpoint, RemoteMonitor, EarlyStopping
from keras.models import load_model
from keras.layers import Conv2D, MaxPooling2D
from keras.regularizers import l2
import os

def train_model(X_train, y_train):


	y_train = tf.keras.utils.to_categorical(y_train, 2)



	################################ CONVOLUTIONAL NEURAL NETWORK ################################
	## NN parameters
	class_weight = {0: 1.,
	                1: 1.,
	                }
	input_shape = (1, X_train.shape[2], X_train.shape[-1])

	# BNN parameters
	dropout=config_keras.dropout  # change to 0.05
	# Regularise
	tau = config_keras.tau
	lengthscale = config_keras.lengthscale
	reg = lengthscale**2 * (1 - dropout) / (2. * len(X_train) * tau)

	W_regularizer=l2(reg)  # regularisation used in layers

	model = Sequential()
	n_dense = 128
	nb_classes = 2
	# number of convolutional filters
	nb_conv_filters = 32
	# num_hidden = 236
	nb_conv_filters_2 = 64
	convout1 = Activation('relu')
	convout2 = Activation('relu')

	model.add(Conv2D(nb_conv_filters, kernel_size = (3,3),
	     activation = 'relu', padding = 'valid', strides = 1,
	     input_shape = input_shape))
	model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Lambda(lambda x: K.dropout(x,level=dropout)))


	model.add(Conv2D(nb_conv_filters_2, kernel_size = (3,3),
	     activation = 'relu', padding = 'valid'))
	model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Lambda(lambda x: K.dropout(x,level=dropout)))

	model.add(Conv2D(nb_conv_filters_2, kernel_size = (3,3),
	     activation = 'relu', padding = 'valid'))
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Lambda(lambda x: K.dropout(x,level=dropout)))

	

	# # model.add(Dropout(0.2))
	model.add(Conv2D(nb_conv_filters_2, kernel_size = (3,3),
	     activation = 'relu', padding = 'valid'))
	model.add(Lambda(lambda x: K.dropout(x,level=dropout)))

	# model.add(Conv2D(nb_conv_filters_2, kernel_size = (3,3),
	#      activation = 'relu', padding = 'valid'))
	# model.add(Lambda(lambda x: K.dropout(x,level=dropout)))

	model.add(Flatten())
	# # Shared between MLP and CNN:
	model.add(Dense(n_dense, activation='relu'))
	model.add(Lambda(lambda x: K.dropout(x,level=dropout)))


	model.add(Dense(nb_classes, activation='softmax',W_regularizer=l2(reg)))
	model.compile(loss='categorical_crossentropy',
	                optimizer='adadelta',
	                metrics=['accuracy'])




    # if checkpoint_name is not None:
    # 	os.path.join(os.path.pardir, 'models', 'keras', checkpoint_name)

	model_name = 'Win_' + str(config.win_size) + '_Stride_' + str(config.step_size) + '_BNN.h5' 
	checkpoint_filepath = os.path.join(os.path.pardir, 'models/keras', model_name) # Need to makedir there too.
	model_checkpoint_callback = ModelCheckpoint(
	    filepath=checkpoint_filepath,
	    save_weights_only=False,
	    monitor='val_accuracy',
	    mode='max',
	    save_best_only=True)

	model.fit(x=X_train, y=y_train, batch_size=config_keras.batch_size, epochs=config_keras.epochs, verbose=1,  validation_split=config_keras.validation_split,
          validation_data=None,
          shuffle=True, class_weight=class_weight, sample_weight=None, initial_epoch=0,
          steps_per_epoch=None, validation_steps=None, callbacks=[model_checkpoint_callback])


	# print('Saving model to:', os.path.join(os.path.pardir, 'models', 'keras', checkpoint_name))


	return model


def evaluate_model(model, X_test, y_test, n_samples):
	all_y_pred = []
	for n in range(n_samples):
		all_y_pred.append(model.predict(X_test))
	return all_y_pred

def load_model(filepath):
	model = tf.keras.models.load_model(filepath, custom_objects={"dropout": config_keras.dropout})
	return model