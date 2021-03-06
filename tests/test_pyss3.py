"""Tests for pytest."""
from os import path
from shutil import rmtree
from pyss3.util import Dataset
from pyss3 import \
    SS3, STR_NORM_GV_XAI, STR_XAI, STR_MOST_PROBABLE, \
    STR_UNKNOWN, STR_UNKNOWN_CATEGORY, IDX_UNKNOWN_CATEGORY, \
    PARA_DELTR, SENT_DELTR, WORD_DELTR

import pyss3
import pytest

DATASET_FOLDER = "dataset"

dataset_path = path.join(path.abspath(path.dirname(__file__)), DATASET_FOLDER)

x_train, y_train = Dataset.load_from_files(dataset_path, folder_label=False)
x_test = [
    "sports nfl nba superbowl soccer football team. learns jersey air bowl hockey.\n"
    "baseball helmet mccutchen jordan curry poker.",

    "travel pictures images moment glamour canvas photoshoot lens dslr portrait "
    "beautiful seasons lines colours snap usm af eos painter gallery museum  "
    "flower kinkade.",

    "hairstyles boutique handbag dress trends womens menswear luxury claudiepierlot "
    "rustic wedding bride collection signed patrick ista streetstyle cocksox purse "
    "trending status brush cosmetic stretchy gucci leather cream trendy "
    "bargains victoria.",

    "finance business development fiverr hiring job social debt logos stationary "
    "read bad media mlm uganda entrepreneurship strategy mistake 1st employee "
    "financial inbound habits coupon.",

    "cooking cook chef food drink rice kitchen cold organic yummy yum bread "
    "strawberry bbq pepper beverages grocery cupcakes easter gurpreet sushi "
    "dining meal chicken lime mushrooms restaurant whiskey.",

    "vitamins calcium minerals workout weightloss fit skin spa motivation care "
    "health yoga food shampoo niche 100ml juvederm losing edp munched "
    "rejuvenating lipstick vegetables.",

    "rock roll radio entertainment playing song celine dion hiphop sinatra britney "
    "spears nowplaying music flow streaming dalston fm hogan songs taylor.",

    "android mobile ios science nasa space data hp enterprise earth major could dns "
    "virtualization teachers strategic spending distribusion comets virtual universe."
]
y_test = ["sports",
          "art&photography",
          "beauty&fashion",
          "business&finance",
          "food",
          "health",
          "music",
          "science&technology"]

stopwords = ['by', 'the', 'for', 'of', 'new', 'to', 'with', 'is', 'at', 'and', 'in', 'this', 'out']


def argmax(lst):
    """Given a list of numbers, return the index of the biggest one."""
    return max(range(len(lst)), key=lst.__getitem__)


