#패키지 임포트
import discord
from discord.ext import commands
from discord.utils import get
import random
#내가 만든 모듈 임포트
from Game import Game
import Config

token = Config.TOKEN

intents=discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

game = Game()


@bot.event
async def on_ready():
    await Clear_room()
    print(f'{bot.user}이 활성화 되었습니다.')
    
@bot.event
async def on_disconnect():
    print(f'{bot.user}이 비활성화 되었습니다.')

@bot.command()
async def 게임시작(ctx):
    await game.GameStart(ctx)

@bot.event
async def on_voice_state_update(member, before, after):
    if not game.isGameStart:
        await game.voice_state_Event(member,before,after)
    
@bot.event
async def on_message(message):
        if message.content.startswith('!안녕'):
            await message.channel.send('안녕하세요..')
        
        if message.content.startswith('!잘가'):
            await message.channel.send('안녕히계세요..')
        if message.content.startswith('!주사위'):
            a = random.uniform(1,6)
            await message.channel.send(a + '가 나왔는데요..')
        await bot.process_commands(message)

#현재 생성된 게임이 존재할경우 삭제한다.
async def Clear_room():
    guild = bot.guilds[0]  # 봇이 연결된 첫 번째 서버를 선택합니다. 필요에 따라 이 부분을 수정하세요.
    category_name = game.category_name  #삭제하려는 카테고리 이름.
    category = get(guild.categories, name=category_name)
    if category is not None:  # 카테고리가 존재하는 경우
        for channel in category.channels:  # 카테고리 아래의 모든 채널에 대해
            await channel.delete()  # 채널을 삭제합니다.
        await category.delete()  # 마지막으로 카테고리를 삭제합니다.
    

bot.run(token)
