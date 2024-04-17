from telebot import types, TeleBot
import json
from src.parser import parse
from src.constants import URL, TOKEN, GAME_OVER_REASONS, BYE_MEME, SOME_MATH_PROBLEMS
from src.keyboard import keyboard
from random import shuffle, randint, choice
from time import sleep, asctime

memes = list()

difficulty = 0

problems = list(SOME_MATH_PROBLEMS.keys())
shuffle(problems)

correct_answer = ""

bot = TeleBot(token=TOKEN)


def get_progress_helper(message: types.Message):
    """
    Sends info about the user's progress by nickname (if found).

    Args:
        message: message.text is a nickname that is searched in database
    """

    nickname = message.text
    with open("winners.json", "r") as file:
        data = json.load(file)
        if nickname in data.keys():
            bot.send_message(message.chat.id,
                             f"*Time*: {data[nickname]['time']}\n"
                             f"*Difficulty*: {data[nickname]['difficulty']}",
                             parse_mode="MarkdownV2")
        else:
            bot.send_message(message.chat.id,
                             "No saved progress for this nickname found.")


@bot.message_handler(commands=["get_progress"])
def get_progress_command(message: types.Message):
    """
    Processes the command "/get_progress".

    Args:
        message: message.text == "/get_progress"
    """

    bot.send_message(message.chat.id,
                     "Enter a nickname.")
    bot.register_next_step_handler(message, get_progress_helper)


@bot.message_handler(commands=["stop"])
def stop_command(message: types.Message):
    """
    Processes the command "/stop".

    Args:
        message: message.text == "/stop"
    """

    bot.send_photo(message.chat.id, BYE_MEME)
    sleep(10)
    bot.send_message(message.chat.id,
                     "Bye! 👋")
    bot.stop_bot()


@bot.message_handler(commands=["help"])
def help_command(message: types.Message):
    """
    Processes the command "/help".

    Args:
        message: message.text == "/help"
    """

    bot.send_message(message.chat.id,
                     "With this bot you can play a game called *MemeMaze*\. You wander through the maze until you find "
                     "an exit \(or until you die\)\. During the game you watch programming memes — and, of course, "
                     "laugh at them\.\n\n"
                     "Useful commands:\n"
                     "`/start` — start a \(new\) game,\n"
                     "`/help` — show this help message,\n"
                     "`/get_progress` — get progress from a previous game,\n"
                     "`/stop` — stop the bot\.",
                     parse_mode="MarkdownV2")


@bot.message_handler(commands=["start"])
def start_command(message: types.Message):
    """
    Processes the command "/start".

    Args:
        message: message.text == "/start"
    """

    global memes
    memes = parse(URL)
    shuffle(memes)
    bot.send_message(message.chat.id,
                     "Hi\! 👋\nThis is my *MemeMaze* bot\.",
                     parse_mode="MarkdownV2")
    sleep(1)
    bot.send_message(message.chat.id,
                     "Before you start, choose the difficulty level \(integer between 1 and 5, where 5 is "
                     "the hardest\)\.",
                     parse_mode="MarkdownV2")
    bot.register_next_step_handler(message, set_difficulty)


@bot.message_handler(content_types=["text"])
def process_extra_message(message: types.Message):
    """
    Called if the user sends unexpected message.

    Args:
        message: any extra message by the user
    """

    help_command(message)


