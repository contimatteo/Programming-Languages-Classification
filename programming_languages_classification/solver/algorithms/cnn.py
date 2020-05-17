# /usr/bin/env python3

import os
from ._tensorflow import _TensorflowAlgorithm
from utils import ConfigurationManager, FileManager
from utils import FileManager
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Flatten
from keras.layers.embeddings import Embedding
from keras.layers import Conv1D, MaxPooling1D
from keras.layers import Dropout, Bidirectional
from keras.layers.recurrent import LSTM
from sklearn.model_selection import train_test_split
import os
import numpy as np

#

MODEL_CONFIG: dict = {
    'max_features': 100000,
    'embed_dim': 128,
    'lstm_out': 64,
    'batch_size': 32,
    'epochs': 10,
    'max_len_sequences': 100,
    'test_size': 0.001
}


class CNN(_TensorflowAlgorithm):

    def __init__(self):
        super().__init__()
        self.type = 'CNN'
        self.config = MODEL_CONFIG.copy()

    def __prepareModel(self, Y):
        max_features: int = self.config['max_features']
        embed_dim: int = self.config['embed_dim']
        input_length: int = self.config['max_len_sequences']
        lstm_out: int = self.config['lstm_out']

        self.model = Sequential()
        self.model.add(Embedding(max_features, embed_dim, input_length=input_length))
        self.model.add(Conv1D(filters=128, kernel_size=3, padding='same', dilation_rate=1, activation='relu'))
        self.model.add(MaxPooling1D(pool_size=4))
        self.model.add(Conv1D(filters=64, kernel_size=3, padding='same', dilation_rate=1, activation='relu'))
        self.model.add(MaxPooling1D(pool_size=2))
        self.model.add(LSTM(lstm_out))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(64))
        self.model.add(Dense(len(Y.columns), activation='softmax'))
        self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        return self

    def __prepareFeatures(self, dataset: str):
        raw_X = []
        raw_Y = []

        sources: dict = self.dataset.getSources(dataset)

        for language in self.dataset.getSources(dataset):
            for exampleDict in sources[language]:
                raw_X.append(exampleDict['original'])
                raw_Y.append(language)

        return raw_X, raw_Y

    def train(self):
        # check if a trained model already exists
        if os.path.exists(FileManager.getTrainedModelFileUrl(self.type)):
            return self

        # configs
        max_features: int = self.config['max_features']
        batch_size: int = self.config['batch_size']
        epochs: int = self.config['epochs']
        test_size: int = self.config['test_size']
        input_length: int = self.config['max_len_sequences']

        #
        # PREPARE FEATURES
        #

        # preparing features
        codeArchive, languages, = self.__prepareFeatures('training')

        # tokenization
        tokenizer = Tokenizer(num_words=max_features)
        tokenizer.fit_on_texts(codeArchive)
        # (X, Y) creation
        X = tokenizer.texts_to_sequences(codeArchive)
        X = pad_sequences(X, maxlen=input_length)
        Y = pd.get_dummies(languages)

        # export words indexes
        self.exportWordsIndexes(tokenizer.word_index)

        # split training and testing data
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size)

        #
        # TRAINING
        #

        # prepare model
        self.__prepareModel(Y)
        # training
        history = self.model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size)
        # export the trained model
        self.exportTrainedModel()

        # model evaluation
        score, acc = self.model.evaluate(X_test, Y_test, verbose=2, batch_size=batch_size)
        print(' ')
        print(" > [training] Model validation loss: %f" % score)
        print(" > [training] Model validation acc: %f" % acc)

        return self

    def test(self):
        if not os.path.exists(FileManager.getTrainedModelFileUrl(self.type)):
            raise Exception('You can\'t test a model without training it.')

        # configs
        matched = 0
        totalExamples = 0
        input_length: int = self.config['max_len_sequences']

        #
        # PREPARE FEATURES
        #

        # preparing features
        languages = ConfigurationManager.getLanguages()
        codeArchive, Y_raw = self.__prepareFeatures('testing')

        # import words indexes
        wordsIndexes = self.importWordsIndexes()
        # import trained model
        self.importTrainedModel()

        #
        # TESTING
        #

        for index, exampleSourceCode in enumerate(codeArchive):
            totalExamples += 1

            # tokenization
            word_vec = self.generateWordsIndexesForUnknownExample(wordsIndexes, exampleSourceCode)
            X = pad_sequences([word_vec], maxlen=input_length)
            X = X[0].reshape(1, X.shape[1])

            # predict
            y_prob = self.model.predict(X, batch_size=1, verbose=2)[0]

            # match language prediction
            a = np.array(y_prob)
            languagePredictedIndex = np.argmax(a)
            if str(languages[languagePredictedIndex]) == Y_raw[index]:
                matched += 1

        print('')
        print(' > [testing] ==> number of total examples = ' + str(totalExamples))
        print(' > [testing] ==> examples matched = ' + str(matched))
        print(' > [testing] ==> % success (matched/totalExamples) = ' + str(matched / totalExamples))