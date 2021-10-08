# Data cleaning about the data in F-VQA / ZS-F-VQA
##
from calamus import fields
from calamus.schema import JsonLDSchema
import os.path as osp
import pickle
import os
import sys
import json
import re
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
class Dictionary(object):
    def __init__(self, word2idx=None, idx2word=None):
        if word2idx is None:
            word2idx = {}
        if idx2word is None:
            idx2word = []
        self.word2idx = word2idx
        self.idx2word = idx2word

    @property
    def ntoken(self):
        return len(self.word2idx)

    @property
    def padding_idx(self):
        return len(self.word2idx)

    def tokenize(self, sentence, add_word):
        sentence = sentence.lower()
        sentence = sentence.replace(',', '').replace('?', '').replace('\'s', ' \'s')
        words = sentence.split()
        tokens = []
        if add_word:
            for w in words:
                tokens.append(self.add_word(w))
        else:
            for w in words:
                tokens.append(self.word2idx[w])
        return tokens

    def dump_to_file(self, path):
        pickle.dump([self.word2idx, self.idx2word], open(path, 'wb'))
        print('dictionary dumped to %s' % path)

    @classmethod
    def load_from_file(cls, path):
        print('loading dictionary from %s' % path)
        word2idx, idx2word = pickle.load(open(path, 'rb'))
        d = cls(word2idx, idx2word)
        return d

    def add_word(self, word):
        if word not in self.word2idx:
            self.idx2word.append(word)
            self.word2idx[word] = len(self.idx2word) - 1
        return self.word2idx[word]

    def __len__(self):
        return len(self.idx2word)

contractions = {
    "aint": "ain't", "arent": "aren't", "cant": "can't", "couldve":
    "could've", "couldnt": "couldn't", "couldn'tve": "couldn't've",
    "couldnt've": "couldn't've", "didnt": "didn't", "doesnt":
    "doesn't", "dont": "don't", "hadnt": "hadn't", "hadnt've":
    "hadn't've", "hadn'tve": "hadn't've", "hasnt": "hasn't", "havent":
    "haven't", "hed": "he'd", "hed've": "he'd've", "he'dve":
    "he'd've", "hes": "he's", "howd": "how'd", "howll": "how'll",
    "hows": "how's", "Id've": "I'd've", "I'dve": "I'd've", "Im":
    "I'm", "Ive": "I've", "isnt": "isn't", "itd": "it'd", "itd've":
    "it'd've", "it'dve": "it'd've", "itll": "it'll", "let's": "let's",
    "maam": "ma'am", "mightnt": "mightn't", "mightnt've":
    "mightn't've", "mightn'tve": "mightn't've", "mightve": "might've",
    "mustnt": "mustn't", "mustve": "must've", "neednt": "needn't",
    "notve": "not've", "oclock": "o'clock", "oughtnt": "oughtn't",
    "ow's'at": "'ow's'at", "'ows'at": "'ow's'at", "'ow'sat":
    "'ow's'at", "shant": "shan't", "shed've": "she'd've", "she'dve":
    "she'd've", "she's": "she's", "shouldve": "should've", "shouldnt":
    "shouldn't", "shouldnt've": "shouldn't've", "shouldn'tve":
    "shouldn't've", "somebody'd": "somebodyd", "somebodyd've":
    "somebody'd've", "somebody'dve": "somebody'd've", "somebodyll":
    "somebody'll", "somebodys": "somebody's", "someoned": "someone'd",
    "someoned've": "someone'd've", "someone'dve": "someone'd've",
    "someonell": "someone'll", "someones": "someone's", "somethingd":
    "something'd", "somethingd've": "something'd've", "something'dve":
    "something'd've", "somethingll": "something'll", "thats":
    "that's", "thered": "there'd", "thered've": "there'd've",
    "there'dve": "there'd've", "therere": "there're", "theres":
    "there's", "theyd": "they'd", "theyd've": "they'd've", "they'dve":
    "they'd've", "theyll": "they'll", "theyre": "they're", "theyve":
    "they've", "twas": "'twas", "wasnt": "wasn't", "wed've":
    "we'd've", "we'dve": "we'd've", "weve": "we've", "werent":
    "weren't", "whatll": "what'll", "whatre": "what're", "whats":
    "what's", "whatve": "what've", "whens": "when's", "whered":
    "where'd", "wheres": "where's", "whereve": "where've", "whod":
    "who'd", "whod've": "who'd've", "who'dve": "who'd've", "wholl":
    "who'll", "whos": "who's", "whove": "who've", "whyll": "why'll",
    "whyre": "why're", "whys": "why's", "wont": "won't", "wouldve":
    "would've", "wouldnt": "wouldn't", "wouldnt've": "wouldn't've",
    "wouldn'tve": "wouldn't've", "yall": "y'all", "yall'll":
    "y'all'll", "y'allll": "y'all'll", "yall'd've": "y'all'd've",
    "y'alld've": "y'all'd've", "y'all'dve": "y'all'd've", "youd":
    "you'd", "youd've": "you'd've", "you'dve": "you'd've", "youll":
    "you'll", "youre": "you're", "youve": "you've"
}

