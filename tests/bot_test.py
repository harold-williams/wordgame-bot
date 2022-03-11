from __future__ import annotations

from collections.abc import Callable
from email.message import Message
from unittest.mock import MagicMock, patch

import pytest

from wordgame_bot.bot import bot, on_message, submit_attempt
from wordgame_bot.leaderboard import AttemptDuplication

VALID_CHANNEL = 944748500787269653
OCTORDLE_MESSAGE = (
    "Daily Octordle #42\n"
    "3️⃣4️⃣\n"
    "🔟🕛\n"
    "2️⃣6️⃣\n"
    "1️⃣7️⃣\n"
    "octordle.com\n"
    "🟨⬜⬜⬜🟨 ⬜🟨⬜⬜⬜\n"
    "⬜🟨⬜⬜🟨 ⬜⬜🟨⬜⬜\n"
    "🟩🟩🟩🟩🟩 🟩⬜⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
    "\n"
    "⬜⬜⬜🟨⬜ 🟨⬜⬜⬜🟨\n"
    "⬜⬜⬜🟨⬜ ⬜⬜⬜⬜🟨\n"
    "⬜⬜⬜⬜🟨 ⬜🟨⬜🟨⬜\n"
    "⬜⬜🟨⬜⬜ ⬜⬜⬜⬜🟩\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜⬜⬜\n"
    "⬜⬜⬜⬜⬜ ⬜⬜⬜🟨⬜\n"
    "🟨🟨🟨⬜⬜ ⬜⬜⬜⬜⬜\n"
    "🟩⬜🟩⬜⬜ 🟨⬜⬜⬜🟨\n"
    "🟩🟩🟩🟩🟩 🟨⬜⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟨🟩🟩🟨🟩\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
    "\n"
    "⬜⬜🟩🟩🟩 ⬜🟨⬜⬜⬜\n"
    "🟩🟩🟩🟩🟩 ⬜🟨🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩⬜🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩⬜⬜🟩⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟨🟩⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩\n"
    "\n"
    "🟩🟩🟩🟩🟩 🟨🟨🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜🟩🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜⬜🟨🟩⬜\n"
    "⬛⬛⬛⬛⬛ ⬜⬜⬜🟨⬜\n"
    "⬛⬛⬛⬛⬛ ⬜⬜🟨🟨🟩\n"
    "⬛⬛⬛⬛⬛ ⬜⬜⬜🟨🟨\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩"
)
QUORDLE_MESSAGE = (
    "Daily Quordle #17\n"
    "4️⃣🟥\n"
    "5️⃣8️⃣\n"
    "quordle.com\n"
    "🟨⬜⬜🟩🟩 ⬜⬜⬜⬜🟨\n"
    "⬜🟨⬜⬜🟨 🟩🟨⬜🟨🟩\n"
    "🟩🟩⬜⬜⬜ ⬜🟨⬜⬜🟨\n"
    "🟩🟩🟩🟩🟩 ⬜🟨⬜⬜🟨\n"
    "⬛⬛⬛⬛⬛ ⬜⬜⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜🟩🟨🟩⬜\n"
    "⬛⬛⬛⬛⬛ ⬜🟨🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜🟨🟨⬜⬜\n"
    "⬛⬛⬛⬛⬛ 🟩🟩⬜🟩🟩\n"
    "\n"
    "🟨⬜⬜⬜⬜ ⬜⬜⬜⬜🟨\n"
    "⬜⬜⬜⬜⬜ ⬜🟩🟨🟨⬜\n"
    "🟨⬜🟨⬜⬜ ⬜⬜⬜⬜⬜\n"
    "🟨⬜🟩⬜⬜ ⬜⬜⬜⬜🟨\n"
    "🟩🟩🟩🟩🟩 ⬜⬜⬜⬜⬜\n"
    "⬛⬛⬛⬛⬛ ⬜🟨⬜🟨🟨\n"
    "⬛⬛⬛⬛⬛ ⬜🟩⬜🟩🟩\n"
    "⬛⬛⬛⬛⬛ 🟩🟩🟩🟩🟩"
)
WORDLE_MESSAGE = (
    "Wordle 6 6/6\n" "⬜⬜⬜⬜⬜\n" "⬜⬜⬜🟨⬜\n" "🟨⬜⬜⬜🟨\n" "⬜🟨🟨🟨🟨\n" "🟩🟩🟩⬜🟩\n" "🟩🟩🟩🟩🟩\n"
)


