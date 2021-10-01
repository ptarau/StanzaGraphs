import os
import pickle
from inspect import getframeinfo, stack
from timeit import default_timer as timer

PARAMS = dict(
    DATA_CACHE="./DATA_CACHE/",
    PICS="./PICS/",
    OUTPUT_DIRECTORY="./OUTPUT_DIRECTORY/"
)


def exists_file(fname):
    """ if it exists as file or dir"""
    return os.path.exists(fname)


def ensure_path(fname):
    folder, _ = os.path.split(fname)
    os.makedirs(folder, exist_ok=True)


def to_pickle(obj,fname):
    """
    serializes an object to a .pickle file
    """
    ensure_path(fname)
    with open(fname, "wb") as outf:
        pickle.dump(obj, outf)


def from_pickle(fname):
    """
    deserializes an object from a pickle file
    """
    with open(fname, "rb") as inf:
        return pickle.load(inf)


def take(n, gen):
    for i, x in enumerate(gen):
        if i >= n: break
        yield x


def ppp(*args, trace=1, **kwargs):
    """
    logging mechanism with possible DEBUG extras
    will tell from which line in which file the printed
    messge orginates from
    """

    if trace:
        caller = getframeinfo(stack()[1][0])
        print('DEBUG:',
              caller.filename.split('/')[-1],
              '->', caller.lineno, end=': ')
    print(*args, **kwargs)
