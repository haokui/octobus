import os
from utils import load_tab
from octobus import *


# 1. load omics dataset
folder = 'data'
meta = load_tab(os.path.join(folder, 'metadata.tsv'), key='SampleID')
genus = load_tab(os.path.join(folder, 'genus.tsv'), key='SampleID')

# 2. Ingest data to DataStore
data_store = DataStore()
data_store.ingest(name='meta', dataframe=meta)
data_store.ingest(name='genus', dataframe=genus)
print('Entities of genus in data store: {}'.format(len(data_store['genus'].entities)))
print('Features of genus in data store: {}'.format(len(data_store['genus'].features)))

# 3. Extract & slice data from DataStore to FeatureStore
meta_store = FeatureStore(data_store['meta'], name='meta')
genus_store = FeatureStore(data_store['genus'], features=data_store['genus'].features[:50], name='genus')
print('Entities of meta store: {}'.format(len(meta_store.entities)))
print('Entities of genus store: {}'.format(len(genus_store.entities)))
print('Features of genus store: {}'.format(len(genus_store.features)))

# 4. Register SampleStore for samples required
samples = SampleStore(samples=meta_store.entities)
# 4-1. Bind feature store to sample store
samples.add_features(meta_store)
samples.add_features(genus_store)

print('Retrieve data cross table:\n{}'.format(
    samples.get_data([
        'k__Bacteria;p__Firmicutes;c__Bacilli;o__Lactobacillales;f__Streptococcaceae;g__Streptococcus',
        'Antibiotics Usage'
    ])
))

# 4-2. Filter samples
samples.filter(samples['Age'] < 60)
print('Retrieve data cross table:\n{}'.format(
    samples.get_data([
        'k__Bacteria;p__Firmicutes;c__Bacilli;o__Lactobacillales;f__Streptococcaceae;g__Streptococcus',
        'Antibiotics Usage'
    ])
))

# 5. Dynamic attach feature store to sample store with FeatureManager
samples = SampleStore(samples=meta_store.entities)
with FeatureManager(meta_store, samples) as fm_meta:
    with FeatureManager(genus_store, samples) as fm_genus:
        samples.filter(samples['Age'] < 60)
        data_set = DataSet(X=samples.get_data(features=genus_store.features),
                           y=samples.get_data(features=['Antibiotics Usage']))
        print('data set: \n{}'.format(data_set.get_data()))
        print('X in data set: \n{}'.format(data_set.X))
        print('y in data set" \n{}'.format(data_set.y))

    print('features out of genus context: {}'.format(
        samples.feature_context.features
    ))
print('features out of meta context: {}'.format(
    samples.feature_context.features
))
