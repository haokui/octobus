"""
core APIs of the data models
"""
from collections import defaultdict
import numpy as np
import pandas as pd


class FeatureSet:
    """
    currently, just a named list of feature names
    """
    def __init__(self, feature_names=None, name=None):
        self.feature_names = feature_names
        self.name = name

    def __getitem__(self, key):
        return self.feature_names[key]


class DataSource:
    def __init__(self, dataframe):
        self.data = dataframe

    @property
    def entities(self):
        return self.data.index

    @property
    def features(self):
        return self.data.columns

    def __getitem__(self, key):
        return DataSource(self.data[key])

    @property
    def loc(self):
        return self.data.loc


class DataStore:
    def __init__(self):
        self.data_store = {}

    def register_features(self, features):
        # check for valid features
        print('ingested features: {}'.format(len(features)))

    def register_entities(self, entities):
        # check for valid entities
        print('ingested entities: {}'.format(len(entities)))

    def register_data(self, name, data):
        if name in self.data_store:
            raise '{} is already registered'.format(name)
        print('ingested data source name: {}'.format(name))
        self.register_features(data.features)
        self.register_entities(data.entities)
        self.data_store[name] = data

    def ingest(self, name, dataframe, entity_idx=None):
        _data = dataframe
        if entity_idx:
            # todo: do not change the original dataframe ???
            _data.set_index(entity_idx, inplace=True)
        self.register_data(name=name,
                           data=DataSource(_data))

    def __getitem__(self, key):
        return self.data_store[key]


class FeatureStore:
    def __init__(self, data_source, features=None, name='unnamed'):
        if features is None:
            features = data_source.features
        self.features = features
        self.data = data_source[features]
        self.name = name
        # TODO: add timestamp for feature context sorting

    @property
    def entities(self):
        return self.data.entities

    def __getitem__(self, key):
        return self.data[key]

    @property
    def loc(self):
        return self.data.loc

    def __repr__(self):
        return '{} [feature store]'.format(self.name)


class FeatureContext:
    """
    store and manage the feature context in a first-in-last-out manner
    """
    def __init__(self):
        # each feature is mapped to a list of feature stores
        # in a first-in-last-out manner
        self.feature_context = defaultdict(list)

    def append(self, feature_store, features=None):
        if features is None:
            features = feature_store.features
        for feature in features:
            self.feature_context[feature].append(feature_store)

    def pop(self, feature_store, features=None):
        if features is None:
            features = feature_store.features
        for feature in features:
            if self.feature_context[feature][-1] is feature_store:
                self.feature_context[feature].pop()

    def __getitem__(self, feature):
        feature_stores = self.feature_context[feature]
        if len(feature_stores) == 0:
            return None
        else:
            return self.feature_context[feature][-1]

    @property
    def features(self):
        return [feature_name for feature_name, feature_stores in self.feature_context.items()
                if len(feature_stores) > 0]


class SampleStore:
    def __init__(self, samples=None):
        self.samples = set()
        if samples is not None:
            self.add_samples(samples)
        self.feature_context = FeatureContext()

    def add_samples(self, samples):
        self.samples.update(samples)

    def filter(self, condition):
        filter_samples = condition[condition].index
        self.samples.difference_update(filter_samples)

    def get_data(self, features=None):
        if features is None:
            features = self.feature_context.features
        collected_stores = defaultdict(list)
        for feature in features:
            fs = self.feature_context[feature]
            if fs is not None:
                collected_stores[fs].append(feature)
        data = [fs.loc[list(self.samples), features] for fs, features in collected_stores.items()]
        return pd.concat(data, axis=1)

    def add_features(self, feature_store, features=None):
        self.feature_context.append(feature_store=feature_store,
                                    features=features)

    def remove_features(self, feature_store, features=None):
        self.feature_context.pop(feature_store=feature_store,
                                 features=features)

    def __getitem__(self, feature):
        feature_store = self.feature_context[feature]
        if feature_store is None:
            raise 'No such feature for in this sample store: {}'.format(feature)

        return feature_store.loc[list(self.samples), feature]


class DataSet:
    def __init__(self, X, y=None):
        self.samples = X.index
        self.features = X.columns
        self.X = X
        self.y = None
        if y is not None:
            self.set_y(y)

    def set_y(self, y):
        assert y.index.equals(self.samples)
        self.y = y.loc[self.samples]

    def get_data(self, with_y=True):
        if with_y:
            if self.y is None:
                y = pd.Series(np.nan, index=self.samples)
            else:
                y = self.y
            return pd.concat([self.X, y], axis=1)
        else:
            return self.X


class FeatureManager:
    def __init__(self, feature_store, sample_store, features=None, verbose=1):
        self.feature_store = feature_store
        self.sample_store = sample_store
        self.verbose = verbose
        if features is None:
            self.features = feature_store.features

    def __enter__(self):
        self.sample_store.add_features(self.feature_store, features=self.features)
        if self.verbose > 0:
            print('>>> {} features are added with {}'.format(len(self.features), repr(self.feature_store)))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sample_store.remove_features(self.feature_store, features=self.features)
        if self.verbose > 0:
            print('<<< {} features are removed with {}'.format(len(self.features), repr(self.feature_store)))
