import os
import codecs


TEST_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
TEST_RESOURCE_DIRECTORY = os.path.join(TEST_DIRECTORY, 'resources')


def load_resource_document(docname: str, encoding: str = 'ascii'):
    datapath = os.path.join(TEST_RESOURCE_DIRECTORY, 'documents/' + docname)
    with codecs.open(datapath, encoding=encoding, mode='r') as myfile:
        data = myfile.read()
    return data


def save_test_document(docname: str, text: str, encoding: str = 'utf-8'):
    savepath = os.path.join(TEST_RESOURCE_DIRECTORY, 'parsed/' + docname)
    with codecs.open(savepath, encoding=encoding, mode='w') as myfile:
        myfile.write(text)
