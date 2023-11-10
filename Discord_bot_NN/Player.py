class Player:
    def __init__(self, member):
        self.member = member
        self.score = 0
        self.id = member.id
        self.nickname = member.display_name
        self.avatarIcon = member.avatar.url
        
    def __str__(self):
        return str(f"{self.nickname} : {self.score}")
        
    def getid(self):
        return self.member.id
    
    def getName(self):
        return self.member.display_name
    
    def getIcon(self):
        return self.member.avatar.url
    
    def getScore(self):
        return self.score
    
    def scorePlus(self, score):
        self.score += score

EMPTY_SCORE = "X : X"
class ScoreManager:
    def __init__(self, player_List) -> None:
        self.player_List = player_List
        self.hightier = [EMPTY_SCORE,EMPTY_SCORE,EMPTY_SCORE]
        self.first = None
        self.second = None
        self.third = None
    
    def SetRank(self):
        sorted_list = sorted(self.player_List, key=lambda player: player.getScore(), reverse=True)
        # Assign the top three players if they exist
        if len(sorted_list) > 0:
            self.hightier[0] = sorted_list[0]
        if len(sorted_list) > 1:
            self.hightier[1] = sorted_list[1]
        if len(sorted_list) > 2:
            self.hightier[2] = sorted_list[2]
            
    def GetSortList(self):
        sorted_list = sorted(self.player_List, key=lambda player: player.getScore(), reverse=True)
        return sorted_list
            
    def Gethightier(self):
        self.SetRank()
        return self.hightier
    
    #맞춘 사람 id로 해당하는 id를 가진 Player객체의 점수 상승.
    def Correct(self, id):
        for player in self.player_List:
            if player.id == id:
                player.scorePlus(1)