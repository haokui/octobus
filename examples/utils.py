import csv
import pandas as pd


def load_tab(fp, key, **kwargs):
    params = dict(header=0,
                  index_col=None,
                  dtype={key: str})
    if fp.endswith('.xlsx'):
        params.update(kwargs)
        dat = pd.read_excel(fp, **params)
    else:
        if kwargs.get('sep', 0):
            params.update({
                'low_memory': False,  # c engine
                **kwargs
            })
        else:
            with open(fp) as csvfile:
                dialect = csv.Sniffer().sniff(csvfile.read(1024))

            params.update({
                'sep': dialect.delimiter,
                'low_memory': False,  # c engine
                **kwargs
            })

        dat = pd.read_csv(fp, **params)

    assert key in dat.columns
    dat.set_index(key, inplace=True)
    return dat
