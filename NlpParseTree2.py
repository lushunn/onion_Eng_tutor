'''
  对每个本文的每个句子生成依存树，截取root词，以及依存树二三层的有效词（动词，名词，形容词，副词）标记为重点词
'''
from spacy import  load
# pip install spacy
# python -m spacy download en

nlp = load("en")
class MarkaImpWord():
    def expansion(self,phrase):
        '''
        将缩写词扩展
        :param phrase: str
        :return: str
        '''
        import re

        # specific
        phrase = re.sub(r"won't", "will not", phrase)
        phrase = re.sub(r"can\'t", "can not", phrase)

        # general
        phrase = re.sub(r"n\'t", " not", phrase)
        phrase = re.sub(r"\'re", " are", phrase)
        phrase = re.sub(r"\'s", " is", phrase)
        phrase = re.sub(r"\'d", " would", phrase)
        phrase = re.sub(r"\'ll", " will", phrase)
        phrase = re.sub(r"\'t", " not", phrase)
        phrase = re.sub(r"\'ve", " have", phrase)
        phrase = re.sub(r"\'m", " am", phrase)
        return phrase


    def StrTransform(self,sentence,tolist=False):
        '''
         将句子经过scapy.nlp预处理后sent组成列表，每个元素为scapy.nlp处理后的一个句子
         或输出str格式的单词组成的列表(tolist=true)
        :param sentence: string
        :return: list
        '''
        if tolist==True:
            sentence = sentence.lower()
            sentence = sentence.replace(',', ' ')
            sentence = sentence.replace('.', ' ')
            sentence = sentence.replace('!', ' ')
            sentence = sentence.replace('?', ' ')
            sentence = sentence.replace(':', ' ')
            sentence = sentence.replace('  ', ' ')
            return self.expansion(sentence.strip()).split(' ')
        else:
            tmp=[]
            for sent in nlp(self.expansion(sentence.strip())).sents:
                tmp.append(sent)
            return tmp

    def build_tree(self,doc):
        '''
        生成依存树，得出dict格式的树，以及root字符
        :param doc:spacy.tokens.span.Span
        :return:string,dict
        '''
        tmp = {}
        for i in doc:
            if str(i) in tmp:
                for j in list(i.children):
                    tmp[str(i).lower()].append(str(j).lower())
            else:
                tmp[str(i).lower()] = [str(m).lower() for m in list(i.children)]
        for i in doc:
            if i.head == i:
                rootw = str(i).lower()
        return tmp, rootw
    def markpos_(self,sent):
        '''
        标记词性
        :param sent: sent句子
        :return:  dict
        '''
        dic=dict()
        for i in sent:
            dic[str(i).lower()]=i.pos_
        return dic
    def markimp(self,doc):
        '''
        标记重点单词，过程为将文段的每个句子分别生成依存树，标记重点词
        :param doc: lsit
        :return set
        '''
        doc=self.StrTransform(doc)
        res = set()
        # for sent in doc:
        #     tmp,rootword=self.build_tree(sent)
        #     for i in tmp[rootword]:
        #         res.add(i)
        for sent in doc:
            tmp, rootword = self.build_tree(sent)
            res.add(rootword)
            dic = self.markpos_(sent)
            for i in tmp[rootword]:
                if dic[i] in ['ADJ','NOUN','ADV','VERB']:
                    res.add(i)
                for j in tmp[i]:
                    if dic[j] in ['ADJ','NOUN','ADV','VERB']:
                        res.add(j)
        return set(i for i in res if i.isalnum())
if __name__ == '__main__':
    #测试范例
    m = MarkaImpWord()
    testworda = "Over the past few weeks, there's been a series of terrorist " \
                "attacks in the South Asian country of Afghanistan."
    print(m.markimp(testworda))
