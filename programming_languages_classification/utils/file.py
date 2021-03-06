# /usr/bin/env python3

import os
import sys


ROOT_DIR: str = os.path.abspath(os.path.dirname(sys.argv[0]))
SOURCE_FOLDER: str = "../datasets/rosetta-code/Lang"
DESTINATION_FOLDER: str = "tmp"
TRAINING_FOLDER: str = 'training'
TESTING_FOLDER: str = 'testing'
VOCABULARIES_FOLDER: str = 'vocabularies'
MODELS_FOLDER: str = 'models'
FEATURES_FOLDER = 'features'
REPORTS_FOLDER = 'reports'


FILE_NAMES: dict = {
    'ORIGINAL': 'original',
    'PARSED': 'parsed',
    'SOURCE_MAP': 'map',
}


class FileManagerClass:

    def __init__(self):
        self.datasets = {'source': {}, 'training': {}, 'testing': {}}
        self.initialize()

    def initialize(self):
        self.datasets['source']['url'] = os.path.join(ROOT_DIR, SOURCE_FOLDER)
        self.datasets['training']['url'] = os.path.join(ROOT_DIR, *[DESTINATION_FOLDER, TRAINING_FOLDER])
        self.datasets['testing']['url'] = os.path.join(ROOT_DIR, *[DESTINATION_FOLDER, TESTING_FOLDER])
        return self

    def getOriginalFileUrl(self, exampleFolderPath):
        return exampleFolderPath + '/' + FILE_NAMES['ORIGINAL'] + '.txt'

    def getParsedFileUrl(self, exampleFolderPath):
        return exampleFolderPath + '/' + FILE_NAMES['PARSED'] + '.txt'

    def getMapFileUrl(self, exampleFolderPath):
        return exampleFolderPath + '/' + FILE_NAMES['SOURCE_MAP'] + '.json'

    def getFeaturesFileUrl(self, algorithm: str):
        fileName = algorithm + '.json'
        return os.path.join(self.getFeaturesFolderUrl(), fileName)

    def getVocabularyFileUrl(self, algorithm: str, axis: str = 'x'):
        name: str = axis + '-' + algorithm.lower() + '.json'
        return os.path.join(self.getVocabularyFolderUrl(), name)

    def getTrainedModelFileUrl(self, algorithm: str):
        extension = self.__getModelFileExtensionByAlgorithm(algorithm)
        name: str = algorithm.lower() + '.' + extension
        return os.path.join(self.getModelsFolderUrl(), name)

    def getReportFileUrl(self, algorithm: str):
        return os.path.join(self.getReportsFolderUrl(),  algorithm.lower() + '.txt')

    def getDatasetCopyFileUrl(self):
        return os.path.join(self.getTmpFolderUrl(),  '_dataset.copy.json')

    def readFile(self, url):
        file = open(url, 'r')
        fileContent = file.read()
        file.close()
        return fileContent

    def writeFile(self, url, content: str):
        file = open(url, 'w')
        file.write(content)
        file.close()

    def createFile(self, url, content: str = ''):
        file = open(url, 'w+')
        file.write(content)
        file.close()

    def getLanguagesFolders(self, datasetUrl: str):
        return [d for d in os.scandir(datasetUrl) if d.is_dir()]

    def getExamplesFolders(self, languageFolderUrl: str):
        return [d for d in os.scandir(languageFolderUrl) if d.is_dir()]

    def getExampleFiles(self, exampleFolderUrl: str):
        return [f for f in os.scandir(exampleFolderUrl) if f.is_file()]

    def getRootUrl(self):
        return ROOT_DIR

    def getTmpFolderUrl(self):
        return os.path.join(ROOT_DIR, DESTINATION_FOLDER)

    def getModelsFolderUrl(self):
        return os.path.join(ROOT_DIR, *[DESTINATION_FOLDER, MODELS_FOLDER])

    def getVocabularyFolderUrl(self):
        return os.path.join(ROOT_DIR, *[DESTINATION_FOLDER, VOCABULARIES_FOLDER])

    def getFeaturesFolderUrl(self):
        return os.path.join(ROOT_DIR, *[DESTINATION_FOLDER, FEATURES_FOLDER])

    def getReportsFolderUrl(self):
        return os.path.join(ROOT_DIR, *[DESTINATION_FOLDER, REPORTS_FOLDER])

    #

    def __getModelFileExtensionByAlgorithm(self, algorithm: str):
        algorithm = algorithm.lower()

        # Scikit-Learn: SVM + NaiveBayes
        if algorithm == 'svm' or algorithm == 'naive-bayes':
            return 'joblib'
        # Tensorflow: CNN
        return 'h5'

##


FileManager = FileManagerClass()