manual_map = { 'none': '0',
              'zero': '0',
              'one': '1',
              'two': '2',
              'three': '3',
              'four': '4',
              'five': '5',
              'six': '6',
              'seven': '7',
              'eight': '8',
               'nine': '9',
              'ten': '10'}
articles = ['a', 'an', 'the']
period_strip = re.compile("(?!<=\d)(\.)(?!\d)")
comma_strip = re.compile("(\d)(\,)(\d)")
punct = [';', r"/", '[', ']', '"', '{', '}',
                '(', ')', '=', '+', '\\', '_', '-',
                '>', '<', '@', '`', ',', '?', '!']


def get_score(occurences):
    if occurences == 0:
        return 0
    elif occurences == 1:
        return 0.3
    elif occurences == 2:
        return 0.6
    elif occurences == 3:
        return 0.9
    else:
        return 1


def process_punctuation(inText):
    outText = inText
    for p in punct:
        if (p + ' ' in inText or ' ' + p in inText) \
           or (re.search(comma_strip, inText) != None):
            outText = outText.replace(p, '')
        else:
            outText = outText.replace(p, ' ')
    outText = period_strip.sub("", outText, re.UNICODE)
    return outText


def process_digit_article(inText):
    outText = []
    tempText = inText.lower().split()
    for word in tempText:
        word = manual_map.setdefault(word, word)
        if word not in articles:
            outText.append(word)
        else:
            pass
    for wordId, word in enumerate(outText):
        if word in contractions:
            outText[wordId] = contractions[word]
    outText = ' '.join(outText)
    return outText


def multiple_replace(text, wordDict):
    for key in wordDict:
        text = text.replace(key, wordDict[key])
    return text


def preprocess_answer(answer):
    answer = process_digit_article(process_punctuation(answer))
    answer = answer.replace(',', '')
    return answer


