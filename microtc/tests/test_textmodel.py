# Copyright 2016 Mario Graff (https://github.com/mgraffg)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def test_tweet_iterator():
    import os
    import gzip
    from microtc.utils import tweet_iterator
    
    fname = os.path.dirname(__file__) + '/text.json'
    a = [x for x in tweet_iterator(fname)]
    fname_gz = fname + '.gz'
    with open(fname, 'r') as fpt:
        with gzip.open(fname_gz, 'w') as fpt2:
            fpt2.write(fpt.read().encode('ascii'))
    b = [x for x in tweet_iterator(fname_gz)]
    assert len(a) == len(b)
    for a0, b0 in zip(a, b):
        assert a0['text'] == b0['text']
    os.unlink(fname_gz)


def test_textmodel():
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator
    import os
    fname = os.path.dirname(__file__) + '/text.json'
    tw = list(tweet_iterator(fname))
    text = TextModel([x['text'] for x in tw])
    # print(text.tokenize("hola amiguitos gracias por venir :) http://hello.com @chanfle"))
    # assert False
    assert isinstance(text[tw[0]['text']], list)
    assert len(text[tw[0]]) == 3


def test_params():
    import os
    import itertools
    from microtc.params import BASIC_OPTIONS
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator

    params = dict(del_diac=[True, False], usr_option=BASIC_OPTIONS,
                  url_option=BASIC_OPTIONS)
    params = sorted(params.items())
    fname = os.path.dirname(__file__) + '/text.json'
    tw = [x for x in tweet_iterator(fname)]
    text = [x['text'] for x in tw]
    for x in itertools.product(*[x[1] for x in params]):
        args = dict(zip([x[0] for x in params], x))
        ins = TextModel(text, **args)
        assert isinstance(ins[text[0]], list)


def test_lang():
    from microtc.textmodel import TextModel

    text = [
        "Hi :) :P XD",
        "excelente dia xc",
        "el alma de la fiesta XD"
    ]
    model = TextModel(text, **{
        "del_dup": True,
        "emo_option": "group",
        "lc": True,
        "num_option": "group",
        "del_diac": False,
        "token_list": [
            (2, 1),
            (2, 2),
            -1,
            # 5,
        ],
        "url_option": "group",
        "usr_option": "group",
    })
    text = "El alma de la fiesta :) conociendo la maquinaria @user bebiendo nunca manches que onda"
    a = model.tokenize(text)
    b = ['el~de', 'alma~la', 'de~fiesta', 'la~_pos', 'fiesta~conociendo', '_pos~la', 'conociendo~maquinaria', 'la~_usr', 'maquinaria~bebiendo', '_usr~nunca',
         'bebiendo~manches', 'nunca~que', 'manches~onda', 'el~la', 'alma~fiesta', 'de~_pos', 'la~conociendo', 'fiesta~la', '_pos~maquinaria', 'conociendo~_usr',
         'la~bebiendo', 'maquinaria~nunca', '_usr~manches', 'bebiendo~que', 'nunca~onda', 'el', 'alma', 'de', 'la', 'fiesta', '_pos',
         'conociendo', 'la', 'maquinaria', '_usr', 'bebiendo', 'nunca', 'manches', 'que', 'onda']
    print(text)
    assert a == b, "got: {0}, expected: {1}".format(a, b)


def test_textmodel_token_min_filter():
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator
    import os
    fname = os.path.dirname(__file__) + '/text.json'
    tw = list(tweet_iterator(fname))
    text = TextModel(tw, token_min_filter=1, token_list=[-2, -1, 3, 4])
    print(len(text.model._w2id), 'hh', text.token_min_filter, text.token_max_filter)
    assert len(text.model._w2id) == 28
    text = TextModel(tw, token_min_filter=0.01, token_list=[-2, -1, 3, 4])
    print(len(text.model._w2id))
    assert len(text.model._w2id) == 28
    text = TextModel(tw, token_min_filter=1)


def test_textmodel_token_max_filter():
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator
    import os
    fname = os.path.dirname(__file__) + '/text.json'
    tw = list(tweet_iterator(fname))
    text = TextModel(tw, token_max_filter=len(tw) / 2, token_list=[-2, -1, 3, 4])
    print(len(text.model._w2id))
    assert len(text.model._w2id) == 28
    text = TextModel(tw, token_max_filter=0.5, token_list=[-2, -1, 3, 4])
    print(len(text.model._w2id))
    assert len(text.model._w2id) == 27
    text = TextModel(tw, token_max_filter=2)
    print(len(text.model._w2id))


def test_textmodel_entropy():
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator
    import os
    fname = os.path.dirname(__file__) + '/text.json'
    tw = list(tweet_iterator(fname))
    text = TextModel(tw, weighting='microtc.weighting.Entropy', token_list=[-1, 3])
    # print(text.tokenize("hola amiguitos gracias por venir :) http://hello.com @chanfle"))
    # assert False
    assert isinstance(text[tw[0]['text']], list)
    _ = text[tw[0]]
    print(_)
    for k, v in _:
        assert text.model.wordWeight[k] == v


def test_textmodel_transform_tonp():
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator
    from sklearn.svm import LinearSVC
    from sklearn.preprocessing import LabelEncoder
    import os
    fname = os.path.dirname(__file__) + '/text.json'
    tw = list(tweet_iterator(fname))
    text = TextModel().fit(tw)
    X = text.transform(tw)
    le = LabelEncoder().fit([x['klass'] for x in tw])
    y = le.transform([x['klass'] for x in tw])
    m = LinearSVC().fit(text.tonp(X), y)
    assert len(m.predict(text.tonp(X))) == len(y)


def test_textmodel_compute_tokens():
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator
    import os
    fname = os.path.dirname(__file__) + '/text.json'
    tw = list(tweet_iterator(fname))
    tm = TextModel(token_list=[-2, -1])
    text = tm.text_transformations(tw[0]['text'])
    L = tm.compute_tokens(text)
    assert len(L) == 2
    r = []
    [r.__iadd__(x) for x in L]
    for a, b in zip(tm.tokenize(tw[0]), r):
        assert a == b


def test_textmodel_weighting_key():
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator
    import os
    fname = os.path.dirname(__file__) + '/text.json'
    tw = list(tweet_iterator(fname))
    for w in ['tfidf', 'tf', 'entropy']:
        TextModel(token_list=[-2, -1], weighting=w).fit(tw)


def test_textmodel_save_load():
    import os
    from microtc.textmodel import TextModel
    from microtc.utils import tweet_iterator, save_model, load_model
    fname = os.path.dirname(__file__) + '/text.json'
    tw = list(tweet_iterator(fname))
    tm = TextModel().fit(tw)
    save_model(tm, 't.model')
    assert isinstance(load_model('t.model'), TextModel)
    os.unlink('t.model')
    
    
