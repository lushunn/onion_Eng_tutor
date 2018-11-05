#Download the pre-built Mac application 'gentle',based on Kaldi https://github.com/lowerquality/gentle/releases/tag/0.10.1
#流程 txt+mp3->输出标准的强制对齐json文件
#markerror2.commonSequence得到带有标记是否错误信息的word list
#根据强制对齐json文件的信息和errorlist，输出错误部分所在的音频时间段
#对错误单词的音频时间段对应的音频进行变速和音量加大,错误句子额外插入1s静默时间
from pydub import AudioSegment#音频切分
class audio_change():
    def  transf_txt(self,inputpath,outputpath,txtfile):
        '''
        把听力文本转换为标准格式
        plain txt：按照aeneas说明文档，为每个句子或短语换行分割的txt文件
        :param inputpath:  string 输入路径
        :param outputpath: string 输出路径
        :param txtfile: string 输入txt文件名
        :return: None
        '''
        from MarkError2 import mark_error
        from re import split
        m=mark_error()
        assert txtfile[-3:] == 'txt', 'text file format error'
        file = inputpath+txtfile

        with open(file,encoding='UTF-8-sig') as f:
            f = f.read()
            f = f.replace('\ufeff', '')
            f=m.str_list(f)
            f='\n'.join(f)

        fh = open(outputpath+txtfile, 'w')#部分文本文件编码有问题
        fh.write(f)
        fh.close()

    def trans_dir_txt(self,path,outpath):
        '''
        对文件夹下的每一个txt原文本进行 transf_txt操作
        :param path:输入路径
        :param outpath:输出路径
        :return:None
        '''
        import os
        pathDir = os.listdir(path)
        for s in pathDir:
            newDir = os.path.join(path, s)
            if os.path.isfile(newDir):
                if os.path.splitext(newDir)[1] == ".txt":
                    self.transf_txt(path,outpath,s)
            else:
                pass



    def forced_align(self,inputpath,outputpath,audiofile,txtfile):
        '''
        强制对齐，输出json，默认txt和mp3在一个文件夹下
        :param inputpath: str
        :param outputpath: str
        :param audiofile: str
        :param txtfile:str
        :return: json
        '''
        import os
        assert  audiofile[-3:]=='mp3','mp3 file format error'
        assert txtfile[-3:] == 'txt', 'text file format error'

        audio= inputpath+audiofile
        txt= inputpath+txtfile

        os.system("curl" +" -F 'audio=@"+audio+"'"+" -F 'transcript=@"+txt+"'" +" 'http://localhost:8765/transcriptions?async=false'"+">"+outputpath+"tmp.json")
        os.chdir(outputpath)
        os.rename('tmp.json', audiofile[:-3] + 'json')




    def forced_align_dir_txt(self, path, outpath):
        '''
        对文件夹下的每一个plain txt格式的txt文本文件和mp3音频进行强制对齐操作
        默认txt和mp3在同一文件夹下，且同一听力txt对应mp3的文件前缀名相同
        :param path:输入路径
        :param outpath:输出路径
        :return:None
        '''
        import os
        pathDir = os.listdir(path)
        for s in pathDir:
            newDir = os.path.join(path, s)
            if os.path.isfile(newDir):
                if os.path.splitext(newDir)[1] == ".txt":
                    self.forced_align(path,outpath,s[:-4]+str('.mp3'),s)
                    print('输出强制对齐json'+'s'+'*****')
            else:
                pass

    def SentenctTime(self,errorlist,jsonfile):
        '''
        利用markerror2库生成的错误标记列表，和forced_align操作生成的json文件，输出错误音频段落的播放时刻
        :param errorlist: list
        :param jsonfile: str
        :return: list
        '''
       # input: errorlist->[['helle', 'red'], ['hello', 'green']]....
        #   output:[[1.12,1.33],[3.11,6.12]] 元素index0为错误起始时刻，index1为结束时刻
        import json
        with open(jsonfile) as f:
            fj=json.load(f)

        fragments=fj['words']
        errortime=[]

        for i in range(len(errorlist)):
            #针对语音识别存在标记失败问题，设定标记失败的单词对齐起始为前一个单词的对齐结束，对齐结束为后一个单词的对齐开始
            if fragments[i]['case']=='not-found-in-audio' and i-1>=0 and i+1<=(len(errorlist)-1):
                timeseg=[float(fragments[i-1]['end']),float(fragments[i+1]['start'])]

            elif  fragments[i]['case']=='success':
                timeseg=[float(fragments[i]['start']),float(fragments[i]['end'])]

            elif fragments[i]['case'] == 'not-found-in-audio' and i - 1 <0:
                timeseg = [float(0), float(fragments[i + 1]['start'])]

            elif fragments[i]['case'] == 'not-found-in-audio' and i + 1 >(len(errorlist)-1):
                timeseg = [float(fragments[i]['start']), 9999999.99]

            if errorlist[i][1]=='red':
                errortime.append(timeseg)

        errortime=sorted(errortime, key=lambda x: x[0])  # 按错误片段时间先后顺序排序

        #如果单词连续出错（后一个出错单词的起始和前一个出错单词的结束相隔不到0.3s），可认为是整个个句子出错，将对应错误时刻list的元素进行合并

        def u(x):
            #临时函数
            try:
                for i in range(1, len(x)):
                    if  x[i][0]-x[i - 1][1]<=0.3 and i <= len(x):
                        x[i - 1] = [x[i - 1][0], x[i][1]]
                        x.remove(x[i])
                        u(x)
            except IndexError as e:
                pass

        u(errortime)
        return errortime
    def speed_change(self,sound, speed=1.0):
        '''
        改变错误语音段的语速（设置为0.95，效果最佳）
        :param sound:pydub.audio_segment.AudioSegment
        :param speed:float
        :return:pydub.audio_segment.AudioSegment
        '''
        sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)
        })

        return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

    def jsonChangeaudio(self,errortime,audiofile,outputpath,):
        #针对错误片段进行音频处理，规则可更改
        '''
        :param errortime: 错误文本对应时间段组成的list
        :param audiofile:语音原文件
        :param outputpath:变化后的语音文件
        :return:
        '''
        song = AudioSegment.from_mp3(audiofile)
        startpart=song[:int(errortime[0][0]* 1000)]#秒转为毫秒
        miderrorpart=[]#错误片段
        midcorrpart = []#正确片段
        long_silence = AudioSegment.silent(duration=1500)
        short_silence = AudioSegment.silent(duration=900)
        for i in range(len(errortime)-1):
            miderrorpart.append(song[int(errortime[i][0]*1000):int(errortime[i][1]*1000)])
            midcorrpart.append(song[int(errortime[i][1]*1000):int(errortime[i+1][0]*1000)])
        miderrorpart.append(song[int(errortime[-1][0] * 1000):int(errortime[-1][1] * 1000)])
        endpart=song[int(errortime[-1][-1]* 1000):]

        miderrorpart = list(map(lambda x: x + 14.5, miderrorpart))  # 加大音量
        miderrorpart = list(map(lambda x: self.speed_change(x,0.95), miderrorpart))#放慢速度
        # 若出错片段大于0.1s,判断为句子，在错误片段处添加1s的静默时间
        miderrorpart = list(map(lambda x: long_silence+x if len(x)>1000 else short_silence+x, miderrorpart))

        for i in range(len(midcorrpart)):
            startpart+=miderrorpart[i]+midcorrpart[i]
        startpart+=miderrorpart[-1]
        res=startpart+endpart
        res.export(outputpath+audiofile.split('/')[-1], format="mp3")