def filter_answers(dic_all, min_occurence):
    """This will change the answer to preprocessed version
    """
    occurence = {}
    entity = dict()
    relation = dict()
    triples = dict()

    for i, key in enumerate(dic_all.keys()):
        fact = dic_all[key]
        fact['KB'] = preprocess_answer(fact['KB'])
        fact['head'] = preprocess_answer(fact['head'])
        fact['relation'] = preprocess_answer(fact['relation'])
        fact['tail'] = preprocess_answer(fact['tail'])
        if fact['head'] not in entity.keys():
            entity[fact['head']] = 1
        else:
            entity[fact['head']] += 1
        if fact['tail'] not in entity.keys():
            entity[fact['tail']] = 1
        else:
            entity[fact['tail']] += 1
        if fact['relation'] not in relation.keys():
            relation[fact['relation']] = 1
        else:
            relation[fact['relation']] += 1
        if (fact['head'], fact['relation'], fact['tail']) not in triples.keys():
            triples[(fact['head'], fact['relation'], fact['tail'])] = 1
    # for i in relation.keys():
    #     print(i, relation[i])
    relation_all_sorted = dict(sorted(relation.items(), key=lambda relation: relation[1], reverse=True))
    with open(os.path.join('Data result distribution', "relation_all_sorted.json"), 'w') as fd:
        json.dump(relation_all_sorted, fd)

    relation_first100 = dict()
    for i,key in enumerate(relation_all_sorted.keys()):
        if i < 100:
            relation_first100[key] = relation_all_sorted[key]
        else:
            break

    # # draw relation 分布图
    x = np.arange(len(list(relation_first100.keys())))  # the label locations
    width = 1  # the width of the bars
    fig, ax1 = plt.subplots()
    rects3 = ax1.bar(x, list(relation_first100.values()), width, label='number', edgecolor='white', color='#d99583', zorder=100)
    ax1.set_ylabel('number', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(list(relation_first100.keys()), fontweight='bold', fontsize=4 , rotation=315)
    ax1.set_ylim((0, 80000))
    ax1.grid(axis='y', linestyle=":", zorder=0)
    fig.tight_layout()
    fig.savefig(os.path.join('Data result distribution', "relation_first20.png"))
    # plt.show()

    entity_all_sorted = dict(sorted(entity.items(), key=lambda entity: entity[1], reverse=True))
    with open(os.path.join('Data result distribution', "entity_all_sorted.json"), 'w') as fd:
        json.dump(entity_all_sorted, fd)

    entity_first100 = dict()
    for i, key in enumerate(entity_all_sorted.keys()):
        if i < 100:
            entity_first100[key] = entity_all_sorted[key]
        else:
            break

    # draw entity 分布图
    x = np.arange(len(list(entity_first100.keys())))  # the label locations
    width = 1  # the width of the bars
    fig, ax1 = plt.subplots()
    rects3 = ax1.bar(x, list(entity_first100.values()), width, label='number', edgecolor='white', color='#d99583', zorder=100)
    ax1.set_ylabel('number', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(list(entity_first100.keys()), fontweight='bold', fontsize=4, rotation=315)
    ax1.set_ylim((0, 14000))
    ax1.grid(axis='y', linestyle=":", zorder=0)
    fig.tight_layout()
    fig.savefig(os.path.join('Data result distribution', "entity_first20.png"))
    # plt.show()

    return dic_all, entity, relation, triples

    # for ans_entry in answers_dset:
    #     answers = ans_entry['answers']
    #     gtruths = list(set([ans["answer"] for ans in answers]))
    #     for gtruth in gtruths:
    #         gtruth = preprocess_answer(gtruth)
    #         if gtruth not in occurence:
    #             occurence[gtruth] = set()
    #         occurence[gtruth].add(ans_entry['question_id'])
    #
    # for answer in list(occurence.keys()):
    #     if len(occurence[answer]) < min_occurence:
    #         occurence.pop(answer)
    #
    # print('Num of answers that appear >= %d times: %d' % (
    #     min_occurence, len(occurence)))
    # return occurence

class Knowledge:
    def __init__(self, _id, name, KB, head, relation, tail):
        self._id = _id
        self.name = name
        self.KB = KB
        self.head = head
        self.relation = relation
        self.tail = tail

schema = fields.Namespace("http://schema.org/")

class KnowledgeSchema(JsonLDSchema):
    _id = fields.Id()
    name = fields.String(schema.name)
    KB = fields.String(schema.KB)
    head = fields.String(schema.head)
    relation = fields.String(schema.relation)
    tail = fields.String(schema.tail)

    class Meta:
        rdf_type = schema.Knowledge
        model = Knowledge

def deal_fact(dic, fact):
    fact = fact.split('/')
    if fact[-1] == "n" or fact[-1] == "v":
        ans = fact[-2]
    else:
        ans = fact[-1]

    ans = ans.split(':')
    if ans[0] == "Category":
        ans = ans[1]
    else:
        ans = ans[0]

    # if ans[-1] == ")":
    #     # ans = ans.split("(")[0]
    #     pdb.set_trace()
    #     ans = dic["answer"]
    return ans


# 将原来fvqa的数据集的json格式的/m/n等格式进行处理，生成一个新的json文件（类似新的知识库）
def get_new_all_json():
    print("start deal json,delete unnecessary!")
    path = "all_qs_dict_release_combine_all.json"
    if not osp.exists(path):
        with open("all_fact_triples_release.json", "r", encoding='utf8') as ffp:
            dic_all = json.load(ffp)
            for i in dic_all.keys():
                # fact_source = dic[i]["fact"][0]
                fact = dic_all[i]
                fact['e1'] = deal_fact(dic_all[i], fact['e1'])
                fact['e2'] = deal_fact(dic_all[i], fact['e2'])
                fact['r'] = fact['r'].split('/')[-1]
                fact['uri'] = 'nothing'
                fact['dataset'] = 'nothing'
                fact['sources'] = 'nothing'
                fact['context'] = 'nothing'
                # add triples
                # dic_all[i]["fact"] = []
                # dic_all[i]["fact"].append(fact['e1'])
                # dic_all[i]["fact"].append(fact['r'])
                # dic_all[i]["fact"].append(fact['e2'])
                dic_all[i]['head'] = fact['e1']
                dic_all[i]['relation'] = fact['r']
                dic_all[i]['tail'] = fact['e2']

                # stupid operation to deal run bug
                fact['uri'] = 'nothing'
                fact['dataset'] = 'nothing'
                fact['sources'] = 'nothing'
                fact['context'] = 'nothing'

                # 留下知识库中有用的，这里留下了kb和fact三元组信息
                # del dic_all[i]['KB']
                del dic_all[i]['e1_label']
                del dic_all[i]['e2_label']
                del dic_all[i]['uri']
                del dic_all[i]['surface']
                del dic_all[i]['dataset']
                del dic_all[i]['sources']
                del dic_all[i]['context']
                del dic_all[i]['score']
                del dic_all[i]['r']
                del dic_all[i]['e1']
                del dic_all[i]['e2']

        with open(path, 'w') as fd:
            json.dump(dic_all, fd)
            print("get_new_json_combile done!（remember to do some human check !!!）")
    print("finish!")
    # else:
    #     # 需要人工去噪

# do some human check,clear dirty data
def human_check():
    print("start human check!")
    with open("all_qs_dict_release_combine_all.json", "r", encoding='utf8') as ffp:
        dic_all = json.load(ffp)
        dic_all, entity, relation, triples = filter_answers(dic_all, 1)
        print("finished")
        print("num of entity:", len(entity))
        print("num of relation:", len(relation))
        print("nun of triples:", len(triples))
        with open("json_afterclear.json", 'w') as fd:
            json.dump(dic_all, fd)

    with open(os.path.join('data', 'okvqa', "trainval_ans2label_okvqa.json") , "r", encoding='utf8') as fp:
        dic_ans = json.load(fp)
        ans_in = 0
        for answer in dic_ans.keys():
            if (answer in entity) or (answer in relation):
                ans_in = ans_in + 1
        print("出现在知识库中的ans个数 ｜ okvqa中的ans个数：", ans_in, '|', len(dic_ans.keys()))

    with open(os.path.join('data', 'vqa2.0', "trainval_ans2label.json"), "r", encoding='utf8') as fp:
        dic_ans = json.load(fp)
        ans_in = 0
        for answer in dic_ans.keys():
            if (answer in entity) or (answer in relation):
                ans_in = ans_in + 1
        print("出现在知识库中的ans个数 ｜ vqa2.0 ans个数：", ans_in, '|', len(dic_ans.keys()))

    with open(os.path.join('data', 'okvqa', "trainval_ans2label_okvqa_occ3.json"), "r", encoding='utf8') as fp:
        dic_ans = json.load(fp)
        ans_in = 0
        for answer in dic_ans.keys():
            if (answer in entity) or (answer in relation):
                ans_in = ans_in + 1
        print("出现在知识库中的ans个数 ｜ okvqa occ3中的ans个数：", ans_in, '|', len(dic_ans.keys()))

    with open(os.path.join('data', 'fvqa', "trainval_ans2label_fvqa.json"), "r", encoding='utf8') as fp:
        dic_ans = json.load(fp)
        ans_in = 0
        for answer in dic_ans.keys():
            if (answer in entity) or (answer in relation):
                ans_in = ans_in + 1
        print("出现在知识库中的ans个数 ｜ fvqa中的ans个数：", ans_in, '|', len(dic_ans.keys()))

    with open(os.path.join('data', 'fvqa', "trainval_ans2label_fvqa1.json"), "r", encoding='utf8') as fp:
        dic_ans = json.load(fp)
        ans_in = 0
        for answer in dic_ans.keys():
            if (answer in entity) or (answer in relation):
                ans_in = ans_in + 1
        print("出现在知识库中的ans个数 ｜ fvqa1中的ans个数：", ans_in, '|', len(dic_ans.keys()))

    with open(os.path.join('data', 'fvqa', "trainval_ans2label_fvqa2.json"), "r", encoding='utf8') as fp:
        dic_ans = json.load(fp)
        ans_in = 0
        for answer in dic_ans.keys():
            if (answer in entity) or (answer in relation):
                ans_in = ans_in + 1
        print("出现在知识库中的ans个数 ｜ fvqa2中的ans个数：", ans_in, '|', len(dic_ans.keys()))

    with open(os.path.join('data', 'fvqa', "trainval_ans2label_fvqa3.json"), "r", encoding='utf8') as fp:
        dic_ans = json.load(fp)
        ans_in = 0
        for answer in dic_ans.keys():
            if (answer in entity) or (answer in relation):
                ans_in = ans_in + 1
        print("出现在知识库中的ans个数 ｜ fvqa3中的ans个数：", ans_in, '|', len(dic_ans.keys()))

    with open(os.path.join('data', 'fvqa', "trainval_ans2label_fvqa4.json"), "r", encoding='utf8') as fp:
        dic_ans = json.load(fp)
        ans_in = 0
        for answer in dic_ans.keys():
            if (answer in entity) or (answer in relation):
                ans_in = ans_in + 1
        print("出现在知识库中的ans个数 ｜ fvqa4中的ans个数：", ans_in, '|', len(dic_ans.keys()))


# 将json的知识库转成预先设定好的组织形式（jsondl或rdf）的知识库
def convert_json2jsondl():
    with open("json_afterclear.json", "r", encoding='utf8') as ffp:
        dic_all = json.load(ffp)
        dic_new = list()
        for i, key in enumerate(dic_all.keys()):
            fact = dic_all[key]
            # pdb.set_trace()
            id = "http://example.com/knowledge/" + str(i)
            name = key
            KB = fact['KB']
            head = fact['head']
            relation = fact['relation']
            tail = fact['tail']
            knowledge = Knowledge(_id=id, name=name, KB=KB, head=head, relation=relation, tail=tail)
            jsonld_dict = KnowledgeSchema().dump(knowledge)
            dic_new.append(jsonld_dict)
            # pdb.set_trace()
    with open("jsondl_knowledgebase.json", 'w') as fd:
        json.dump(dic_new, fd)


if __name__ == '__main__':
    get_new_all_json()

    human_check()

    convert_json2jsondl()

