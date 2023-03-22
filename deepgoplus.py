#!/usr/bin/env python

import click as ck
import numpy as np
import pandas as pd
import tensorflow as tf
import logging
import math

from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import (
    Input, Dense, Embedding, Conv1D, Flatten, Concatenate,
    MaxPooling1D, Dropout, RepeatVector, Layer
)
from tensorflow.keras.utils import Sequence
from tensorflow.keras import backend as K
from tensorflow.keras.optimizers import Adam, RMSprop
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, CSVLogger
from sklearn.metrics import roc_curve, auc, matthews_corrcoef

from utils import Ontology, FUNC_DICT
from aminoacids import to_ngrams, to_onehot, MAXLEN

logging.basicConfig(level=logging.INFO)



# config = tf.ConfigProto(allow_soft_placement=True) not required if 
tf.config.set_soft_device_placement(True)


# config.gpu_options.allow_growth = True
# session = tf.Session(config=config)
# K.set_session(session)

@ck.command()
@ck.option(
    '--go-file', '-gf', default='data/go.obo',
    help='Gene Ontology file in OBO Format')
@ck.option(
    '--train-data-file', '-trdf', default='data/train_data.pkl',
    help='Data file with sequences and complete set of annotations')
@ck.option(
    '--test-data-file', '-tsdf', default='data/test_data.pkl',
    help='Data file with sequences and complete set of annotations')
@ck.option(
    '--terms-file', '-tf', default='data/terms.pkl',
    help='Data file with sequences and complete set of annotations')
@ck.option(
    '--model-file', '-mf', default='data/model.h5',
    help='DeepGOPlus model')
@ck.option(
    '--out-file', '-o', default='data/predictions.pkl',
    help='Result file with predictions for test set')
@ck.option(
    '--split', '-s', default=0.9,
    help='train/valid split')
@ck.option(
    '--batch-size', '-bs', default=32,
    help='Batch size')
@ck.option(
    '--epochs', '-e', default=12,
    help='Training epochs')
@ck.option(
    '--load', '-ld', is_flag=True, help='Load Model?')
@ck.option(
    '--logger-file', '-lf', default='data/training.csv',
    help='Batch size')
@ck.option(
    '--threshold', '-th', default=0.5,
    help='Prediction threshold')
@ck.option(
    '--device', '-d', default='gpu:0',
    help='Prediction threshold')
@ck.option(
    '--params-index', '-pi', default=-1,
    help='Definition mapping file')
def main(go_file, train_data_file, test_data_file, terms_file, model_file,
         out_file, split, batch_size, epochs, load, logger_file, threshold,
         device, params_index):
    params = {
        'max_kernel': 129,
        'initializer': 'glorot_normal',
        'dense_depth': 0,
        'nb_filters': 512,
        'optimizer': Adam(lr=3e-4),
        'loss': 'binary_crossentropy'
    }
    # SLURM JOB ARRAY INDEX
    pi = params_index
    if params_index != -1:
        kernels = [33, 65, 129, 257, 513]
        dense_depths = [0, 1, 2]
        nb_filters = [32, 64, 128, 256, 512]
        params['max_kernel'] = kernels[pi % 5]
        pi //= 5
        params['dense_depth'] = dense_depths[pi % 3]
        pi //= 3
        params['nb_filters'] = nb_filters[pi % 5]
        pi //= 5
        out_file = f'data/predictions_{params_index}.pkl'
        logger_file = f'data/training_{params_index}.csv'
        model_file = f'data/model_{params_index}.h5'
    print('Params:', params)
    
    go = Ontology(go_file, with_rels=True)
    terms_df = pd.read_pickle(terms_file)
    terms = terms_df['terms'].values.flatten()
    
    train_df, valid_df = load_data(train_data_file, terms, split)
    test_df = pd.read_pickle(test_data_file)
    terms_dict = {v: i for i, v in enumerate(terms)}
    nb_classes = len(terms)
    with tf.device('/' + device):
        test_steps = int(math.ceil(len(test_df) / batch_size))
        test_generator = DFGenerator(test_df, terms_dict,
                                     nb_classes, batch_size)
        if load:
            logging.info('Loading pretrained model')
            model = load_model(model_file)
        else:
            logging.info('Creating a new model')
            model = create_model(nb_classes, params)
            
            logging.info("Training data size: %d" % len(train_df))
            logging.info("Validation data size: %d" % len(valid_df))
            checkpointer = ModelCheckpoint(
                filepath=model_file,
                verbose=1, save_best_only=True)
            earlystopper = EarlyStopping(monitor='val_loss', patience=6, verbose=1)
            logger = CSVLogger(logger_file)

            logging.info('Starting training the model')

            valid_steps = int(math.ceil(len(valid_df) / batch_size))
            train_steps = int(math.ceil(len(train_df) / batch_size))
            train_generator = DFGenerator(train_df, terms_dict,
                                          nb_classes, batch_size)
            valid_generator = DFGenerator(valid_df, terms_dict,
                                          nb_classes, batch_size)
    
            model.summary()
            model.fit(
                train_generator,
                steps_per_epoch=train_steps,
                epochs=epochs,
                validation_data=valid_generator,
                validation_steps=valid_steps,
                max_queue_size=batch_size,
                workers=12,
                callbacks=[logger, checkpointer, earlystopper])
            logging.info('Loading best model')
            model = load_model(model_file)

    
        logging.info('Evaluating model')
        loss = model.evaluate(test_generator, steps=test_steps)
        logging.info('Test loss %f' % loss)
        logging.info('Predicting')
        test_generator.reset()
        preds = model.predict(test_generator, steps=test_steps)
        
        # valid_steps = int(math.ceil(len(valid_df) / batch_size))
        # valid_generator = DFGenerator(valid_df, terms_dict,
        #                               nb_classes, batch_size)
        # logging.info('Predicting')
        # valid_generator.reset()
        # preds = model.predict_generator(valid_generator, steps=valid_steps)
        # valid_df.reset_index()
        # valid_df['preds'] = list(preds)
        # train_df.to_pickle('data/train_data_train.pkl')
        # valid_df.to_pickle('data/train_data_valid.pkl')
        
    test_labels = np.zeros((len(test_df), nb_classes), dtype=np.int32)
    for i, row in enumerate(test_df.itertuples()):
        for go_id in row.prop_annotations:
            if go_id in terms_dict:
                test_labels[i, terms_dict[go_id]] = 1
    logging.info('Computing performance:')
    roc_auc = compute_roc(test_labels, preds)
    logging.info('ROC AUC: %.2f' % (roc_auc,))
    test_df['labels'] = list(test_labels)
    test_df['preds'] = list(preds)
    
    logging.info('Saving predictions')
    test_df.to_pickle(out_file)

