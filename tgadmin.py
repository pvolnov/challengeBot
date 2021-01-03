import datetime

import telebot

from models import Users

TB_BOT_TOKEN = "1411314976:AAHHsTGPIVOoQUlyIobwS1hZE-y1KoyQQ-Y"

bot = telebot.TeleBot(TB_BOT_TOKEN)

taxes = {0: 0, 1: 30, 2: 95, 3: 195, 4: 330, 5: 500, 6: 705, 7: 945, 8: 1220, 9: 1530, 10: 1875, 11: 2255, 12: 2655,
         13: 3055, 14: 3455, 15: 3855, 16: 4255, 17: 4655, 18: 5055, 19: 5455, 20: 5855, 21: 6255, 22: 6655, 23: 7055,
         24: 7455, 25: 7855, 26: 8255, 27: 8655, 28: 9055, 29: 9455}


@bot.message_handler(commands=['start', "/restart"])
def start(message):
    pass


@bot.message_handler(content_types=["photo"])
def done(message):
    print("photo")
    user = Users.get_or_none(Users.tel_id == message.from_user.id)
    if not user:
        user = Users.get_or_create(name=message.from_user.first_name, tel_id=message.from_user.id)
        print("User created")

    if user.last_trening < datetime.date.today():
        print("Comlete")
        user.username = message.from_user.username
        user.last_trening = datetime.date.today()
        user.done_per_week += 1
        user.done += 1
        user.save()
        bot.reply_to(message, f"Тренировка засчитана! Всего выполнено: {user.done}")
    else:
        bot.reply_to(message, f"2 раза за день перебор) Всего выполнено: {user.done}")


def get_leaderboard():
    mes = "Лидер борд 👊🏼\n\n"
    day = datetime.date.today().weekday()
    for i, u in enumerate(Users.select().order_by(Users.done.desc()).execute()):
        rest = 2 - (day - u.done_per_week)
        if u.fails:
            mes += f"{i + 1}. {u.name} - {u.done} [{rest}] (-{taxes[u.fails]})\n"
        else:
            mes += f"{i + 1}. {u.name} - {u.done} [{rest}] 💪\n"

        print(u.name, u.tel_id)
    return mes


@bot.message_handler(content_types=["text"])
def text_mes(message):
    if message.text == "/leaderboard":
        bot.send_message(message.chat.id, get_leaderboard())

    if message.from_user.id == 445330281 and message.text == "/alarm":
        text = "Напомню, что вам нужно сделать сегодня тренировочку: "
        for u in Users.select().execute():
            if u.last_trening < datetime.date.today() and u.username:
                text += f"@{u.username} "
        bot.send_message(message.chat.id, text)

    if message.from_user.id == 445330281 and message.text == "/weekEnd":
        for u in Users.select().execute():
            u.fails += max(5 - u.done_per_week, 0)
            u.done_per_week = 0
            u.save()
        bot.send_message(message.chat.id, "Неделя обновлена.")
        bot.send_message(message.chat.id, get_leaderboard())

    print(message.text, message.from_user.id)


if __name__ == "__main__":
    # tasks = {}
    # sum = 0
    # delt = 30
    # for t in range(30):
    #     tasks[t] = sum
    #     sum += delt
    #     delt += 35
    #     delt = min(delt, 400)
    # print(tasks)
    print("Start")
    bot.polling(none_stop=True, timeout=60)
