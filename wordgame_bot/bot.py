import os

from dotenv import load_dotenv
from discord import Message, Embed
from discord.ext import commands
from wordgame_bot.attempt import Attempt, AttemptParser
from wordgame_bot.embed import QuordleMessage, WordleMessage
from wordgame_bot.quordle import QuordleAttemptParser
from wordgame_bot.leaderboard import AttemptDuplication, Leaderboard, connect_to_leaderboard
from wordgame_bot.wordle import WordleAttemptParser

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class WordgameBot(commands.Bot):
    def __init__(self, command_prefix, description=None, **options):
        self.leaderboard: Leaderboard | None = None
        self.wordle_message: WordleMessage = WordleMessage()
        self.quordle_message: QuordleMessage = QuordleMessage()
        super().__init__(command_prefix, description, **options)

bot = WordgameBot(command_prefix='-')


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

@bot.event
async def on_message(message: Message):
    embed = None
    if message.channel.id == 944748500787269653:
        if message.content.startswith('Wordle ') and "/6" in message.content:
            embed = await handle_wordle(message)
        elif message.content.startswith('Daily Quordle #'):
            embed = await handle_quordle(message)
        elif message.content.lower() in ("leaderboard", "l"):
            embed = await get_leaderboard(message)
        # TODO add listener for help message

        if embed is not None:
            await message.channel.send(embed=embed)

async def handle_quordle(message: Message) -> Embed:
    attempt = QuordleAttemptParser(message.content)
    attempt_details = submit_attempt(attempt, message)
    return bot.quordle_message.create_embed(message.author, attempt_details)

async def handle_wordle(message: Message) -> Embed:
    attempt = WordleAttemptParser(message.content)
    attempt_details = submit_attempt(attempt, message)
    return bot.wordle_message.create_embed(message.author, attempt_details)

async def submit_attempt(attempt: AttemptParser, message: Message):
    attempt_details = attempt.parse()
    try:
        bot.leaderboard.insert_submission(attempt_details, message.author)
    except AttemptDuplication as ad:
        cheat_str = f"{ad.username} trying to submit attempt for day {ad.day} again... CHEAT"
        await message.channel.send(cheat_str)
        return # TODO Replace with error embeds
    return attempt_details

async def get_leaderboard() -> Embed:
    return bot.leaderboard.get_leaderboard()

if __name__ == "__main__": # pragma: no cover
    with connect_to_leaderboard() as leaderboard:
        bot.leaderboard = leaderboard
        bot.run(TOKEN)