def compute_roc(labels, preds):
    # Compute ROC curve and ROC area for each class
    fpr, tpr, _ = roc_curve(labels.flatten(), preds.flatten())
    roc_auc = auc(fpr, tpr)
    return roc_auc


def create_model(nb_classes, params):
    inp_hot = Input(shape=(MAXLEN, 21), dtype=np.float32)
    
    kernels = range(8, params['max_kernel'], 8)
    nets = []
    for i in range(len(kernels)):
        conv = Conv1D(
            filters=params['nb_filters'],
            kernel_size=kernels[i],
            padding='valid',
            name='conv_' + str(i),
            kernel_initializer=params['initializer'])(inp_hot)
        print(conv.get_shape())
        pool = MaxPooling1D(
            pool_size=MAXLEN - kernels[i] + 1, name='pool_' + str(i))(conv)
        flat = Flatten(name='flat_' + str(i))(pool)
        nets.append(flat)

    net = Concatenate(axis=1)(nets)
    for i in range(params['dense_depth']):
        net = Dense(nb_classes, activation='relu', name='dense_' + str(i))(net)
    net = Dense(nb_classes, activation='sigmoid', name='dense_out')(net)
    model = Model(inputs=inp_hot, outputs=net)
    model.summary()
    model.compile(
        optimizer=params['optimizer'],
        loss=params['loss'])
    logging.info('Compilation finished')

    return model



def load_data(data_file, terms, split):
    df = pd.read_pickle(data_file)
    n = len(df)
    # Split train/valid
    n = len(df)
    index = np.arange(n)
    train_n = int(n * split)
    np.random.seed(seed=0)
    np.random.shuffle(index)
    train_df = df.iloc[index[:train_n]]
    valid_df = df.iloc[index[train_n:]]

    return train_df, valid_df
    

class DFGenerator(Sequence):

    def __init__(self, df, terms_dict, nb_classes, batch_size):
        self.start = 0
        self.size = len(df)
        self.df = df
        self.batch_size = batch_size
        self.nb_classes = nb_classes
        self.terms_dict = terms_dict


    ### copied from deepgopp    
    def __len__(self):                                                                                                                   
        return np.ceil(len(self.df) / float(self.batch_size)).astype(np.int32)   

    def __getitem__(self, idx):                                                                                                          
        batch_index = np.arange(                                                                                                         
            idx * self.batch_size, min(self.size, (idx + 1) * self.batch_size))                                                          
        df = self.df.iloc[batch_index]                                                                                                   
        data_onehot = np.zeros((len(df), MAXLEN, 21), dtype=np.float32)
        labels = np.zeros((len(df), self.nb_classes), dtype=np.int32)
        for i, row in enumerate(df.itertuples()):
            seq = row.sequences
            onehot = to_onehot(seq)
            data_onehot[i, :, :] = onehot
            for t_id in row.prop_annotations:
                if t_id in self.terms_dict:
                    labels[i, self.terms_dict[t_id]] = 1
        self.start += self.batch_size
        print(data_onehot, labels)
        return (data_onehot, labels)
    ###################

    def __next__(self):
        return self.next()

    def reset(self):
        self.start = 0

    def next(self):
        if self.start < self.size:
            batch_index = np.arange(
                self.start, min(self.size, self.start + self.batch_size))
            df = self.df.iloc[batch_index]
            data_onehot = np.zeros((len(df), MAXLEN, 21), dtype=np.int32)
            labels = np.zeros((len(df), self.nb_classes), dtype=np.int32)
            for i, row in enumerate(df.itertuples()):
                seq = row.sequences
                onehot = to_onehot(seq)
                data_onehot[i, :, :] = onehot
                for t_id in row.prop_annotations:
                    if t_id in self.terms_dict:
                        labels[i, self.terms_dict[t_id]] = 1
            self.start += self.batch_size
            return (data_onehot, labels)
        else:
            self.reset()
            return self.next()

    
if __name__ == '__main__':
    main()
