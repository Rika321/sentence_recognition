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
        label_set = set()
        counter = 0
        with open(filename, 'r', encoding='UTF-8') as destination:
            for line in destination:
                texts = line.strip().split("\t")
                label, info = texts[0], texts[1]
                label_set.add(label)
                counter += 1
        return counter, list(label_set)
    except:
        return None, []


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
        label_set = set()
        counter = 0
        with open(filename, 'w+', encoding='UTF-8') as destination:
            for line in f:
                line = line.decode("UTF-8")
                texts = line.strip().split("\t")
                label, info = texts[0], texts[1]
                if len(label_set)==2 and label not in label_set:
                    #more than 2 label
                    continue
                else:
                    label_set.add(label)
                destination.write(str(label)+"\t"+str(info)+"\n")
                counter += 1
        if len(label_set)==1:
            destination.write("UNK"+"\t"+"food is good"+"\n")
            label_set.add("UNK")
        return counter, sorted(list(label_set))
    except Exception as e:
        print(e)
        return 0, None


def transfer_stream(fs):
    data = []
    labels = []
    for line in fs:
        try:
            line = line.decode("UTF-8")
            (label,text) = line.strip().split("\t")
            labels.append(label)
            data.append(text)
        except:
            print(line)
    return data, labels
