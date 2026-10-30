import re
import numpy as np
from collections import defaultdict

def markov(text, o = 1, sentence_count = 1):
    assert o in [1, 2], "order must be 1 or 2"
    assert isinstance(sentence_count, int) and sentence_count > 0, "sentence count must be a natural number"

    text = text.lower()
    tokens = re.findall(r"(?:mrs|mr|ms|dr|st)\.|'?\w+(?:['-]\w+)*|[.,?;:!]", ". " + text)

    assert len(tokens) > 1 and tokens[1] not in [".", ",", "?", ";", ":", "!"], "text must have a word" 
    assert tokens[-1] in [".", "?", "!"], "text must end with closing punctuation"

    order_one_list = list(dict.fromkeys(tokens))
    order_one_dict = dict(zip(order_one_list, range(len(order_one_list))))
    stops = [order_one_dict["."]]
    if "?" in order_one_list:
        stops.append(order_one_dict["?"])
    if "!" in order_one_list:
        stops.append(order_one_dict["!"])
    semicolon = []
    if ";" in order_one_list:
	    semicolon.append(order_one_dict[";"])

    tokens_int = np.array([order_one_dict[token] for token in tokens], dtype = np.int32)

    order_one_t = defaultdict(lambda: defaultdict(int))
    order_one_t[tokens_int[0]][tokens_int[1]] = 1
    order_one_tm = {}

    if o == 2:
        order_two_t = defaultdict(lambda: defaultdict(int))
        order_two_tm = {}

        for prev, curr, succ in zip(tokens_int, tokens_int[1:], tokens_int[2:]):
            order_one_t[curr][succ] += 1
            order_two_t[(prev, curr)][succ] += 1

    else:
        for prev, curr in zip(tokens_int[1:], tokens_int[2:]):
            order_one_t[prev][curr] += 1

    for curr, succs in order_one_t.items():
        succs_list = list(succs)
        transitions = np.array([succs[s] for s in succs_list], dtype = np.float32)
        order_one_tm[curr] = (succs_list, transitions / transitions.sum())

    if o == 2:
        for curr, succs in order_two_t.items():
            succs_list = list(succs)
            transitions = np.array([succs[s] for s in succs_list], dtype = np.float32)
            order_two_tm[curr] = (succs_list, transitions / transitions.sum())

    prev = 0 # .
    succs, ps = order_one_tm[prev]
    curr = succs[np.random.default_rng().choice(len(succs), p = ps)]

    sentences = [curr]
    sentence_count = int(sentence_count)

    while sentence_count:
        if o == 1 or curr in stops or curr in semicolon:
            succs, ps = order_one_tm[curr]
        else:
            succs, ps = order_two_tm[(prev, curr)]
        prev = curr
        curr = succs[np.random.default_rng().choice(len(succs), p = ps)]
        sentences.append(curr)
        if curr in stops:
            sentence_count -= 1

    sentences = list(map(lambda m: order_one_list[m], sentences))

    sentences_str = sentences[0]

    for token in sentences[1:]:
        if token in [".", "?", ",", ";", "!", ":"]:
            sentences_str += token
        else:
            sentences_str += " " + token

    print(sentences_str)

with open("markov.txt", "r") as file:
    text = file.read()
    markov(text)
