import os
import requests
from bs4 import BeautifulSoup
import json
import telebot

bot = telebot.TeleBot('6309609511:AAEOIGhoXheEWysKep-wy4l_oyq2IgJai_E')

main_url = 'https://health-diet.ru'
url = main_url+"/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"
#1

product_info = []
product_list = []

headers = {
    'Accept':  '*/*',
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36"
}
req = requests.get(url, headers=headers)
src = req.text

soup = BeautifulSoup(src, 'lxml')

all_categories_href = soup.find_all(class_='mzr-tc-group-item-href')
product_info = []

try:
    with open('../food_bot/products.json', 'w')as file:
        file.write('')

except:
    pass

for i in all_categories_href:
    try:
        req = requests.get(main_url+i['href'])
        src = req.text

        soup = BeautifulSoup(src, 'lxml')

        categories__all_food = soup.find('table', class_='mzr-tc-group-table').find('tbody').find_all('tr')


        for i in categories__all_food:
            product_tds = i.find_all('td')

            src = main_url+(product_tds[0].find('a').get('href'))
            title = product_tds[0].find('a').text
            calories = product_tds[1].text
            proteins = product_tds[2].text
            fats = product_tds[3].text
            carbohydrates = product_tds[4].text


            product_info.append(
                {
                    'src': src,
                    'title': title.lower(),
                    'calories': calories,
                    'proteins': proteins,
                    'fats': fats,
                    'carbohydrates': carbohydrates
                }
            )

        with open(f'../food_bot/products.json', 'a', encoding='utf-8') as file:
            json.dump(product_info, file, indent=4, ensure_ascii=False)
    except:
        pass

for i in product_info:
    product_list.append(i['title'])
print(product_list)


def search_info(message, name):
    # with open('products.json', 'r', encoding='utf-8')as file:
    #      test = json.load(file)
    test = product_info
    for i in test:
        if i['title'] == name:
            bot.send_message(message.chat.id, f"Калорийнеость на 100гр: {i['calories']}")
            bot.send_message(message.chat.id, f"Белки на 100гр: {i['proteins']}")
            bot.send_message(message.chat.id, f"Жиры на 100гр: {i['fats']}")
            bot.send_message(message.chat.id, f"Углеводы на 100гр: {i['carbohydrates']}")

@bot.message_handler(commands=['start', 'help'])
def main_func_bot(message):
    bot.send_message(message.chat.id, 'Привет! Я бот, который поможет с твоимм питанием!\nПросто отошли мне название продукта и я выведу его калорийность и краткие характеристики\n <b>Разработал: Ober</b>', parse_mode='html')


@bot.message_handler(content_types=['text'])
def step2(message):
    res = []
    user_input = message.text.lower()
    for i in product_list:
        if user_input.lower() in i:
            res.append(i)

    if len(res) == 1:
        for i in res:
            res1 = i
        bot.send_message(message.chat.id, res1)
        search_info(message, res1)

    else:
        if len(res) != 0:
            bot.send_message(message.chat.id, 'Результат:')
            bot.send_message(message.chat.id,f'Найдено {len(res)} продуктов')
            if len(res) <= 10:
                for i in res:
                    bot.send_message(message.chat.id, i)
            else:
                bot.send_message(message.chat.id, "Слишклм много продуктов для вывода текстом, список отправлен файлом")
                with open(f'send/send_{message.chat.id}.txt', 'w', encoding='utf-8')as file:
                    for i in res:
                        file.write(f'{i}\n')

                file1 = open(f'send/send_{message.chat.id}.txt', encoding='utf-8')
                bot.send_document(message.chat.id, file1)
                file1.close()

            bot.send_message(message.chat.id, 'Уточните название:')
            bot.register_next_step_handler(message, step2)
        else:
            bot.send_message(message.chat.id, 'Ничего не найдено, введите заново:')


bot.polling(none_stop=True)