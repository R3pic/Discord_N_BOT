#패키지 임포트
import discord
from discord.ext import commands
#내가 만든 모듈 임포트
from Game import Game
import Config

token = Config.TOKEN

intents=discord.Intents.all()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="/", intents=intents)

games:Game = {}  # 서버 ID를 키로 갖는 게임 인스턴스 딕셔너리

@bot.event
async def on_ready():
    print(f'{bot.user}이 활성화 되었습니다.')
    
@bot.event
async def on_disconnect():
    print(f'{bot.user}이 비활성화 되었습니다.')

@bot.command()
async def 게임시작(ctx):
    guild_id = ctx.guild.id  # 현재 길드(서버)의 ID를 가져옵니다.
    if guild_id not in games:
        games[guild_id] = Game(bot)  # 해당 길드 ID에 대한 새 게임 인스턴스를 생성합니다.
    await games[guild_id].GameStart(ctx)

@bot.command()
async def 게임종료(ctx):
    guild_id = ctx.guild.id
    if ctx.author == ctx.guild.owner:
        if guild_id in games:
            await games[guild_id].DebugGameReset(ctx)
            del games[guild_id]  # 게임 종료 후 인스턴스를 제거합니다.

@bot.event
async def on_voice_state_update(member, before, after):
    guild_id = member.guild.id  # 멤버가 속한 길드(서버)의 ID를 가져옵니다.
    if guild_id in games:  # 해당 길드 ID에 대한 게임 인스턴스가 존재하는지 확인합니다.
        game = games[guild_id]  # 해당 길드의 게임 인스턴스를 가져옵니다.
        if not game.isGameStart:
            await game.voice_state_Event(member, before, after)
            
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

bot.run(token)
