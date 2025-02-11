# Copyright 2016 Eric S. Tellez

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import gzip


def line_iterator(filename):
    if filename.endswith(".gz"):
        f = gzip.GzipFile(filename)
    else:
        f = open(filename, encoding='utf8')

    while True:
        line = f.readline()
        # Test the type of the line and encode it if neccesary...
        if type(line) is bytes:
            line = str(line, encoding='utf8')

        # If the line is empty, we are done...
        if len(line) == 0:
            break

        line = line.strip()
        # If line is empty, jump to next...
        if len(line) == 0:
            continue

        yield line

    # Close the file...
    f.close()


def tweet_iterator(filename):
    for line in line_iterator(filename):
        yield json.loads(line)


TEXT = os.environ.get("TEXT", 'text')
KLASS = os.environ.get("KLASS", 'klass')
VALUE = os.environ.get("VALUE", 'value')


def read_data_labels(filename, get_tweet=TEXT,
                     get_klass=KLASS, maxitems=1e100):
    data, labels = [], []
    count = 0
    for tweet in tweet_iterator(filename):
        count += 1
        try:
            x = get_tweet(tweet) if callable(get_tweet) else tweet[get_tweet]
            y = get_klass(tweet) if callable(get_klass) else tweet[get_klass]
            data.append(x)
            labels.append(str(y))
            if count == maxitems:
                break
        except KeyError as e:
            raise e

    return data, labels


def read_data_values(filename, get_tweet=TEXT, get_value=VALUE, maxitems=1e100):
    data, values = [], []
    count = 0
    for tweet in tweet_iterator(filename):
        count += 1
        try:
            x = get_tweet(tweet) if callable(get_tweet) else tweet[get_tweet]
            y = get_value(tweet) if callable(get_value) else tweet[get_value]
            data.append(x)
            values.append(float(y))
            if count == maxitems:
                break
        except KeyError as e:
            raise e

    return data, values


def read_data(filename, get_tweet=TEXT, maxitems=1e100):
    data = []
    count = 0
    for tweet in tweet_iterator(filename):
        count += 1
        x = get_tweet(tweet) if callable(get_tweet) else tweet[get_tweet]
        data.append(x)
        if count == maxitems:
            break

    return data


def get_class(m):
    """Import class from string

    :param m: string or class to be imported
    :type m: str or class
    :rtype: class

    >>> get_class('microtc.textmodel.TextModel')
    <class 'microtc.textmodel.TextModel'>
    """
    import importlib

    if isinstance(m, str):
        a = m.split('.')
        p = importlib.import_module('.'.join(a[:-1]))
        return getattr(p, a[-1])
    return m


def load_model(fname):
    """Read model from file. The model must be stored using gzip and pickle

    :param fname: filename
    :type fname: str (path)
    """
    import gzip
    import pickle
    with gzip.open(fname, 'r') as fpt:
        _ = pickle.load(fpt)
    return _


def save_model(obj, fname):
    """Store model from file. The model is stored using gzip and pickle

    :param obj: object to store
    :type obj: object
    :param fname: filename
    :type fname: str (path)
    """
    
    import gzip
    import pickle
    with gzip.open(fname, 'w') as fpt:
        pickle.dump(obj, fpt)

