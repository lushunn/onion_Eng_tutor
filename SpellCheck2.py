'''
单词拼写检测
'''
class SpellCheck():
    def BuildTrie(self,words):
        '''
        将单词构造trie
        :param words:list
        :return:dict
        '''
        trie = {}
        for word in words:
            t = trie
            for c in word:
                if c not in t: t[c] = {}
                t = t[c]
            t[None] = None
        return trie

    def FindErrorWord(self,TrueWordList,submitWordList):
        '''
        找出错词(提交的本文中包含的原文本不含有的单词)，并过滤掉单词长度小于等于1的词
        :param TrueWordList: list
        :param submitWordList: list
        :return: list
        '''
        ErrorSet=set(submitWordList)-set(TrueWordList)
        return list(filter(lambda x:len(x)>2,ErrorSet))

    def check(self,trie, word, path='', tol=1):
        '''
        查找错词中真正的拼错词,即字母拼错数为tol的单词，返回可能的修正结果，
        :param trie: dict 原文本构造的Trie
        :param word: 提交单词
        :param path: 记录搜索的单词
        :param tol: 单词拼错字母数，默认为1
        :return: set 可能正确的单词set
        '''
        if tol < 0:
            return set()
        elif word == '':
            results = set()
            if None in trie:
                results.add(path)
            for k in trie:
                if k is not None:
                    results |= self.check(trie[k], '', path+k, tol-1)
            return results
        else:
            results = set()
            if word[0] in trie:
                results |= self.check(trie[word[0]], word[1:], path + word[0], tol)
            for k in trie:
                if k is not None and k != word[0]:
                    results |= self.check(trie[k], word[1:], path+k, tol-1)
                    results |= self.check(trie[k], word, path+k, tol-1)
            results |= self.check(trie, word[1:], path, tol-1)
            if len(word) > 1:
                results |= self.check(trie, word[1]+word[0]+word[2:], path, tol-1)
            return results

    def CorrectStr(self,TrueWordList,submitWordList,tol=1):
        '''
        更正提交文本中的拼错词，输出改正后的错词和由于拼错词减去的分#拼错一个扣去0.5
        :param TrueWordList: list
        :param submitWordList: list
        :param tol: int
        :return: list，float
        '''
        t = self.BuildTrie(TrueWordList)
        errorlist = self.FindErrorWord(TrueWordList, submitWordList)
        res=['']*len(submitWordList)
        count=0
        for i in range(len(submitWordList)):
            if submitWordList[i] in errorlist:
                tmp = self.check(t, submitWordList[i], tol=tol)
                if tmp:
                    res[i]=tmp.pop()
                    count+=0.5
                else:
                    res[i]=submitWordList[i]
            else:
                res[i]=submitWordList[i]

        return res,count