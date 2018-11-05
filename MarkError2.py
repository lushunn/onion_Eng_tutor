'''
标错词汇标错
'''
class mark_error():
    def expansion(self,phrase):
        '''
        扩写缩写词
        :param phrase: str 原文本
        :return:str 扩写后文本
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


    def str_list(self,sentence):
        '''
        string文本转为小写单词组成list
        :param sentence:  str
        :return: list
        '''
        from re import split
        sentence=sentence.lower()
        strlist = split(" |!|\?|\.|,|:", self.expansion(sentence.strip()))
        strlist = list(filter(lambda x: x != '', strlist))
        return strlist

    def dot_upper_list(self,sentence):
        '''
        输出标记标点符号，和首字母大写单词的位置列表，用于打印标记错误单词后，还原标点符号和首字母大写
        :param sentence: str 原文本
        :return: list 错误单词位置标记list/首字母大写位置标记list
        '''
        from re import split
        strlist=split(" |!|\?|\.|,|:",self.expansion(sentence.strip()))
        dot_inx_list=[]#标点符号索引数组
        upper_inx_list=[]#大写数组
        for i, word in enumerate(strlist):
            if word == '':
                dot_inx_list.append(i)
            elif not word.islower():
                upper_inx_list.append(i)
        return dot_inx_list,upper_inx_list




    def commonSequence(self,TrueWordList,submitWordList):
        '''
        标记正确错误后的单词，输出二维nX2列表，每个元素为[],位置0为单词，位置1为标记，错误的标记为'red'，
        正确的标为'green'
        :param TrueWordList: list 原文本单词list
        :param submitWordList: list 提交文本单词list
        :return:list [['helle','red'],['hello','green']]
        '''
        if  not submitWordList:
            return list(map(lambda x:[x,'red'],TrueWordList))
        from collections import deque
        #生成动态规划二维数组，寻找最长公共子序列
        n, m = len(TrueWordList), len(submitWordList)
        dp = [[0 for j in range(m + 1)] for i in range(n + 1)]
        for i in range(1,n + 1):
            for j in range(1,m + 1):
                if TrueWordList[i - 1] == submitWordList[j - 1]:
                    dp[i][j] = 1 + dp[i - 1][j - 1]
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        if dp[-1][-1]==0:
            return list(map(lambda x:[x,'red'],TrueWordList))#若无公共子序列，全标红
        #在dp数组中，从右下角进行遍历，错误单词标记为'red'
        result = deque()
        x, y= len(TrueWordList), len(submitWordList)
        while x != 0 or y != 0:
            if dp[x][y] == dp[x - 1][y]:
                x -= 1
                result.appendleft([TrueWordList[x], 'red'])
            elif dp[x][y] == dp[x][y - 1]:
                y -= 1
            else:
                if TrueWordList[x - 1] == submitWordList[y - 1]:
                    result .appendleft([TrueWordList[x - 1],'green'])
                    x -= 1
                    y -= 1
        return list(result)


    def printerror(self,marklist,dot_inx_list,upper_inx_list):
        '''
        在原文本上进行标错打印
        :param marklist:标记错误后的list
        :param dot_inx_list: 标记标点位置的list
        :param upper_inx_listr_inx_list: 标记首字母大写位置的list
        :return: none
        '''
        res=[]
        for i in dot_inx_list:
            marklist.insert(i,'/')#标点符号同一记为'/'
        for  i in upper_inx_list:
            marklist[i][0]=marklist[i][0].title()
        for marktuple in marklist:
            if type(marktuple)==list:
                if marktuple[1] =='red':
                    res.append('<red>'+marktuple[0]+"<\\red>")
                else:
                    res.append(marktuple[0])
            else:
                res.append(marktuple[0])
        return ' '.join(res)
    def errorlist(self,marklist,dot_inx_list):
        '''
        将错误的单词/短句所在的原文句子用list包装
        :param marklist: 错误标记list
        :return: list
        '''
        for i in dot_inx_list:
            marklist.insert(i,'/')
        res=[]
        tmp = []
        for i in marklist:
            if i !='/':
                tmp.append(i)
            else:
                res.append(tmp)
                tmp=[]
        res1=[]
        tmp=''
        i=0
        while i<len(res):
            for j in res[i]:
                if j[1]=='red':
                    for inx in range(len(res[i])):
                        tmp+=' '+res[i][inx][0]
                    res1.append(tmp.strip())
                    tmp = ''
                    break
            i+=1



        return res1


    def fit(self,TrueWordstr,submitWordstr):
        '''
        打印错误
        :param TrueWordstr: 原文本
        :param submitWordstr: 提交文本
        :return: none
        '''
        dot_inx_t, upper_inx_t = self.dot_upper_list(TrueWordstr)
        submitWordlist = self.str_list(submitWordstr)
        TrueWordlist = self.str_list(TrueWordstr)
        marklist = self.commonSequence(TrueWordlist,submitWordlist)
        return self.printerror(marklist, dot_inx_t, upper_inx_t)

    def fit_list(self, TrueWordstr, submitWordstr):
        '''
        生成听力错误单词/断句所在的原文句子组成的list
        :param TrueWordstr: 原文本
        :param submitWordstr: 提交文本
        :return:
        '''
        dot_inx_t, _ = self.dot_upper_list(TrueWordstr)
        submitWordlist = self.str_list(submitWordstr)
        TrueWordlist = self.str_list(TrueWordstr)
        marklist = self.commonSequence(TrueWordlist, submitWordlist)
        return self.errorlist(marklist,dot_inx_t)
if __name__ == '__main__':
    #测试范例
    m=mark_error()
    testworda="Over the past few weeks, there's been a series of terrorist " \
              "attacks in the South Asian country of Afghanistan."
    testwordb="Over the past fqw weeks, there's bean a series of terrorist " \
              "attacks in the South Asian count og Afghanistan."
    print(m.fit( testworda,testwordb))
    #print(m.fit_list(testworda, testwordb))
    ##长度变换
    testworda="Over the past few weeks, there's been a series of terrorist " \
              "attacks in the South Asian country of Afghanistan."
    testwordb="series of terrorist " \
              "attacks in the South Asian country of Afghanistan."
    print(m.fit(testworda, testwordb))
    #print(m.fit_list(testworda, testwordb))