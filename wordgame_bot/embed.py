from discord import Color, Embed, User

from wordgame_bot.quordle import QuordleAttempt
from wordgame_bot.wordle import WordleAttempt


class EmbedCreator:

    @staticmethod
    def create_quordle_embed(user: User, attempt: QuordleAttempt) -> Embed:
        q_embed = Embed(
            title = "🧠 Quordle Submission 🧠",
            color = Color.gold()
        )
        q_embed.set_author(name="QuordlerParser", icon_url="https://styles.redditmedia.com/t5_5sz4bw/styles/communityIcon_3qy4mer1lqh81.png?width=256&s=b5f57f27a5c13170505365a686fca349a0cb368f")
        if attempt.score <= 25:
            thumbnail="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8IA9Juny2kQw0v1IV2EnzzMs5JEjMH33BHzmof6gg3qm0svccUXi4nr0CBv5S8dn9IXs&usqp=CAU"
        else:
            thumbnail="https://cdn.memes.com/up/18641351578798577/i/1616796464166.jpg"

        q_embed.set_thumbnail(url=thumbnail)
        attempt_str = f"User: {user.name}\nDay: {attempt.day}\nScore: {attempt.score}/50\nCorrect: {attempt.num_correct}/4\n"
        q_embed.add_field(name="Attempt", value=attempt_str, inline=False)
        q_embed.set_footer(text="Quordle: https://www.quordle.com/#/\n")
        return q_embed

    @staticmethod
    def create_wordle_embed(user: User, attempt: WordleAttempt) -> Embed:
        w_embed = Embed(
            title = "🤠 Wordle Submission 🤠",
            color = Color.dark_red()
        )
        w_embed.set_author(name="WordleParser", icon_url="https://play-lh.googleusercontent.com/jQXwLdYhmDdd5mISOcRkaU0Q7rwm4Yphc6YmJgeBzLe_IrZ5IVNX4WoIGtZL8k6G5Q=w256")
        if attempt.score > 6:
            thumbnail="https://wompampsupport.azureedge.net/fetchimage?siteId=7575&v=2&jpgQuality=100&width=700&url=https%3A%2F%2Fi.kym-cdn.com%2Fentries%2Ficons%2Foriginal%2F000%2F037%2F344%2Fcoverwise.jpg"
        else:
            thumbnail="https://ots.nbcwpshield.com/wp-content/uploads/2022/01/wordle-mockup.jpg?quality=85&strip=all&resize=1200%2C675"

        w_embed.set_thumbnail(url=thumbnail)
        attempt_str = f"User: {user.name}\nDay: {attempt.day}\nScore: {attempt.score}/10\n"
        w_embed.add_field(name="Attempt", value=attempt_str, inline=False)
        w_embed.set_footer(text="Wordle: https://www.nytimes.com/games/wordle/index.html\n")
        return w_embed