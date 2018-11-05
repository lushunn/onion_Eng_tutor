from aeneas.executetask import ExecuteTask
from aeneas.task import Task
#用于音频文本同步映射
#依赖：brew install FFmpeg,eSpeak
#pip install aeneas
from pydub import AudioSegment
#pydub用于音频分割，处理
class Audio_tech():
    def  transfplaintxt(self,inputpath,outputpath,txtfile):
        '''
        把听力文本转换为plain txt
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
        with open(file) as f:
            f = f.read()
            f=m.str_list(f)
            f='\n'.join(f)
        fh = open(outputpath+txtfile, 'w', encoding='UTF-8-sig')#部分文本文件编码有问题
        fh.write(f)
        fh.close()

    def transfeachFile(self,path,outpath):
        '''
        对文件夹下的每一个txt原文本进行transfplaintxt操作
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
                    self.transfplaintxt(path,outpath,s)
            else:
                pass



    def Synch_audio(self,inputpath,outputpath,audiofile,txtfile):

        assert  audiofile[-3:]=='mp3','mp3 file format error'
        assert txtfile[-3:] == 'txt', 'text file format error'
        config_string = u"task_language=eng|is_text_type=plain|os_task_file_format=json|words-multilevel|presets-word"
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = inputpath+audiofile
        task.text_file_path_absolute = inputpath+txtfile
        task.sync_map_file_path_absolute = outputpath+audiofile.split('.')[0]+".json"
        ExecuteTask(task).execute()
        print("output json file: "+audiofile[:-4])
        task.output_sync_map_file()

    def Synch_audio_feachFile(self, path, outpath):
        '''
        对文件夹下的每一个plain txt格式的txt文本文件和mp3音频进行Synch_audio操作
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
                    self.Synch_audio(path,outpath,s[:-4]+str('.mp3'),s)
            else:
                pass

    def SentenctTime(self,errorlist,jsonfile):
       # input: [['helle', 'red'], ['hello', 'green']]
        import json
        with open(jsonfile) as f:
            fj=json.load(f)
        fragments=fj['fragments']
        errortime=[]
        for i in range(len(errorlist)):
            timeseg=[float(fragments[i]['begin']),float(fragments[i]['end'])]
            if errorlist[i][1]=='red':
                errortime.append(timeseg)
        errortime=sorted(errortime, key=lambda x: x[0])  # 按错误片段时间先后顺序排序
        def u(x):
            try:
                for i in range(1, len(x)):
                    if x[i - 1][1] == x[i][0] and i <= len(x):
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
        '''
        :param errortime: 错误文本对应时间段组成的list
        :param audiofile:语音原文件
        :param outputpath:变化后的语音文件
        :return:
        '''
        song = AudioSegment.from_mp3(audiofile)
        startpart=song[:int(errortime[0][0]* 1000)]#秒转为毫秒
        miderrorpart=[]
        midcorrpart = []
        one_second_silence = AudioSegment.silent(duration=1000)
        for i in range(len(errortime)-1):
            miderrorpart.append(song[int(errortime[i][0]*1000):int(errortime[i][1]*1000)])
            midcorrpart.append(song[int(errortime[i][1]*1000):int(errortime[i+1][0]*1000)])
        miderrorpart.append(song[int(errortime[-1][0] * 1000):int(errortime[-1][1] * 1000)])
        endpart=song[int(errortime[-1][-1]* 1000):]
        miderrorpart = list(map(lambda x: self.speed_change(x,0.95), miderrorpart))
        miderrorpart=list(map(lambda x:x+9,miderrorpart))#加大音量
        miderrorpart = list(map(lambda x: one_second_silence+x, miderrorpart))  #添加静默
        for i in range(len(midcorrpart)):
            startpart+=miderrorpart[i]+midcorrpart[i]
        startpart+=miderrorpart[-1]
        res=startpart+endpart
        res.export(outputpath+audiofile.split('/')[-1], format="mp3")

if __name__ == '__main__':
    at=Audio_tech()
    #将原来音频文本转成plain txt
    at.transfeachFile('/Users/guanghe/Documents/CNN/','/Users/guanghe/Documents/CNN/plain_txt/')
    #利用 plain txt 和mp3 生成语音和文本句子同步映射的json
    #at.Synch_audio_feachFile('/Users/guanghe/Documents/CNN/plain_txt/', '/Users/guanghe/Documents/CNN/json/')
    from MarkError2 import mark_error
    m = mark_error()
    testworda = open('/Users/guanghe/Documents/CNN/test/原文本.txt').read().strip()
    testwordb = open('/Users/guanghe/Documents/CNN/test/测试文本.txt').read().strip()
    m.fit(testworda, testwordb)
    testworda = m.str_list(testworda)
    testwordb = m.str_list(testwordb)
    errorlist=m.commonSequence(testworda, testwordb)

    #输出错误语句所在的句子在mp3音频中的时刻
    errortime=at.SentenctTime( errorlist, '/Users/guanghe/Documents/CNN/json/阿富汗一天多起爆炸袭击 ISIS认领首都爆炸案.json')
    print('错误语句所在音频时刻：' + str(errortime))
    at.jsonChangeaudio(errortime,'/Users/guanghe/Documents/CNN/阿富汗一天多起爆炸袭击 ISIS认领首都爆炸案.mp3',
                       '/Users/guanghe/Documents/CNN/changed_audio/')