def perform_tests_with(clf, cv_test):
    """Perform some tests with the given classifier."""
    unknown_doc = "bla bla bla."
    blocks_doc0 = "is this a sentence? a paragraph?!who knows"
    blocks_doc1 = "these-are-words"
    multilabel_doc = x_test[0] + x_test[1]
    multilabel_labels = [y_test[0], y_test[1]]
    multilabel_idxs = [clf.get_category_index(y_test[0]),
                       clf.get_category_index(y_test[1])]
    new_cat = "bla"
    def_cat = "music"
    def_cat_idx = clf.get_category_index(def_cat)
    most_prob_cat = clf.get_most_probable_category()
    most_prob_cat_idx = clf.__get_most_probable_category__()

    # category names case-insensitiveness check
    assert clf.get_category_index("SpOrTs") == clf.get_category_index("sports")

    # predict
    y_pred = clf.predict(x_test)
    assert y_pred == y_test

    y_pred = clf.predict(x_test, labels=False)
    y_pred = [clf.get_category_name(ic) for ic in y_pred]
    assert y_pred == y_test

    y_pred = clf.predict([unknown_doc], def_cat=STR_UNKNOWN)
    assert y_pred[0] == STR_UNKNOWN_CATEGORY

    y_pred = clf.predict([unknown_doc], def_cat=STR_MOST_PROBABLE)
    assert y_pred[0] == most_prob_cat
    assert y_pred[0] == "science&technology"

    assert clf.predict([unknown_doc], def_cat=def_cat)[0] == def_cat

    # predict_proba
    y_pred = clf.predict_proba(x_test)
    assert y_test == [clf.get_category_name(argmax(cv)) for cv in y_pred]
    assert [round(p, 5) for p in y_pred[0]] == cv_test

    y_pred = clf.predict_proba([unknown_doc])
    assert y_pred[0] == [0] * len(clf.get_categories())

    # classify
    pred = clf.classify(unknown_doc, sort=False)
    assert pred == [0] * len(clf.get_categories())

    pred0 = clf.classify(x_test[0], sort=False)
    assert argmax(pred0) == clf.get_category_index(y_test[0])

    pred1 = clf.classify(x_test[0], sort=True)
    assert pred1[0][0] == clf.get_category_index(y_test[0])
    assert argmax(pred0) == pred1[0][0] and pred0[argmax(pred0)] == pred1[0][1]

    # classify_label
    assert clf.classify_label(x_test[0]) == y_test[0]
    assert clf.classify_label(x_test[0], labels=False) == clf.get_category_index(y_test[0])

    assert clf.classify_label(unknown_doc) == most_prob_cat
    assert clf.classify_label(unknown_doc, def_cat=STR_UNKNOWN) == STR_UNKNOWN_CATEGORY
    assert clf.classify_label(unknown_doc, def_cat=def_cat) == def_cat

    assert clf.classify_label(unknown_doc, labels=False) == most_prob_cat_idx
    assert clf.classify_label(unknown_doc, def_cat=STR_UNKNOWN, labels=False) == -1
    assert clf.classify_label(unknown_doc, def_cat=def_cat, labels=False) == def_cat_idx

    # classify_multilabel

    r = clf.classify_multilabel(multilabel_doc)
    assert len(multilabel_labels) == len(r)
    assert r[0] in multilabel_labels and r[1] in multilabel_labels
    r = clf.classify_multilabel(multilabel_doc, labels=False)
    assert len(multilabel_labels) == len(r)
    assert r[0] in multilabel_idxs and r[1] in multilabel_idxs

    assert clf.classify_multilabel(unknown_doc) == [most_prob_cat]
    assert clf.classify_multilabel(unknown_doc, def_cat=STR_UNKNOWN) == [pyss3.STR_UNKNOWN_CATEGORY]
    assert clf.classify_multilabel(unknown_doc, def_cat=def_cat) == [def_cat]

    assert clf.classify_multilabel(unknown_doc, labels=False) == [most_prob_cat_idx]
    assert clf.classify_multilabel(unknown_doc, def_cat=STR_UNKNOWN, labels=False) == [-1]
    assert clf.classify_multilabel(unknown_doc, def_cat=def_cat, labels=False) == [def_cat_idx]

    # "learn an unknown_doc and a new category" case
    clf.learn(unknown_doc * 2, new_cat, update=True)
    assert new_cat in clf.get_categories()
    y_pred = clf.predict([unknown_doc])
    assert y_pred[0] == new_cat

    # get_stopwords
    learned_stopwords = clf.get_stopwords(.01)
    assert [sw for sw in stopwords if sw in learned_stopwords] == stopwords

    # set_block_delimiters
    pred = clf.classify(blocks_doc0, json=True)
    assert len(pred["pars"]) == 1 and len(pred["pars"][0]["sents"]) == 1
    assert len(pred["pars"][0]["sents"][0]["words"]) == 8

    clf.set_block_delimiters(parag="!", sent=r"\?")
    pred = clf.classify(blocks_doc0, json=True)
    assert len(pred["pars"]) == 2 and len(pred["pars"][0]["sents"]) == 4
    clf.set_block_delimiters(sent=r"(\?)")
    assert len(pred["pars"][0]["sents"]) == 4

    clf.set_block_delimiters(word="-")
    pred = clf.classify(blocks_doc1, json=True)
    assert len(pred["pars"][0]["sents"][0]["words"]) == 3

    clf.set_block_delimiters(parag=PARA_DELTR, sent=SENT_DELTR, word=WORD_DELTR)


