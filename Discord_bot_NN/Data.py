import json
import os

#데이터를 로드해서 읽어낸걸 class문제에 저장.
#class 문제로 리스트로 만들어서 데이터관리하는 class문제관리자

#

#데이터 선언부.

DATA_PATH = "Discord_bot_NN\data"

class Question:
    def __init__(self, url, correct_answer, desc, starttime):
        self.url = url
        self.correct_answer = correct_answer
        self.desc = desc
        self.starttime = starttime
    
    def __str__(self):
        return f'Url: {self.url}, CorrectAnswer: {self.correct_answer}, desc: {self.desc}, time: {self.starttime}'
    
    def AnwserCheck(self, answer :str) -> bool:
        ori_answer = answer.replace(' ', '').lower()
        if ori_answer in self.correct_answer:
            return True
        else:
            print(str(ori_answer), self.correct_answer)
            return False
        
    def Getdesc(self) -> str:
        return self.desc
    def GetUrl(self) -> str:
        return self.url
    def GetStarttime(self) -> str:
        return self.starttime

#json을 실제로 읽고 반환하는 클래스.
class DataReader:
    def __init__(self, path):
        self.path = path
    
    #Json파일들 이름을 추출.
    def read_json_files_name(self) -> list:
        theme_list = []
        for jsonfile in os.listdir(self.path):
            if jsonfile.endswith('.json'):
                theme_name, _ = os.path.splitext(jsonfile)
                theme_list.append(theme_name)
        return theme_list
    #Stri을 받아 해당하는 이름을 가진 Json.load해 반환
    def load_json_content(self, filename: str) -> any:
        with open(os.path.join(self.path, filename), 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
    
#파일이름리스트와 문제리스트 반환가능.
class DataContainer:
    def __init__(self):
        self.reader = DataReader(DATA_PATH)
        self.theme_list = self.reader.read_json_files_name()
    #파일이름입력 -> 해당하는 문제 리스트 반환
    def get_exam_list(self, file_name):
        if file_name is None:
            return None
        jsondata = self.reader.load_json_content(file_name + '.json')
        question_list = []
        for item in jsondata:
            start_time = item.get('StartTime', "0")
            question = Question(item['Url'], item['CorrectAnswer'], item['Desc'], start_time)
            question_list.append(question)
        return question_list
    #로드된 파일 이름 리스트 반환
    def get_theme_list(self)-> list:
        return self.theme_list
    
data = DataContainer()

list = data.get_theme_list()
for data in list:
    print(f"{data} 이건됨")
    
data = DataContainer()
    
exlist = data.get_exam_list("한국")
for dataa in exlist:
    print(dataa)