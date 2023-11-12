#
# 1. 게임이 시작되고 방이 생성되면 30초 뒤 게임이 시작된다. OK
# 2. 게임이 시작되면 게임방에 들어와 있는 인원을 참가자 리스트에 넣는다. OK
# 3.1 30초가 지나면 !게임시작을 친 사람이 문제주제를 선택할 수 있게 한다. OK
#     (버튼식)(다른사람도 볼 수 있지만 누르지는 못함)
# 3.2 주제 선택을 한 뒤 게임시작을 누르면 진짜 시작,  OK
#     주의사항(띄어쓰기 금지, 정답입력방법등, 정답은 게임채팅창에서만 입력하기등등) 출력후 문제가 출제된다.
# 3.3 참가자 리스트에 존재하는 사람이 게임채팅창에 입력하면 정답입력메소드를 호출. OK
#      답이 제출된다. Anwser("플레이어가 입력함")
# 3.4 만약 정답과 같다면 현재문제 정답자 리스트에 추가. 만약 1번째면 3점, 2번째면 2점, 3번째면 1점추가.
# 3.5 총 3명이 맞추면 다음문제로 넘어감
# 3.6 또는 스킵 인원이 참가자 절반이 넘어가면 다음문제로 넘어감.
#
import random
import time
import discord
import asyncio

import yt_dlp
from Data import DataContainer, Question
from Player import Player
from Player import ScoreManager
from discord import Embed
from yt_dlp import YoutubeDL

#상수
ABLE_JOIN_TIME = 5
TIME_OUT = 30
QUIZ_TIME = 40
ROOM_NAME = "-Game-"

