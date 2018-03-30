"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""

"""
Trains SVM classifier to detect document type - lease or not lease.
"""
import os
import pickle

from sklearn import metrics
from sklearn.datasets import load_files
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.8/LICENSE"
__version__ = "1.0.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def load_lease_dataset(root):
    return load_files(root)


if __name__ == '__main__':
    root = os.path.expanduser('~/lexpredict/misc/lease')
    cache_dir = os.path.join(root, 'cache')
    cache_train = os.path.join(cache_dir, 'lease_train.pickle')
    cache_test = os.path.join(cache_dir, 'lease_test.pickle')

    script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    cache_model = os.path.join(script_dir, 'parsing/lease_doc_detector_svm_model.pickle')

    train_dataset = load_lease_dataset(os.path.join(root, 'train'))

    if not os.path.isfile(cache_model):
        if os.path.isfile(cache_train):
            print('Loading train dataset from cache')
            train_dataset = pickle.load(open(cache_train, 'rb'))
        else:
            print('Loading train dataset from files')
            train_dataset = load_lease_dataset(os.path.join(root, 'train'))
            pickle.dump(train_dataset, open(cache_train, 'wb'))

        print('Building model...')
        text_clf = Pipeline([('vect', CountVectorizer()),
                             ('tfidf', TfidfTransformer()),
                             ('clf', SGDClassifier(loss='hinge', penalty='l2',
                                                   alpha=1e-3, random_state=42,
                                                   max_iter=5, tol=None)),
                             ])
        model = text_clf.fit(train_dataset.data, train_dataset.target)
        pickle.dump(model, open(cache_model, 'wb'))
    else:
        print('Loading model from cache...')
        model = pickle.load(open(cache_model, 'rb'))

    if os.path.isfile(cache_test):
        print('Loading test dataset from cache')
        test_dataset = pickle.load(open(cache_test, 'rb'))
    else:
        print('Loading test dataset from files')
        test_dataset = load_lease_dataset(os.path.join(root, 'test'))
        pickle.dump(test_dataset, open(cache_test, 'wb'))

    print('Testing model on test data...    ')
    predicted = model.predict(test_dataset.data)
    print(metrics.classification_report(test_dataset.target, predicted,
                                        target_names=test_dataset.target_names))

    print(metrics.confusion_matrix(test_dataset.target, predicted))
