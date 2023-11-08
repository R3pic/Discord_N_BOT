#
# 1. 게임이 시작되고 방이 생성되면 30초 뒤 게임이 시작된다. OK
# 2. 게임이 시작되면 게임방에 들어와 있는 인원을 참가자 리스트에 넣는다. OK
# 3.1 30초가 지나면 !게임시작을 친 사람이 문제주제를 선택할 수 있게 한다. <----------TODO이거 해야돼!!!!!!!!!!!!!!
#     (버튼식)(다른사람도 볼 수 있지만 누르지는 못함)
# 3.2 주제 선택을 한 뒤 게임시작을 누르면 진짜 시작, 
#     주의사항(띄어쓰기 금지, 정답입력방법등, 정답은 게임채팅창에서만 입력하기등등) 출력후 문제가 출제된다.
# 3.3 참가자 리스트에 존재하는 사람이 게임채팅창에 입력하면 정답입력메소드를 호출. 
#      현재 문제번호와 답이 제출된다. Anwser(int currentMun, "플레이어가 입력함")
# 3.4 만약 정답과 같다면 현재문제 정답자 리스트에 추가. 만약 1번째면 3점, 2번째면 2점, 3번째면 1점추가.
# 3.5 총 3명이 맞추면 다음문제로 넘어감
# 3.6 또는 스킵 인원이 참가자 절반이 넘어가면 다음문제로 넘어감.
#
import discord
import random
import asyncio
from Data import DataContainer
from discord import Embed

#상수
ABLE_JOIN_TIME = 5

class Game:
    category_name = "NoNoBot-Games"
    def __init__(self) -> None:
        self.isGameStart = False
        self.isGameReady = False
        self.category_name = "NoNoBot-Games"
        self.category = None
        self.text_channel = None
        self.voice_channel = None
        self.player_List = []
        self.starterid = None
        self.selectedTheme = None
        self.current_question_list = None
        
    async def GameStart(self, ctx):
        #통화방 및 채팅방 생성
        if(self.isGameReady):
            await ctx.send(f"이미 게임이 진행중입니다! 통화방에서 {ctx.bot.user.name}을 찾아보세요!")
            return
        
        await self.Create_channel(ctx)
        
        await self.Choicetheme(ctx)

    async def Create_channel(self, ctx):
        self.isGameReady = True
        self.guild = ctx.guild
        exist_category = discord.utils.get(self.guild.categories, name=self.category_name)
        if not exist_category:
            self.category = await ctx.guild.create_category(self.category_name)
            self.text_channel = await ctx.guild.create_text_channel('-Game-', category=self.category)
            self.voice_channel = await ctx.guild.create_voice_channel('-Game-', category=self.category)
            print(f'Creating a new category: {self.category_name}')
        else:
            print(f'Category {self.category_name} already exists.')
        self.vc = await self.voice_channel.connect()
        await self.text_channel.send(f"게임이 시작되었습니다. {ABLE_JOIN_TIME}초 동안 <#{self.voice_channel.id}>에 입장할 수 있습니다.")
        await asyncio.sleep(ABLE_JOIN_TIME)
        overwrites = {self.guild.default_role: discord.PermissionOverwrite(connect=False)}
        await self.voice_channel.edit(overwrites=overwrites)
        overwrites = {self.guild.default_role: discord.PermissionOverwrite(send_messages=False)}
        await self.text_channel.edit(overwrites=overwrites)
        if self.starterid == None:
            print("유저가 없어 게임을 종료합니다.")
            return
        await self.text_channel.send(f"{ABLE_JOIN_TIME}초가 지났습니다. 이제 <#{self.voice_channel.id}>에 입장할 수 없습니다.")
        self.isGameStart = True
        self.isGameReady = False

    async def Choicetheme(self, ctx):
        view = ThemeView(self.starterid)
        member = ctx.guild.get_member(self.starterid)
        display_name = member.display_name
        embed = Embed(description=f"{display_name}", color=0xE5FFCC)
        await self.text_channel.send(embed=embed, view=view)
        await view.wait()
        #누른 버튼에서 문제리스트를 가져옴.
        self.selectedTheme = view.get_selected_theme()
        self.current_question_list = view.dataloader.get_exam_list(self.selectedTheme)
        print(self.selectedTheme)
        for a in self.current_question_list:
            print(a)
        
        
    #플레이어 통화방 입장,퇴장 관리
    async def voice_state_Event(self, member, before, after):
        if not member.bot:
            channel = before.channel or after.channel
            if channel.id == self.voice_channel.id:
                if before.channel is None and after.channel is not None:  # 사용자가 채널에 입장했는지 확인합니다.
                    await self.PlayerJoin(member)
                elif before.channel is not None and after.channel is None:  # 사용자가 채널에서 나갔는지 확인합니다.
                    await self.PlayerExit(member)

    #플레이어 입장메소드 -> Player_List에 추가
    async def PlayerJoin(self,member):
        self.player_List.append(member.id)
        self.__set_Starter()
        print(f"현재 등록된 플레이어 : {self.player_List}, 현재 방장 : {self.starterid}")
        embed = Embed(description=f"{member.mention}님이 입장하셨습니다.", color=0xE5FFCC)
        embed.set_thumbnail(url=member.avatar.url)
        await self.text_channel.send(embed=embed)
    #플레이어 퇴장메소드 -> Player_List에서 삭제
    async def PlayerExit(self,member):
        self.player_List.remove(member.id)
        self.__set_Starter()
        print(f"현재 등록된 플레이어 : {self.player_List}, 현재 방장 : {self.starterid}")
        embed = Embed(description=f"{member.mention}님이 퇴장하셨습니다.", color=0xFF1300)
        embed.set_thumbnail(url=member.avatar.url)
        await self.text_channel.send(embed=embed)
    #방장 설정하기.
    def __set_Starter(self):
        if not self.player_List:
            self.starterid = None
        elif self.starterid is None:
            self.starterid = self.player_List[0]   
        elif self.player_List[0] == self.starterid:
            return
        else:
            self.starterid = self.player_List[0]
            
            
class ThemeView(discord.ui.View):
    def __init__(self, starterid, timeout=30):
        super().__init__(timeout=timeout)
        self.starterid = starterid
        self.dataloader = DataContainer()
        self.button_list = []
        self.selected_theme = None
        
        theme_list = self.dataloader.get_theme_list()

        for theme in theme_list:
            if not theme:  # 테마가 빈 문자열이거나 None인 경우
                print("Invalid theme found:", theme)
            button = ThemeButton(theme, self)
            self.add_item(button)
            self.button_list.append(button)
            
    def get_selected_theme(self) -> str:  # 추가
        return self.selected_theme

#버튼 작동 버튼이름을 반환함.
class ThemeButton(discord.ui.Button):
    def __init__(self, label, theme_view):
        super().__init__(label=label, style=discord.ButtonStyle.grey)
        self.theme_view = theme_view

    async def callback(self, interaction):
        if interaction.user.id != self.theme_view.starterid:
            msg = await interaction.response.send_message(f"{interaction.user.display_name}님은 방장이 아닙니다.")
            await asyncio.sleep(2)
            await msg.delete()
            return
        self.theme_view.selected_theme = self.label
        await interaction.response.send_message(f"{interaction.user.display_name}님이 {self.label}을 선택하였습니다.")
        self.theme_view.stop()