class Game:
    category_name = "Bot-Games"
    def __init__(self, bot) -> None:
        self.bot = bot
        self.isGameStart = False
        self.isGameReady = False
        self.category_name = "Bot-Games"
        self.category = None
        self.guild = None
        self.text_channel = None
        self.voice_channel = None
        self.player_id_list = []
        self.starterid = None
        self.selected_theme = None
        self.current_question_list = None
        self.vc = None
        
    async def GameStart(self, ctx):
        #통화방 및 채팅방 생성
        if(self.isGameReady or self.isGameStart):
            await ctx.send(f"이미 게임이 진행중입니다! 통화방에서 {ctx.bot.user.name}을 찾아보세요!")
            return
        await self.__Create_channel(ctx)
        if self.starterid is None:
            try :
                await ctx.send(f"게임에 참가한 플레이어가 없습니다. 게임을 종료합니다.")
            except:
                await self.text_channel.send(f"게임에 참가한 플레이어가 없습니다. 게임을 종료합니다.")
            await self.__GameReset()
            return
        isPlayerSelect = await self.Choicetheme(ctx)
        if not isPlayerSelect:
            await self.__GameReset()
            return
        await self.ProgressGame(self.bot)
        asyncio.sleep(30)
        self.__GameReset()

    async def __Create_channel(self, ctx):
        self.isGameReady = True
        self.guild = ctx.guild
        exist_category = discord.utils.get(self.guild.categories, name=self.category_name)
        
        if not exist_category:
            self.category = await ctx.guild.create_category(self.category_name)
            self.text_channel = await ctx.guild.create_text_channel('game', category=self.category)
            self.voice_channel = await ctx.guild.create_voice_channel(ROOM_NAME, category=self.category)
        else:
            self.category = discord.utils.get(self.guild.categories, name=self.category_name)
            self.text_channel = discord.utils.get(self.category.text_channels, name='game')
            self.voice_channel = discord.utils.get(self.category.voice_channels, name=ROOM_NAME)
            await self.ClearRoom()
            self.category = await ctx.guild.create_category(self.category_name)
            self.text_channel = await ctx.guild.create_text_channel('game', category=self.category)
            self.voice_channel = await ctx.guild.create_voice_channel(ROOM_NAME, category=self.category)

        self.vc = await self.voice_channel.connect()
        bgm = "https://www.youtube.com/watch?v=Yb-rLsCpBvI"
        self.__Music_Start(bgm, 0)
        try:
            await ctx.send(f"게임이 시작되었습니다. {ABLE_JOIN_TIME}초 동안 <#{self.voice_channel.id}>에 입장할 수 있습니다.")
        except:
            await self.text_channel.send(f"게임이 시작되었습니다. {ABLE_JOIN_TIME}초 동안 <#{self.voice_channel.id}>에 입장할 수 있습니다.")

        await asyncio.sleep(ABLE_JOIN_TIME)
        overwrites = {self.guild.default_role: discord.PermissionOverwrite(connect=False)}
        await self.voice_channel.edit(overwrites=overwrites)
        overwrites = {self.guild.default_role: discord.PermissionOverwrite(send_messages=False)}
        await self.text_channel.edit(overwrites=overwrites)
        try:
            await ctx.send(f"{ABLE_JOIN_TIME}초가 지났습니다. 이제 <#{self.voice_channel.id}>에 입장할 수 없습니다.")
        except:
            await self.text_channel.send(f"{ABLE_JOIN_TIME}초가 지났습니다. 이제 <#{self.voice_channel.id}>에 입장할 수 없습니다.")
        

    #유저에게 주제 선택창 띄우고, 해당 주제를 로드함.
    #저장되는 내용 self.current_question_list, self.selected_theme
    #로드하지 않으면 False, 로드하면 True 반환
    async def Choicetheme(self, ctx):
        view = ThemeView(self.starterid)
        self.supermember = ctx.guild.get_member(self.starterid)
        display_name = self.supermember.display_name
        embed=discord.Embed(title=f"방장은 {TIME_OUT}초 안에 주제를 선택하세요!", description="아래의 버튼을 눌러 주제를 선택하세요!", color=0xe6fedc)
        embed.set_author(name=f"현재 방장 : {display_name}")
        embed.set_thumbnail(url=self.supermember.avatar.url)
        msg = await self.text_channel.send(embed=embed)
        await self.text_channel.send(view=view)
        countdown_task = asyncio.create_task(self.countdown(msg, embed))
        await view.wait()
        countdown_task.cancel()
        if self.vc and self.vc.is_playing():
            self.vc.stop()
            time.sleep(1)
        #누른 버튼에서 문제리스트를 가져옴.
        self.selected_theme = view.get_selected_theme()
        self.current_question_list = view.dataloader.get_exam_list(self.selected_theme)
        random.shuffle(self.current_question_list)
        self.isGameStart = True
        self.isGameReady = False
        if self.current_question_list:
            embed=discord.Embed(title=f"{self.selected_theme}을 선택하였습니다.", description="문제를 가져옵니다...", color=0xe6fedc)
            await msg.edit(embed=embed)
            embed = discord.Embed(title=f"노래 듣고 맞추기 ({self.selected_theme})",
                      description=f"> 주의사항\n```\n1. 모든 정답은 **띄어쓰기** 없이 입력하세요. \n2. 영어제목의 경우 영어로 써도 되고 발음으로 써도 됩니다.\n3. 한문제당 {QUIZ_TIME}초의 시간이 주어집니다.\n4. \"/\"기호는 사용하지 마세요.\n```",
                      colour=0x00b0f4)
            await self.text_channel.send(embed=embed)
            return True
        else:
            embed=discord.Embed(title=f"방장이라는 사람이... 주제를 고르지 않았습니다..", description="곧 방이 사라집니다.", color=0xff0000)
            await msg.edit(embed=embed)
            return False
            
    #카운트다운 1초마다 embad변경시킴.
    async def countdown(self, msg, embed):
        start_time = time.time()  # 시작 시간
        while True:
            elapsed_time = time.time() - start_time  # 경과 시간
            remaining_time = TIME_OUT - int(elapsed_time)  # 남은 시간
            if remaining_time <= 0:
                break
            embed.title = f"방장은 {remaining_time}초 안에 주제를 선택하세요!"
            await msg.edit(embed=embed)
            await asyncio.sleep(1)  # 1초 대기
    #Url을 받아 해당하는 노래를 틀어줌.    
    def __Music_Start(self, url, start_time):
        ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
            self.audio_source = discord.FFmpegOpusAudio(url2, options=f'-ss {start_time}')
            self.vc.play(self.audio_source)

    def __Music_Stop(self):
        if self.vc and self.vc.is_playing():
            self.vc.stop()
            if self.audio_source:  # If audio source exists
                print("오디오소스정리함")
                self.audio_source.cleanup()  # Clean up the audio source

    async def ProgressGame(self, bot):
        question_list_len = len(self.current_question_list)
        overwrites = {self.guild.default_role: discord.PermissionOverwrite(send_messages=True)}
        await self.text_channel.edit(overwrites=overwrites)
        #플레이어 ID리스트를 Player 객체로 변환한 게임참가 확정리스트 (점수관리용)
        player_List = []
        #현재 통화방에서 플레이어 객체를 생성하고 리스트화.
        for member in self.voice_channel.members:
            if member.bot:
                continue
            tmp_player = Player(member)
            player_List.append(tmp_player)
        scoremanager = ScoreManager(player_List)
        
        for i in range(question_list_len):
            question = self.current_question_list[i]
            start_time = question.GetStarttime()
            url = "https://www.youtube.com/watch?v="+question.GetUrl()
            self.__Music_Start(url, start_time)
            try:
                def check(m):
                    if m.channel == self.text_channel and m.author.id in self.player_id_list and not m.content.startswith('/'):
                        return question.AnwserCheck(m.content)
                #상위 3명 추출.
                hightier = scoremanager.Gethightier()
                
                embed = discord.Embed(title=f"주제 : {self.selected_theme}",
                      description=f"> **현재 순위**\n```\n1. {hightier[0]}점\n2. {hightier[1]}점\n3. {hightier[2]}점\n```__아 이거 들어봤는데__",
                      colour=0xccfff0)
                embed.set_author(name=f"{self.supermember.display_name}님이 방장입니다.", icon_url=f"{self.supermember.avatar.url}")
                embed.set_footer(text=f"문제 : {question_list_len - i} /  {question_list_len}")
                await self.text_channel.send(embed=embed)
                
                message = await bot.wait_for('message', check=check, timeout=QUIZ_TIME)
                scoremanager.Correct(message.author.id)
                await self.text_channel.send(f'**{message.author}**님, 정답입니다!\n정답 : **{question.Getdesc()}**')
            except asyncio.TimeoutError:
                await self.text_channel.send(f'시간이 초과되었습니다. 다음 문제로 넘어갑니다. 정답 : **{question.Getdesc()}**')
            
            if i < question_list_len - 1:
                await self.text_channel.send('다음 문제로 넘어갑니다.')
            self.__Music_Stop()
            await asyncio.sleep(1)
    
        await self.text_channel.send('모든 문제가 끝났습니다..')
        # 최종 점수 패널 생성
        final_result_list = scoremanager.GetSortList()
        description = f"> **최종 순위**\n```\n"
        for i, player in enumerate(final_result_list):
            description = description+f"{i+1}. {str(player)}점\n"
        description += "```"
        winner = final_result_list[0]
        embed = discord.Embed(title=f"{winner.getName()}님 축하드립니다!", description=description, colour=0xccfff0)
        embed.set_thumbnail(url=winner.getIcon())
        await self.text_channel.send(embed=embed)

        
    #플레이어 통화방 입장,퇴장 관리
    async def voice_state_Event(self, member, before, after):
        if not member.bot and self.isGameReady:
            channel = before.channel or after.channel
            if channel.id == self.voice_channel.id:
                if before.channel is None and after.channel is not None:  # 사용자가 채널에 입장했는지 확인합니다.
                    await self.__PlayerJoin(member)
                elif before.channel is not None and after.channel is None:  # 사용자가 채널에서 나갔는지 확인합니다.
                    await self.__PlayerExit(member)
    #플레이어 입장메소드 -> player_List에 추가
    async def __PlayerJoin(self,member):
        if member.id not in self.player_id_list:
            self.player_id_list.append(member.id)
            self.__set_Starter()
            print(f"현재 등록된 플레이어 : {self.player_id_list}, 현재 방장 : {self.starterid}")
            embed = Embed(description=f"{member.mention}님이 입장하셨습니다.", color=0xE5FFCC)
            embed.set_thumbnail(url=member.avatar.url)
            await self.text_channel.send(embed=embed)
    #플레이어 퇴장메소드 -> player_List에서 삭제
    async def __PlayerExit(self,member):
        if self.player_id_list:
            self.player_id_list.remove(member.id)
            self.__set_Starter()
            print(f"현재 등록된 플레이어 : {self.player_id_list}, 현재 방장 : {self.starterid}")
            embed = Embed(description=f"{member.mention}님이 퇴장하셨습니다.", color=0xFF1300)
            embed.set_thumbnail(url=member.avatar.url)
            await self.text_channel.send(embed=embed)
    #방장 설정하기.
    def __set_Starter(self):
        if not self.player_id_list:
            self.starterid = None
        elif self.starterid is None:
            self.starterid = self.player_id_list[0]   
        elif self.player_id_list[0] == self.starterid:
            return
        else:
            self.starterid = self.player_id_list[0]
    async def __GameReset(self):
        await asyncio.sleep(5)
        if self.vc:
            self.vc = await self.vc.disconnect()
        await self.ClearRoom()
        self.__init__()
    #개발용 메소드 꼭 지우기
    async def DebugGameReset(self,ctx):
        self.guild = ctx.guild
        if self.vc:
            self.vc = await self.vc.disconnect()
        await self.ClearRoom()
        self.__init__(self.bot)

    #방이 존재한다면 삭제.
    async def ClearRoom(self):
        category = discord.utils.get(self.guild.categories, name=self.category_name)
        if category is not None:  # 카테고리가 존재하는 경우
            for channel in category.channels:  # 카테고리 아래의 모든 채널에 대해
                await channel.delete()  # 채널을 삭제합니다.
            await category.delete()  # 마지막으로 카테고리를 삭제합니다.
            

#주제선택 뷰
class ThemeView(discord.ui.View):
    def __init__(self, starterid, timeout=TIME_OUT):
        super().__init__(timeout=timeout)
        self.starterid = starterid
        self.dataloader = DataContainer()
        self.button_list = []
        self.selected_theme = None
        
        theme_list = self.dataloader.get_theme_list()
        for theme in theme_list:
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
            message = await interaction.channel.send(f"!!! **{interaction.user.display_name}님은 방장이 아닙니다.**")
            await asyncio.sleep(1)
            await message.delete()
            return
        self.theme_view.selected_theme = self.label
        await interaction.response.send_message(f"{interaction.user.display_name}님이 {self.label}을 선택하였습니다.")
        self.theme_view.stop()