def test_pyss3_functions():
    """Test pyss3 functions."""
    assert pyss3.sigmoid(1, 0) == 0
    assert pyss3.sigmoid(1, 1) == .5
    assert pyss3.sigmoid(.2, .2) == .5
    assert pyss3.sigmoid(.5, .5) == .5
    assert round(pyss3.sigmoid(0, .5), 5) == .00247
    assert round(pyss3.sigmoid(1, .5), 5) == .99753
    assert round(pyss3.sigmoid(1, 2), 5) == .04743

    assert pyss3.mad([1, 1, 1], 3) == (1, .0)
    assert pyss3.mad([1, 1, 1], 3) == (1, .0)
    assert pyss3.mad([], 1) == (0, .0)
    assert round(pyss3.mad([1, 2, 1], 3)[1], 5) == .33333
    assert round(pyss3.mad([1, 10, 1], 3)[1], 5) == 3.0

    r = [(6, 8.1), (7, 5.6), (2, 5.5), (4, 1.5),
         (5, 1.3), (3, 1.2), (0, 1.1), (1, 0.4)]
    assert pyss3.kmean_multilabel_size(r) == 3
    with pytest.raises(ZeroDivisionError):
        pyss3.kmean_multilabel_size([(0, 0), (1, 0)])

    with pytest.raises(IndexError):
        pyss3.mad([], 0)


def test_pyss3_ss3():
    """Test SS3."""
    clf = SS3(
        s=.45, l=.5, p=1, a=0, name="test",
        cv_m=STR_NORM_GV_XAI, sn_m=STR_XAI
    )

    # "cold start" tests
    assert clf.get_name() == "test"
    assert clf.get_category_index("a_category") == IDX_UNKNOWN_CATEGORY
    assert clf.get_category_name(0) == STR_UNKNOWN_CATEGORY
    assert clf.get_category_name(-1) == STR_UNKNOWN_CATEGORY

    with pytest.raises(pyss3.EmptyModelError):
        clf.predict(x_test)
    with pytest.raises(pyss3.EmptyModelError):
        clf.predict_proba(x_test)

    # train and predict/classify tests (model: terms are single words)
    clf.fit(x_train, y_train)

    perform_tests_with(clf, [.00114, .00295, 0, 0, 0, .00016, .01894, 8.47741])

    # train and predict/classify tests (model: terms are word n-grams)
    clf = SS3(
        s=.32, l=1.24, p=1.1, a=0, name="test-3grams",
        cv_m=STR_NORM_GV_XAI, sn_m=STR_XAI
    )
    clf.fit(x_train, y_train, n_grams=3)

    perform_tests_with(clf, [.00074, .00124, 0, 0, 0, .00028, .00202, 9.19105])

    # n-gram recognition tests
    pred = clf.classify("android mobile and video games", json=True)
    assert pred["pars"][0]["sents"][0]["words"][0]["lexeme"] == "android mobile"
    assert pred["pars"][0]["sents"][0]["words"][-1]["lexeme"] == "video games"
    assert argmax(pred["cv"]) == clf.get_category_index("science&technology")
    assert [round(p, 5) for p in pred["cv"]] == [0, 0, 0, 0, 0, 0, 4.3789, 0, 0]

    pred = clf.classify("playing football soccer", json=True)
    assert pred["pars"][0]["sents"][0]["words"][-1]["lexeme"] == "football soccer"
    assert argmax(pred["cv"]) == clf.get_category_index("sports")
    assert [round(p, 5) for p in pred["cv"]] == [0, 0, 0, 0, 0, .53463, 0, 1.86708, 0]

    # load and save model tests
    clf.set_model_path("tests/")
    clf.save_model()
    clf.load_model()

    clf = SS3(name="test-3grams")

    with pytest.raises((OSError, IOError)):
        clf.set_model_path("dummy")
        clf.load_model()

    clf.set_model_path("./tests")
    clf.load_model()

    clf.set_model_path("tests/tmp")
    clf.save_model()
    clf.save_model()
    clf.load_model()

    clf.save_model("tests/")
    clf.load_model()

    clf = SS3(name="test-3grams")
    clf.load_model("./tests/")

    clf.save_model("./tests/tmp/")
    clf.save_model()
    clf.load_model()

    rmtree("./tests/tmp", ignore_errors=True)
    rmtree("./tests/ss3_models", ignore_errors=True)


# if __name__ == "__main__":
#     test_pyss3_ss3()
