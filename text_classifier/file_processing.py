import tarfile
from django.core.files.storage import FileSystemStorage
import json

def add_save_my_session(key,val):
    try:
        with open('my_session/session.json', 'r') as file:
            data = json.load(file)
        data[key] = val
        with open('my_session/session.json', 'w+') as file:
            json.dump(data, file)
        return 0
    except:
        with open('my_session/session.json', 'w+') as file:
            json.dump({key:val}, file)
        return 0

def load_my_session(key):
    try:
        with open('my_session/session.json', 'r') as file:
            data = json.load(file)
        return data[key]
    except:
        return None


def count_labeled_examples(filename):
    try:
        counter = 0
        with open(filename, 'r', encoding='UTF-8') as destination:
            for line in destination:
                counter += 1
        return counter
    except:
        return None


def transfer_one_line(filename, sentence, label):
    try:
        counter = 0
        with open(filename, 'a+', encoding='UTF-8') as destination:
            line = str(label) + "\t" + str(sentence) + "\n"
            destination.write(line)
            counter += 1
        return counter
    except:
        return 0


def transfer_labeled_tsvfile(filename, f):
    try:
        counter = 0
        with open(filename, 'a+', encoding='UTF-8') as destination:
            for line in f:
                line = line.decode("UTF-8")
                # text = line.strip()
                destination.write(line)
                counter += 1
        return counter
    except Exception as e:
        print(e)
        return 0
