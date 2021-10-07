import json

from textdeps import TextWorker


def run():
    tw = TextWorker()
    with open('cat_desc.txt', 'r') as f:
        with open('cat_terms.pro', 'wt') as g:
            cats = []
            data = []
            for i, line in enumerate(f.readlines()):
                line = line[0:-1]
                if i % 2 == 0:
                    cat = line[3:5].lower()
                    cats.append(cat)
                    text = line[8:]
                    data.append(text)
                else:
                    data[-1] += (".  " + line)
            print(len(cats), len(data))
            d = dict(zip(cats, data))
            s = json.dumps(d, indent=2)
            # print(s)
            for cat, text in d.items():
                text=text.lower()
                tw.from_text(text)
                term=tw.as_term()
                xs = [cat, str(term)]
                args = ",".join(xs)
                print('desc(' + args + ').',file=g)


run()