if __name__ == '__main__':
    at=audio_change()
    #将原来音频文本转成plain txt
    #at.trans_dir_txt('/Users/guanghe/Documents/CNN/','/Users/guanghe/Documents/CNN/plain_txt/')
    #利用 plain txt 和mp3 生成语音和文本句子同步映射的json
    #at.forced_align_dir_txt('/Users/guanghe/Documents/CNN/plain_txt/', '/Users/guanghe/Documents/CNN/json/')
    from MarkError2 import mark_error
    m = mark_error()
    testworda = open('/Users/guanghe/Documents/CNN/test/原文本.txt').read().strip()
    testwordb = open('/Users/guanghe/Documents/CNN/test/测试文本.txt').read().strip()

    m.fit(testworda, testwordb)
    testworda = m.str_list(testworda)
    testwordb = m.str_list(testwordb)
    errorlist=m.commonSequence(testworda, testwordb)
    print(len(errorlist))
    #输出错误语句所在的句子在mp3音频中的时刻
    errortime=at.SentenctTime( errorlist, '/Users/guanghe/Documents/CNN/json/阿富汗一天多起爆炸袭击 ISIS认领首都爆炸案.json')

    print('错误语句所在音频时刻：' + str(errortime))

    at.jsonChangeaudio(errortime,'/Users/guanghe/Documents/CNN/阿富汗一天多起爆炸袭击 ISIS认领首都爆炸案.mp3',
                       '/Users/guanghe/Documents/CNN/changed_audio/')
