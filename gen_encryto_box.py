import random
import copy
import argparse
import json

origin = []

for i in range(256):
    origin.append(i)


def mkbox():
    box = []
    o = copy.deepcopy(origin)
    for i in range(256):
        index = random.randint(0, len(o) - 1)
        value = o[index]
        box.append(value)
        o.remove(value)
    return box


def get_options():
    parser = argparse.ArgumentParser(
        description=u"make encryto box")
    parser.add_argument("count", help=u"box count.default:1000", default=1000)
    parser.add_argument("filename", help=u"target file name.default:encryto.json",
                        default="encryto.json")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_options()
    boxs = []
    for i in range(int(args.count)):
        boxs.append(mkbox())
    with open(args.filename, 'w') as fp:
        json.dump(boxs, fp)
