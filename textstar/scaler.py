import os
import subprocess
import glob
import sys
from multiprocessing import Pool, cpu_count

from nltk.tokenize import sent_tokenize, word_tokenize

from textstar import *


def out_dirs():
    out = 'out/'
    ensure_path(out + 'any')
    fs = [out + x for x in
          ('overview.txt',
           'pdftexts/',
           'sums/',
           'keys/'
           )
          ]

    for f in fs:
        ensure_path(f)
    return fs


def exists_file(fname):
    """ if it exists as file or dir"""
    return os.path.exists(fname)


def ensure_path(fname):
    folder, _ = os.path.split(fname)
    os.makedirs(folder, exist_ok=True)


def pdf2txt(pdf, txt):
    subprocess.run(["pdftotext", "-q", pdf, txt])
    if os.path.getsize(txt) > 32:
        return True
    os.remove(txt)
    return False


def file2string(fname):
    with open(fname, 'r') as f:
        return f.read()


def string2file(text, fname):
    with open(fname, 'w') as g:
        g.write(text)


def clean_text_file(fname, lang=None):
    # print('cleaning: '+fname)
    data = file2string(fname)
    if len(data) < 100:
        s = [x for x in data if x != ' ']
        if len(s) < 10:
            return False
    if lang is None:
        lang = detect_lang(data)
    if lang != 'en': return None
    texts = sent_tokenize(data)
    clean = []
    for text in texts:
        ws = word_tokenize(text)
        good = 0
        bad = 0
        if len(ws) > 256: continue
        for w in ws:
            if w.isalpha() and len(w) > 1:
                good += 1
            else:
                bad += 1
        if good / (1 + bad + good) < 0.75: continue
        if ws[-1] not in ".?!": ws.append(".")
        sent = " ".join(ws)
        clean.append(sent)
    new_data = "\n".join(clean)
    string2file(new_data, fname)
    return True


def walk(wdir="./"):
    for filename in sorted(set(glob.iglob(wdir + '**/**', recursive=True))):
        yield filename


def summarize_one(pdf, trim, texts, sums, keys, lang):
    """ summarizer for one document
    """
    if pdf[-4:].lower() != ".pdf": return None

    name = pdf[trim:-4]

    tname0 = texts + name
    tname = texts + name + ".txt"
    sname = sums + name + ".txt"
    kname = keys + name + ".txt"

    ensure_path(tname)
    try:
        print('START processing:', pdf)
        if not (pdf2txt(pdf, tname)):
            print('Unable to convert from PDF, skipping file!')
            return None
        clean_text_file(tname, lang=lang)

        sents, kws = summarize(tname0)
        sents = [sent for (_sid,sent) in sents]

        ktext = "\n".join(kws)
        ensure_path(kname)
        string2file(ktext, kname)

        stext = "\n".join(sents)
        ensure_path(sname)
        string2file(stext, sname)
        print('WRITTEN TO', sname, kname)

        text = "\n".join(
            ['FILE:', pdf, '\nSUMMARY:', stext, '\nKEYWORDS:', ktext, '\n'])
        print('DONE processing:', pdf)
        return text
    except IndexError:
        print('ERROR:', sys.exc_info()[0])
        print('Processing failed on:', pdf)
        return None
    except ValueError:
        return None
    except RuntimeError:
        return None
    except:
        return None


def summarize_all(
    rootdir=None,
    pdfs="../pdfs/",
    lang='en',
):
    """ sequential summarizer"""

    overview, texts, sums, keys = out_dirs()

    if rootdir:
        rootdir = os.path.abspath(rootdir) + "/"
        names = (pdfs, overview, texts, sums, keys)
        pdfs, overview, texts, sums, keys = tuple(rootdir + x for x in names)
    ensure_path(overview)
    with open(overview, 'w') as outf:
        trim = len(pdfs)
        for pdf in walk(wdir=pdfs):
            text = summarize_one(pdf, trim, texts, sums, keys, lang)
            if not text: continue
            print(text, file=outf)
            # print(text)
            # break


def sum_one(args):
    return summarize_one(*args)


def parsum_all(rootdir=None, pdfs="pdfs/", lang='en'):
    """ parallel summarizer"""

    overview, texts, sums, keys = out_dirs()

    if rootdir:
        rootdir = os.path.abspath(rootdir) + "/"
        names = (pdfs, overview, texts, sums, keys)
        pdfs, overview, texts, sums, keys = tuple(rootdir + x for x in names)

    count = max(2, cpu_count() // 3)
    with Pool(processes=count) as pool:
        trim = len(pdfs)
        fs = [pdf for pdf in walk(wdir=pdfs) if pdf[-4:].lower() == ".pdf"]
        pdf_count = len(fs)
        chunksize = 1  # max(1,int(l/(4*count)))
        print('pdf files:', pdf_count, 'processes:', count, 'chunksize:', chunksize)
        args = [(pdf, trim, texts, sums, keys, lang) for pdf in fs]
        ensure_path(overview)
        with open(overview, 'w') as outf:
            for text in pool.imap(sum_one, args, chunksize=chunksize):
                if text:
                    print(text, file=outf)


if __name__ == "__main__":
    print('MAKE SURE you have created  "pdfs/" directory with ".pdf" files in it')
    print('OR that you give the path of a directory where pdfs/ is a subdirectory')

    params = dict(
        # rootdir = "/Users/tarau/Desktop/sit/GRAPHSTAX/",
        # pdfs = "biblion/"
        # rootdir="/Users/tarau/Desktop/paps/",
        rootdir="/Users/tarau/Desktop/",
        pdfs="paps/"
        # rootdir = "/Users/tarau/Desktop/sit/MISC/",
        # pdfs="sienna2021/"

    )
    #summarize_all()
    # parsum_all()
    summarize_all(**params)

    # parsum_all(**params)
