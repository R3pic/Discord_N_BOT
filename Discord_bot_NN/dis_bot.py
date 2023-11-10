#패키지 임포트
import discord
from discord.ext import commands
#내가 만든 모듈 임포트
from Game import Game
import Config

token = Config.TOKEN

intents=discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

game = Game(bot)


@bot.event
async def on_ready():
    print(f'{bot.user}이 활성화 되었습니다.')
    
@bot.event
async def on_disconnect():
    print(f'{bot.user}이 비활성화 되었습니다.')

@bot.command()
async def 게임시작(ctx):
    await game.GameStart(ctx)

@bot.command()
async def 게임종료(ctx):
    if ctx.author == ctx.guild.owner:
        await game.DebugGameReset(ctx)

@bot.event
async def on_voice_state_update(member, before, after):
    if not game.isGameStart:
        await game.voice_state_Event(member,before,after)
    
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

bot.run(token)