def set_difficulty(message: types.Message):
    """
    Sets the difficulty of the game.

    Args:
        message: message.text is the difficulty level selected by the user

    Raises:
        ValueError.
    """

    global difficulty
    while difficulty == 0:
        try:
            difficulty = int(message.text)
            if difficulty not in range(1, 6):
                raise ValueError
        except ValueError:
            bot.send_message(message.chat.id,
                             "❗ _*Incorrect*_️: integer between 1 and 5, please\. ❗",
                             parse_mode="MarkdownV2")
            bot.register_next_step_handler(message, set_difficulty)
            break
        global memes
        memes = memes[:8 * difficulty]
        bot.send_message(message.chat.id,
                         "Good!")
        sleep(1)
        bot.send_message(message.chat.id,
                         "__LEGEND__: 👇\n||_Imagine you're in a maze\. But it's too dark here, so you can't see "
                         "anything\. At every step you should decide where to go: left, forward, or right\. If you're "
                         "lucky enough, you'll survive\. If not, you'll die\.\.\. Also maybe sometime you'll find an "
                         "exit\._||",
                         parse_mode="MarkdownV2")
        sleep(12)
        bot.send_message(message.chat.id,
                         "Are you ready?")
        bot.register_next_step_handler(message, say_nice)


def say_nice(message: types.Message):
    """
    Tells the user "Nice" and finally starts the game by sending them buttons to choose the first move.

    Args:
        message: message.text is the readiness of the user to start a game
    """

    bot.send_message(message.chat.id,
                     "Nice! 😉")
    sleep(1)
    bot.send_message(message.chat.id,
                     text="Choose what to do:",
                     reply_markup=keyboard)


def process_answer(message: types.Message):
    """
    Processes an answer given by the user to a math problem. Checks if it's correct.

    Args:
        message: message.text is the answer
    """

    global correct_answer
    if message.text == correct_answer:
        bot.send_message(message.chat.id,
                         "Correct!")
        bot.send_photo(message.chat.id, memes.pop())
        sleep(7)
        if difficulty >= 3 and randint(0, 2) == 0:
            problem = problems.pop()
            correct_answer = SOME_MATH_PROBLEMS[problem]
            bot.send_message(message.chat.id,
                             text=problem)
            bot.register_next_step_handler_by_chat_id(message.chat.id, process_answer)
        else:
            bot.send_message(message.chat.id,
                             text="Choose what to do:",
                             reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id,
                         text="Wrong answer :(")
        bot.send_message(message.chat.id,
                         text=f"☠️ *GAME OVER*: {choice(GAME_OVER_REASONS)}\.\.\. ☠️",
                         parse_mode="MarkdownV2")


@bot.callback_query_handler(lambda call: True)
def process_button(call: types.CallbackQuery):
    """
    Processes the user's choice (expressed by pressing the appropriate button).

    Args:
        call: call.data in ["left", "forward", "right"]
    """

    global memes
    if len(memes) == 0:
        bot.send_message(call.message.chat.id,
                         "🎉 *Congratulations, you won\!* 🎉",
                         parse_mode="MarkdownV2")
        bot.send_message(call.message.chat.id,
                         "Tell me your nickname.")
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, save_progress)
    elif randint(0, 9) == 0:
        bot.send_message(call.message.chat.id,
                         f"☠️ *GAME OVER*: {choice(GAME_OVER_REASONS)}\.\.\. ☠️",
                         parse_mode="MarkdownV2")
    else:
        bot.send_message(call.message.chat.id,
                         "Oh, you're alive!")
        bot.send_photo(call.message.chat.id, memes.pop())
        sleep(7)
        if difficulty >= 3 and randint(0, 2) == 0:
            problem = problems.pop()
            global correct_answer
            correct_answer = SOME_MATH_PROBLEMS[problem]
            bot.send_message(call.message.chat.id,
                             text=problem)
            bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_answer)
        else:
            bot.send_message(call.message.chat.id,
                             text="Choose what to do:",
                             reply_markup=keyboard)


def save_progress(message: types.Message):
    """
    Saves the user's progress (if they win). Adds time and difficulty level along with the user's nickname.

    Args:
        message: message.text is a nickname that is added to database
    """

    nickname = message.text
    with open("winners.json", "r") as file:
        data = json.load(file)
        data[nickname] = {
            "time": asctime(),
            "difficulty": difficulty
        }
    with open("winners.json", "w") as file:
        json.dump(data, file)


bot.polling()
