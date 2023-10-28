import telebot as tb
from telebot import types
import pandas as pd
import numpy as np
from scipy.stats import norm, ttest_rel, mannwhitneyu
from tqdm.auto import tqdm




# Здесь я сохраняю выборку на которой буду тестить
# RAND = 100
# ab_df = pd.DataFrame()
# ab_df['control'] = stats.norm.rvs(loc=50, scale=10, size=5000, random_state=RAND)
# ab_df['test'] = stats.norm.rvs(loc=46, scale=10, size=5000, random_state=RAND)
# ab_df.to_csv('ab_df.csv', index=False)


bot = tb.TeleBot('6303544653:AAFOBPfyI6KEaKrjyPzYceP1bjsMHUTrAPQ')


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("T-test")
    btn2 = types.KeyboardButton("Bootstrap")
    btn3 = types.KeyboardButton("U-test")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Привет, {0.first_name}! Я мини ботик, который немног умеет считать A/B тесты. Выбери метод!".format(message.from_user), reply_markup=markup)
    bot.send_message(message.chat.id, "Сюда нужно загрузить csv фай, у которого 2 столбца (результаты теста)")
    bot.send_message(message.chat.id, "Далее можно выбрать один из методов подсчета, стат значимости результатов")
    bot.send_message(message.chat.id, "Если нет файла нужного формата, то я прекрепил на github сгенерированный файл")



@bot.message_handler(content_types=['document'])
def save_file_csv(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        save_file_csv.src = '/home/max887/' + message.document.file_name
        with open(save_file_csv.src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.send_message(message.chat.id, 'Сохранено!')
        return save_file_csv.src
    except Exception as e:
        bot.send_message(message.chat.id, 'Файл не сохранился')


@bot.message_handler(content_types=['text'])
def func(message):
    src0 = search_file()
    if src0 is None:
        bot.send_message(message.chat.id, 'Вы не загрузили файл!')
    else:
        try:
            if message.text == 'Bootstrap':
                bot.send_message(message.chat.id, 'Ждем) Там 1000 итераций')
                df = pd.read_csv(src0)
                res = get_bootstrap(df.iloc[:, 0], df.iloc[:, 1])
                bot.send_message(message.chat.id, f'p-value = {res}')
                if res >= 0.5:
                    bot.send_message(message.chat.id, 'Результат не стат значим')
                else:
                    bot.send_message(message.chat.id, 'Результат стат значим')
        except Exception as e:
            bot.reply_to(message, e)

        try:
            if message.text == 'T-test':
                df = pd.read_csv(src0)
                res = get_t_test(df.iloc[:, 0], df.iloc[:, 1])
                bot.send_message(message.chat.id, f'p-value = {res}')
                if res >= 0.5:
                    bot.send_message(message.chat.id, 'Результат не стат значим')
                else:
                    bot.send_message(message.chat.id, 'Результат стат значим')
        except Exception as e:
            bot.reply_to(message, e)

        try:
            if message.text == 'U-test':
                bot.send_message(message.chat.id, 'Входные данные должны быть целые числа')
                df = pd.read_csv(src0)
                res = get_mannwhitneyu(df.iloc[:, 0], df.iloc[:, 1])
                bot.send_message(message.chat.id, f'p-value = {res}')
                if res >= 0.5:
                    bot.send_message(message.chat.id, 'Результат не стат значим')
                else:
                    bot.send_message(message.chat.id, 'Результат стат значим')
        except Exception as e:
            bot.reply_to(message, e)


def get_t_test(col1, col2):
    return ttest_rel(col1, col2)[1]


def get_mannwhitneyu(col1, col2):
    return mannwhitneyu(col1, col2)[1]


def get_bootstrap(col1, col2, boot_it=1000, statistic=np.mean):
    boot_len = max([len(col1), len(col2)])
    boot_data = []
    for _ in tqdm(range(boot_it)):
        samples_1 = col1.sample(boot_len, replace=True).values
        samples_2 = col2.sample(boot_len, replace=True).values
        boot_data.append(statistic(samples_1 - samples_2))

    p_1 = norm.cdf(
        x=0,
        loc=np.mean(boot_data),
        scale=np.std(boot_data)
    )
    p_2 = norm.cdf(
        x=0,
        loc=-np.mean(boot_data),
        scale=np.std(boot_data)
    )
    p_value = min(p_1, p_2) * 2

    return p_value

def search_file():
    try:
        return save_file_csv.src
    except Exception as e:
        return None


bot.polling(none_stop=True)
