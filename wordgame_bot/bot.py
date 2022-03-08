import os

from dotenv import load_dotenv
from discord import Message
from discord.ext import commands
from wordgame_bot.embed import QuordleMessage, WordleMessage
from wordgame_bot.quordle import QuordleAttemptParser
from wordgame_bot.leaderboard import AttemptDuplication, Leaderboard, connect_to_leaderboard
from wordgame_bot.wordle import WordleAttemptParser

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class QuordleBot(commands.Bot):

    # Change only the no_category default string
    _help_command = commands.DefaultHelpCommand(
        no_category = 'Commands'
    )

    def __init__(self, command_prefix, description=None, **options):
        self.leaderboard: Leaderboard | None = None
        self.wordle_message: WordleMessage = WordleMessage()
        self.quordle_message: QuordleMessage = QuordleMessage()
        super().__init__(command_prefix, self._help_command, description, **options)

bot = QuordleBot(command_prefix='-')


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message: Message):
    if message.channel.id == 944748500787269653:
        if message.content.startswith('Wordle ') and "/6" in message.content:
            await submit_wordle(message)
        elif message.content.startswith('Daily Quordle #'):
            await submit_quordle(message)
        elif message.content.lower() in ("leaderboard", "l"):
            await get_leaderboard(message)

async def submit_quordle(message: Message):
    attempt = QuordleAttemptParser(message.content)
    attempt_details = attempt.parse()
    try:
        bot.leaderboard.insert_submission(attempt_details, message.author)
    except AttemptDuplication as ad:
        cheat_str = f"{ad.username} trying to submit attempt for day {ad.day} again... CHEAT"
        await message.channel.send(cheat_str)
        return

    embed = bot.quordle_message.create_embed(message.author, attempt_details)
    await message.channel.send(embed=embed)

async def submit_wordle(message: Message):
    attempt = WordleAttemptParser(message.content)
    attempt_details = attempt.parse()
    try:
        bot.leaderboard.insert_submission(attempt_details, message.author)
    except AttemptDuplication as ad:
        cheat_str = f"{ad.username} trying to submit attempt for day {ad.day} again... CHEAT"
        await message.channel.send(cheat_str)
        return

    embed = bot.wordle_message.create_embed(message.author, attempt_details)
    await message.channel.send(embed=embed)

async def get_leaderboard(message: Message):
    leaderboard = bot.leaderboard.get_leaderboard()
    await message.channel.send(embed=leaderboard)

with connect_to_leaderboard() as leaderboard:
    bot.leaderboard = leaderboard
    bot.run(TOKEN)