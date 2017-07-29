import numpy as np
import keras
from keras.models import model_from_json, Model
from keras.layers import Input, Conv3D, MaxPooling3D, Flatten, Dropout, Dense
from keras.optimizers import Adam
import statsmodels.api as sm
from sklearn.neighbors import KernelDensity as KDE
import numpy as np
import pandas as pd


'''
Class name: Model
Handles backend analysis of nodule malignancy probability and intensity.

Variables:
models_dir: global directory of the models folder
data_dir: root dir of the DICOM image directory
filename: convnet model filename
patchSize: input width and height patch size of the test sample
patchZ: depth (z-dim) of the input test sample


'''
class Model():

    models_dir = '/opt/bitnami/apps/flask/sake/models/'
    data_dir = '/opt/bitnami/apps/flask/sake/data/'
    model_filename = 'model'
    data_filename = 'nodules.csv'
    patchSize = 128
    patchZ = 10
    model = None

    def __init__(self):

    	# convnet model initialization
        self.model = self.create_model(new_model=False)
        # kde model initialization
        self.kde = create_kde()

    '''
    generate_shape
    Converts a set of 3d polygon points to a pixelwise mask
    input: polygons: a 3d array of polygon points
    return: a 3d pixel-wise mask for input into the convnet
    '''
    def generate_shape(self, polygons):
        polygon = polygons[len(polygons)//2]
        center_z = len(polygons)//2
        center_x = (np.max(polygon[:,0])+np.min(polygon[:,0]))/2.
        center_y = (np.max(polygon[:,1])+np.min(polygon[:,1]))/2.
        offset = (center_x-patchSize//2, center_y-patchSize//2)
        mask = np.zeros((self.patchZ, self.patchSize, self.patchSize))
        for polygon_ind in range(len(polygons)):
            for point in polygons[polygon_ind]:
                mask[int(polygon_ind), int(point[0]-offset[0]), int(point[1]-offset[1])] = 1.
        return mask

    '''
    create_kde
    Initializes and trains a KDE model
    input: none
    return: a kde model object
    '''
    def create_kde(self):
    	nodules_df =pd.read_csv(self.data_dir+self.data_filename)
        x_init = np.array([nodules_df['x_center'],nodules_df['y_center'],
                            nodules_df['width'],nodules_df['length']]).T
        kde = KDE()
        kde.fit(x_init)
        return kde

    '''
    create_model
    Loads or creates a Keras convnet model
    input: existing model
    return Keras model
    '''
    def create_model(self, new_model=False):
        if (not new_model):
            model = model_from_json(open(self.models_dir + self.model_filename + '.json').read())
        else:
            input = Input(shape=(1, self.patchZ, self.patchSize, self.patchSize))
            x = Conv3D(32, (1, 3, 3), activation='relu', padding='valid')(input)
            x = Conv3D(32, (1, 3, 3), activation='relu', padding='valid')(x)
            x = MaxPooling3D(pool_size=(1, 2, 2))(x)
            x = Conv3D(64, (1, 3, 3), activation='relu', padding='valid')(x)
            x = Conv3D(64, (1, 3, 3), activation='relu', padding='valid')(x)
            x = MaxPooling3D(pool_size=(1, 2, 2))(x)
            x = Conv3D(128, (1, 3, 3), activation='relu', padding='valid')(x)
            x = Conv3D(128, (1, 3, 3), activation='relu', padding='valid')(x)
            x = MaxPooling3D(pool_size=(1, 2, 2))(x)
            x = Conv3D(256, (1, 3, 3), activation='relu', padding='valid')(x)
            x = Conv3D(256, (1, 3, 3), activation='relu', padding='valid')(x)
            x = MaxPooling3D(pool_size=(1, 2, 2))(x)
            x = Flatten()(x)
            x = Dropout(.5)(x)
            x = Dense(512, activation='relu')(x)
            probs= Dense(1, activation='sigmoid')(x)

            model = Model(inputs=input, outputs=probs)

        model.load_weights(self.models_dir + self.model_filename + '_weights.h5')
        model.compile(loss = 'mean_squared_error', optimizer = Adam(lr = 0.00001), metrics = ['accuracy'])

        return model

    #
    def get_malignancy(self, polygons):
        sample = np.reshape(self.generate_shape(polygons), (1, 1, 10, 128, 128))
        im_pred = self.model.predict(x=sample, batch_size=1)
        return im_pred[0][0]

    def get_percentiles(self, x_center, y_center, polygons):
        polygon = polygons[len(polygons)//2]
        x_length = np.max(polygon[:,0])-np.min(polygon[:,0])
        y_length = np.max(polygon[:,1])-np.min(polygon[:,1])
        x = np.array([x_center, y_center, x_length, y_length])
        return self.kde.score(x.reshape(1,-1))

