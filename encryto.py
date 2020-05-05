import random
import json

with open("en.json") as fp:
    boxs = json.load(fp)


def decode(index, data):
    box = boxs[index]
    ret = []
    for c in data:
        ret.append(box.index(c))
    return bytes(ret)


def encode(index, data):
    box = boxs[index]
    nd = []
    for c in data:
        nd.append(box[c])
    return bytes(nd)


def rand_index():
    return random.randint(0, len(boxs) - 1)
