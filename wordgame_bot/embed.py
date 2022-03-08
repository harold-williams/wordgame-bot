from __future__ import annotations

from dataclasses import dataclass, field
import random
from discord import Colour, Embed, User
from wordgame_bot.attempt import Attempt

SUCCESS_THUMBNAILS = (
    "https://wompampsupport.azureedge.net/fetchimage?siteId=7575&v=2&jpgQuality=100&width=700&url=https%3A%2F%2Fi.kym-cdn.com%2Fentries%2Ficons%2Foriginal%2F000%2F037%2F344%2Fcoverwise.jpg",
    "https://cdn.memes.com/up/18641351578798577/i/1616796464166.jpg",
    "https://64.media.tumblr.com/e68ad3308e9701c10ca6aebe56008be5/tumblr_inline_p6nhl0n3qv1vvskl5_640.jpg",
    "https://memegenerator.net/img/instances/73729603.jpg",
    "https://preview.redd.it/fh9bx6t4guh81.jpg?width=640&crop=smart&auto=webp&s=efb2a12fe46828e30a55e7f00cd0224ce5a0aa80",
    "https://i.kym-cdn.com/photos/images/newsfeed/001/480/544/6c1.jpg",
    "https://media.makeameme.org/created/that-question-was-5be89b.jpg",
)

FAILURE_THUMBNAILS = (
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8IA9Juny2kQw0v1IV2EnzzMs5JEjMH33BHzmof6gg3qm0svccUXi4nr0CBv5S8dn9IXs&usqp=CAU",
    "https://ots.nbcwpshield.com/wp-content/uploads/2022/01/wordle-mockup.jpg?quality=85&strip=all&resize=1200%2C675",
    "https://preview.redd.it/be3744z6mv981.jpg?width=640&crop=smart&auto=webp&s=fc45dc8b2628485acab9e101391ad4f0cd03f497",
    "https://www.meme-arsenal.com/memes/41413a3e7b911cc978c4c672ebe7ca09.jpg",
    "https://memegenerator.net/img/instances/69628502.jpg",
    "https://i.kym-cdn.com/photos/images/newsfeed/001/762/116/e6b.jpg",
    "https://mediacloud.theweek.com/image/private/s--X-WVjvBW--/f_auto,t_content-image-full-desktop@1/v1608188672/39969_article_full.jpg",
)

WORDGAME_LINKS = (
    "Wordle: https://www.nytimes.com/games/wordle/index.html\n"
    "Quordle: https://www.quordle.com/#/\n"
    "Octordle: https://octordle.com/?mode=daily\n"
)


class MessageCreator:
    def create_embed(self, attempt: Attempt, user: User) -> Embed:
        w_embed = Embed(
            title = self.title,
            color = self.colour
        )
        w_embed.set_author(**self.author)
        if attempt.score > self.threshold:
            thumbnail = get_congratulations_thumbnail()
        else:
            thumbnail = get_failure_thumbnail()
        w_embed.set_thumbnail(url=thumbnail)
        attempt_str = f"User: {user.name}\nDay: {attempt.info.day}\nScore: {attempt.score}/{attempt.maxscore}\n"
        w_embed.add_field(name="Attempt", value=attempt_str, inline=False)
        w_embed.set_footer(text=WORDGAME_LINKS)
        return w_embed


@dataclass
class QuordleMessage(MessageCreator):
    threshold: int = 25
    title: str = "🧠 Quordle Submission 🧠"
    colour: Colour = Colour.gold()
    author: dict[str, str] = field(default_factory=lambda: {
        "name" : "QuordleParser",
        "icon_url" : "https://styles.redditmedia.com/t5_5sz4bw/styles/communityIcon_3qy4mer1lqh81.png?width=256&s=b5f57f27a5c13170505365a686fca349a0cb368f"
    })


@dataclass
class WordleMessage(MessageCreator):
    threshold: int = 6
    title: str = "🤠 Wordle Submission 🤠"
    colour: Colour = Colour.dark_red()
    author: dict[str, str] = field(default_factory=lambda: {
        "name" : "WordleParser",
        "icon_url" : "https://play-lh.googleusercontent.com/jQXwLdYhmDdd5mISOcRkaU0Q7rwm4Yphc6YmJgeBzLe_IrZ5IVNX4WoIGtZL8k6G5Q=w256"
    })


@dataclass
class OctordleMessage(MessageCreator):
    threshold: int = 51
    title: str = "🤓 Octordle Submission 🤓"
    colour: Colour = Colour.green()
    author: dict[str, str] = field(default_factory=lambda: {
        "name" : "OctordleParser",
        "icon_url" : "https://www.egames.news/__export/1645898819912/sites/debate/img/2022/02/26/octopsycho.jpg_415429280.jpg"
    })


def get_congratulations_thumbnail():
    return random.choice(SUCCESS_THUMBNAILS)

def get_failure_thumbnail():
    return random.choice(FAILURE_THUMBNAILS)