@pytest.mark.parametrize(
    "content, expected_handler",
    [
        (
            OCTORDLE_MESSAGE,
            "handle_octordle",
        ),
        (
            QUORDLE_MESSAGE,
            "handle_quordle",
        ),
        (
            WORDLE_MESSAGE,
            "handle_wordle",
        ),
        (
            "leaderboard",
            "get_leaderboard",
        ),
        (
            "league",
            "get_league",
        ),
        (
            "lg",
            "get_league",
        ),
    ],
)
async def test_on_valid_message(
    valid_message: MagicMock,
    content: str,
    expected_handler: Callable,
):
    generated_embed = MagicMock()
    with patch(
        f"wordgame_bot.bot.{expected_handler}",
        return_value=generated_embed,
    ) as handler:
        valid_message.content = content
        await on_message(valid_message)
        handler.assert_called_once_with(valid_message)
        valid_message.channel.send.assert_called_with(embed=generated_embed)


@pytest.mark.parametrize(
    "content, expected_handler",
    [
        (
            OCTORDLE_MESSAGE,
            "handle_octordle",
        ),
        (
            QUORDLE_MESSAGE,
            "handle_quordle",
        ),
        (
            WORDLE_MESSAGE,
            "handle_wordle",
        ),
        (
            "leaderboard",
            "get_leaderboard",
        ),
        (
            "l",
            "get_leaderboard",
        ),
    ],
)
async def test_on_invalid_message(
    invalid_message: MagicMock,
    content: str,
    expected_handler: Callable,
):
    generated_embed = MagicMock()
    with patch(
        f"wordgame_bot.bot.{expected_handler}",
        return_value=generated_embed,
    ) as handler:
        invalid_message.content = content
        await on_message(invalid_message)
        handler.assert_not_called()
        invalid_message.channel.send.assert_not_called()


async def test_submit_valid_attempt(valid_message: Message):
    bot.leaderboard = MagicMock()
    attempt = MagicMock()
    mock_details = MagicMock()
    attempt.parse.return_value = mock_details
    result = await submit_attempt(attempt, valid_message)
    bot.leaderboard.insert_submission.assert_called_once_with(
        mock_details,
        valid_message.author,
    )
    assert result == mock_details


async def test_submit_duplicate_attempt(valid_message: Message):
    bot.leaderboard = MagicMock()
    bot.leaderboard.insert_submission.side_effect = AttemptDuplication(
        valid_message.author.name,
        1,
    )
    attempt = MagicMock()
    mock_details = MagicMock()
    attempt.parse.return_value = mock_details
    result = await submit_attempt(attempt, valid_message)
    bot.leaderboard.insert_submission.assert_called_once_with(
        mock_details,
        valid_message.author,
    )
    assert result == None


async def test_get_leaderboard(valid_message: Message):
    valid_message.content = "leaderboard"
    bot.leaderboard.get_leaderboard = MagicMock()
    await on_message(valid_message)
    bot.leaderboard.get_leaderboard.assert_called_once()


@patch("wordgame_bot.bot.bot")
async def test_handle_quordle(
    bot: MagicMock,
    valid_message: Message,
    mock_parser: MagicMock,
):
    valid_message.content = QUORDLE_MESSAGE

    with patch("wordgame_bot.bot.QuordleAttemptParser", return_value=mock_parser):
        await on_message(valid_message)

    mock_details = mock_parser.parse.return_value
    bot.leaderboard.insert_submission.assert_called_once_with(
        mock_details,
        valid_message.author,
    )
    bot.quordle_message.create_embed.assert_called_once_with(
        mock_details,
        valid_message.author,
    )


@patch("wordgame_bot.bot.bot")
async def test_handle_wordle(
    bot: MagicMock,
    valid_message: Message,
    mock_parser: MagicMock,
):
    valid_message.content = WORDLE_MESSAGE

    with patch("wordgame_bot.bot.WordleAttemptParser", return_value=mock_parser):
        await on_message(valid_message)

    mock_details = mock_parser.parse.return_value
    bot.leaderboard.insert_submission.assert_called_once_with(
        mock_details,
        valid_message.author,
    )
    bot.wordle_message.create_embed.assert_called_once_with(
        mock_details,
        valid_message.author,
    )


@patch("wordgame_bot.bot.bot")
async def test_handle_octordle(
    bot: MagicMock,
    valid_message: Message,
    mock_parser: MagicMock,
):
    valid_message.content = OCTORDLE_MESSAGE

    with patch("wordgame_bot.bot.OctordleAttemptParser", return_value=mock_parser):
        await on_message(valid_message)

    mock_details = mock_parser.parse.return_value
    bot.leaderboard.insert_submission.assert_called_once_with(
        mock_details,
        valid_message.author,
    )
    bot.octordle_message.create_embed.assert_called_once_with(
        mock_details,
        valid_message.author,
    )
