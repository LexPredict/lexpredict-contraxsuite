import os
import codecs


def load_resource_document(docname: str, encoding: str="ascii"):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    datapath = os.path.join(dir_path, "resources/documents/" + docname)
    with codecs.open(datapath, encoding=encoding, mode='r') as myfile:
        data = myfile.read()
    return data


def save_test_document(docname: str, text: str, encoding: str="utf-8"):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    savepath = os.path.join(dir_path, "resources/parsed/" + docname)
    with codecs.open(savepath, encoding=encoding, mode='w') as myfile:
        myfile.write(text)
