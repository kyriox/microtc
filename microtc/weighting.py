# Copyright 2018 Mario Graff

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import numpy as np
from .utils import KLASS 
from collections import Counter


class TFIDF(object):
    """
    Vector Space model using TFIDF

    :param docs: corpus as a list of list of tokens
    :type docs: list
    :param X: original corpus, useful to pass extra information in a dict
    :type X: list
    :param token_min_filter: Keep those tokens that appear more times than the parameter
    :type token_min_filter: int or float

    :param token_max_filter: Keep those tokens that appear less times than the parameter
    :type token_max_filter: int or float

    Usage:

    >>> from microtc.weighting import TFIDF
    >>> tokens = [['buenos', 'dia', 'microtc'], ['excelente', 'dia'], ['buenas', 'tardes'], ['las', 'vacas', 'me', 'deprimen'], ['odio', 'los', 'lunes'], ['odio', 'el', 'trafico'], ['la', 'computadora'], ['la', 'mesa'], ['la', 'ventana']]
    >>> tfidf = TFIDF(tokens)
    >>> vector = tfidf['buenos', 'X', 'trafico']
    """

    def __init__(self, docs, X=None, token_min_filter=0, token_max_filter=1):
        w2id = {}
        weight = {}
        self._ndocs = len(docs)
        for tokens in docs:
            for x, freq in Counter(tokens).items():
                try:
                    ident = w2id[x]
                    weight[ident] = weight[ident] + 1
                except KeyError:
                    ident = len(w2id)
                    w2id[x] = ident
                    weight[ident] = 1
        if token_min_filter > 0 or token_max_filter != 1:
            if token_min_filter < 1:
                token_min_filter = int(self._ndocs * token_min_filter)
                if token_min_filter < 1:
                    token_min_filter = 1
            if token_min_filter > 0:
                w2id = [(k, v) for k, v in w2id.items() if weight[v] > token_min_filter]
            if token_max_filter != 1:
                if token_max_filter < 1:
                    token_max_filter = int(self._ndocs * token_max_filter)
                w2id = [(k, v) for k, v in w2id if weight[v] < token_max_filter]
            w2id.sort(key=lambda x: x[1])
            mm = {k: v[1] for k, v in enumerate(w2id)}
            w2id = {v[0]: k for k, v in enumerate(w2id)}
            weight = {ident: weight[mm[ident]] for ident in w2id.values()}
        self.word2id = w2id
        self.wordWeight = weight

    @property
    def num_terms(self):
        """Number of terms"""

        return self._num_terms

    @property
    def word2id(self):
        """Map word to id"""

        return self._w2id

    @word2id.setter
    def word2id(self, value):
        self._num_terms = len(value)
        self._w2id = value

    @property
    def wordWeight(self):
        """Weight associated to each word, this could be the inverse document frequency"""
        return self._weight

    @wordWeight.setter
    def wordWeight(self, value):
        """Inverse document frequency

        :param value: weights
        :type value: dict
        """

        N = self._ndocs
        self._weight = {k: np.log2(N / v) for k, v in value.items()}

    def doc2weight(self, tokens):
        """Weight associated to each token

        :param tokens: list of tokens
        :type tokens: lst

        :rtype: tuple - ids, term frequency, wordWeight
        """
        lst = []
        w2id = self._w2id
        weight = self.wordWeight
        for token in tokens:
            try:
                id = w2id[token]
                lst.append(id)
            except KeyError:
                continue
        ids_tf = [(a, b) for a, b in Counter(lst).items()]
        # ids, tf = np.unique(lst, return_counts=True)
        ids = [x[0] for x in ids_tf]
        tf = np.array([x[1] for x in ids_tf])
        tf = tf / tf.sum()
        df = np.array([weight[x] for x in ids])
        return ids, tf, df

    def __getitem__(self, tokens):
        """
        TF-IDF and the vectors are normalised.

        :param tokens: list of tokens
        :type tokens: lst

        :rtype: lst
        """

        __ = self.doc2weight(tokens)
        r = [(i, _tf * _df) for i, _tf, _df in zip(*__)]
        n = np.sqrt(sum([x * x for _, x in r]))
        return [(i, x/n) for i, x in r]


class TF(TFIDF):
    @property
    def wordWeight(self):
        """Weight associated to each word, this is one on TF"""
        return self._weight

    @wordWeight.setter
    def wordWeight(self, value):
        """Inverse document frequency

        :param value: weights
        :type value: dict
        """

        self._weight = {k: 1 for k, v in value.items()}

    def __getitem__(self, tokens):
        """
        TF, the frequency is normalised

        :param tokens: list of tokens
        :type tokens: lst

        :rtype: lst
        """

        __ = self.doc2weight(tokens)
        r = [(i, _tf) for i, _tf, _df in zip(*__)]
        return r


class Entropy(TFIDF):
    """
    Vector Space using 1 - entropy as the weighting scheme

    Usage:

    >>> from microtc.weighting import Entropy
    >>> tokens = [['buenos', 'dia', 'microtc'], ['excelente', 'dia'], ['buenas', 'tardes'], ['las', 'vacas', 'me', 'deprimen', 'al', 'dia'], ['odio', 'los', 'lunes'], ['odio', 'el', 'trafico'], ['la', 'computadora'], ['la', 'mesa'], ['la', 'ventana']]
    >>> y = [0, 0, 0, 2, 2, 2, 1, 1, 1]
    >>> ent = Entropy(tokens, X=[dict(text=t, klass=k) for t, k in zip(tokens, y)])
    >>> vector = ent['buenos', 'X', 'dia']
    """
    def __init__(self, docs, X=None, **kwargs):
        assert X is not None
        super(Entropy, self).__init__(docs, X=X, **kwargs)
        self.wordWeight = self.entropy(docs, X, self.word2id)

    @property
    def wordWeight(self):
        """Weight associated to each word, entropy per token"""
        return self._weight

    @wordWeight.setter
    def wordWeight(self, value):
        """Entropy

        :param value: weights
        :type value: dict
        """

        if isinstance(value, dict):
            self._weight = value
        else:
            self._weight = {k: v for k, v in enumerate(value)}

    @staticmethod
    def entropy(corpus, docs, word2id):
        """
        Compute entropy

        :param corpus: Tokenized corpus, i.e., as a list of tokens list
        :type corpus: list
        :param docs: Original corpus is a list of dictionaries where key klass contains the class or label
        :type docs: list
        :param word2id: Map token to identifier
        :type word2id: dict

        :rtype: np.array
        """
        m = word2id
        y = [x[KLASS] for x in docs]
        klasses = np.unique(y)
        nklasses = klasses.shape[0]
        ntokens = len(m)
        weight = np.zeros((klasses.shape[0], ntokens))
        for ki, klass in enumerate(klasses):
            for _y, tokens in zip(y, corpus):
                if _y != klass:
                    continue
                for x in Counter(tokens).keys():
                    try:
                        weight[ki, m[x]] += 1
                    except KeyError:
                        continue
        weight = weight / weight.sum(axis=0)
        weight[~np.isfinite(weight)] = 1.0 / nklasses
        logc = np.log2(weight)
        logc[~np.isfinite(logc)] = 0
        if nklasses > 2:
            logc = logc / np.log2(nklasses)
        return (1 + (weight * logc).sum(axis=0))

    def __getitem__(self, tokens):
        """
        Entropy

        :param tokens: list of tokens
        :type tokens: lst

        :rtype: lst
        """

        __ = self.doc2weight(tokens)
        r = [(i, _df) for i, _tf, _df in zip(*__)]
        return r
