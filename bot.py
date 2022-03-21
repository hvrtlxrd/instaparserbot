from logging import NullHandler
from instaloader.exceptions import ProfileNotExistsException, QueryReturnedNotFoundException
from instaloader.structures import TopSearchResults
from requests.models import HTTPError
import telebot
from telebot import types
import config
import instaloader
import requests
import os
import markups as nav
from telebot.apihelper import ApiTelegramException
from datetime import datetime, timedelta
import pymysql.cursors   
import instabot


bot = telebot.TeleBot(config.TOKEN)

connection = pymysql.connect(host='localhost',
                             user='root',                            
                             db='pyinst',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor) 
print ("connect successful!!") 

last_time = datetime.now()
lasts_time = datetime.now()
past_time = datetime.now()
h = 0
@bot.message_handler(commands=['start'])
def welcome(message):
    if message.from_user.username == "switch02":
        bot.send_message(message.chat.id, "hvrtlxrd любит {0.username} :з".format(message.from_user))
    bot.send_message(message.chat.id, "Добро пожаловать, {0.first_name}!\nМеня зовут <b>{1.first_name}</b>. Я помогаю определить тех, кто не подписан на вас взаимно :)".format(message.from_user, bot.get_me()), 
    parse_mode = 'html')
    sent_msg = bot.send_message(message.chat.id, f"Для этого просто отправь мне свой nickname в instagram")
    
    bot.register_next_step_handler(sent_msg, name_handler)
    global h
    if h == 0:
        global last_time
        last_time -= timedelta(seconds=60)
        h=1
    
names = ""    

proxies = {}

proxies = {
	'http': f"http://45.8.104.232:80",
	'https': f"https://34.138.225.120:8888"
}



L = instaloader.Instaloader(save_metadata=True, compress_json=False, max_connection_attempts = 0)

# L.context._session.cookies.update(cookie_data)
# L.load_session_from_file("bobik2341s")
# L.context._session.proxies = proxies

@bot.message_handler(content_types=['text'])
def name_handler(message):
    global names
    name = message.text
    names = message.text
    global past_time
    global last_time
    try :
        cursor = connection.cursor() 
        sql = "Select user_id from inst "
        cursor.execute(sql) 
        # 1 строка данных
        oneRow = cursor.fetchone()      

        # Output: {'Max_Grade': 4} or {'Max_Grade': None}
        print ("Row Result: ", oneRow) 
        grade = 1
        
        # if oneRow != None and oneRow["id"] != None:
        #     grade = oneRow["id"] + 1 
        cursor = connection.cursor()  
        sql =  "Insert IGNORE into inst (user_id, username, chat_id, lastRequest, instaNik)" \
            + " values (%s, %s, %s, %s, %s) " 
        # sql = " SELECT @newComp, u1.username, u1.chat_id, u1.lastRequest, u1.instaNik FROM inst u1 WHERE user_id = @oldComp AND  NOT EXISTS (SELECT 1 FROM inst u2 WHERE u1.username = u2.username AND u1.chat_id = u2.chat_id AND u1.lastRequest = u2.lastRequest AND u1.instaNik = u2.instaNik AND u2.user_id = @newComp) "
        
        print ("Insert Grade: ", grade)  
        # Выполнить sql и передать 3 параметра.
        cursor.execute(sql, (message.from_user.id, message.from_user.username, message.chat.id, last_time, name ) ) 
        connection.commit()  
    except: 
        connection.close()
    cursor = connection.cursor() 
    sql = "Update IGNORE inst set user_id = %s, username = %s, chat_id = %s, lastRequest = %s, instaNik = %s  "   
                            # Hire_Date
                            # Выполнить sql и передать 3 параметра.
                            # ​​​​​​​
    rowCount = cursor.execute(sql, (message.from_user.id, message.from_user.username, message.chat.id, last_time, name) ) 
    connection.commit()  
    print ("Updated! ", rowCount, " rows") 
    sent_msg = bot.send_message(message.chat.id, "Идет проверка, подождите! Время ожидания зависит от количества ваших подписчиков.")
    status = ['creator', 'administrator', 'member']
    name = message.text
    for stat in status:
        if stat == bot.get_chat_member(chat_id="@testeesaw", user_id=message.from_user.id).status:
            delta = past_time - last_time
            if delta.seconds < 60:
                markup = types.InlineKeyboardMarkup()
                btn_verif= types.InlineKeyboardButton(text='Попробовать еще раз', callback_data='da')
                markup.add(btn_verif)
                sent_msg = bot.send_message(message.chat.id, f"Не так быстро! В целях снижения нагрузки на бота запрос на проверку можно отправлять только через каждые 60 минут.", reply_markup = markup)
                past_time = datetime.now()
            else:
                L.login("bobik2341s", "bobik23#$#41s")
                instagram ='https://www.instagram.com/'
                x=requests.get(instagram+name)
                if x.status_code == 200:
                    profile = instaloader.Profile.from_username(L.context, name)
                    # os.system("instaloader --stories-only --no-posts --no-compress-json --login {0} {1}".format(L.context, name))
                    
                    follow_list = []
                    followees_list = []
                    count=0
                    if profile.is_private == True:
                        sent_msg = bot.send_message(message.chat.id, "Аккаунт закрыт!\nПожалуйста, откройте профиль на время, либо выберите другой аккаунт, чтобы я смог сделать проверку.")
                        bot.register_next_step_handler(sent_msg, name_handler) 
                    else:
                        sent_msg = bot.send_message(message.chat.id, f"Пользователи, которые взаимно на вас не подписаны:")
                        follow_list = []
                        follows_list = []
                        followss_list = []
                        try:
                            for followee in profile.get_followers():
                                follow_list.append(followee.username)
                            for followee in profile.get_followees():
                                followss_list.append(f"{followee.username}")
                                if f'{followee.username}' not in follow_list:
                                    follows_list.append(f"{followee.username}")
                            num = len(follow_list)
                            nums = len(followss_list)
                            follow_list = []
                            follows_list = []
                            if num > 10:
                                for followee in profile.get_followers():
                                    follow_list.append(followee.username)
                                for followee in profile.get_followees():
                                    if f'{followee.username}' not in follow_list:
                                        follows_list.append(f"{followee.username}")
                                        file = open(f"{name}relativefollow.csv","a+")
                                        file.write(f'https://www.instagram.com/{follows_list[count]}/')
                                        file.write("\n")
                                        
                                        doc = open(f'{name}relativefollow.csv', 'rb')
                                        count=count+1  
                                file.close()
                                bot.send_document(message.chat.id, doc)
                                file = open(f"{name}relativefollow.csv","w")
                                file.close() 
                            elif num == 0:
                                sent_msg = bot.send_message(message.chat.id, f"Не взаимных подписок не найдено")
                            elif nums == 0:
                                sent_msg = bot.send_message(message.chat.id, f"Не взаимных подписок не найдено")
                            else:
                                for followee in profile.get_followers():
                                    follow_list.append(followee.username)
                                for followee in profile.get_followees():
                                    if f'{followee.username}' not in follow_list:
                                        follows_list.append(f"{followee.username}")
                                        sent_msg = bot.send_message(message.chat.id, f"https://www.instagram.com/{follows_list[count]}/")
                                        count=count+1    
                            markup = types.InlineKeyboardMarkup()
                            
                            btn_verif= types.InlineKeyboardButton(text='Да', callback_data='add')
                            markup.add(btn_verif)
                            sent_msg = bot.send_message(message.chat.id, f"Спасибо, что использовали нашего бота! Хотите еще раз проверить на взаимные подписки?", reply_markup = markup)
                            past_time = datetime.now()
                            last_time = datetime.now()
                        except HTTPError as e:
                            print (e.code)
                            print (e.read() )
                else:
                    sent_msg = bot.send_message(message.chat.id, f"Я не нашел такого пользователя, попробуй другой :(")
                    sent_msg = bot.send_message(message.chat.id, "Введи ник, который хочешь запарсить")
                    bot.register_next_step_handler(sent_msg, name_handler) 
            break
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_channel= types.InlineKeyboardButton(text='Подписаться', url='https://t.me/testeesaw')
        btn_verif= types.InlineKeyboardButton(text='Проверить подписку', callback_data='verif')
        markup.add(btn_channel, btn_verif)
        bot.send_message(message.chat.id, "Проверка завершена! Подпишитесь на @testeesaw, чтобы получить список тех, кто не подписан на вас.", reply_markup = markup)
    

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    if call.message:
        if call.data == 'verif':
            status = ['creator', 'administrator', 'member']
            for stat in status:
                if stat == bot.get_chat_member(chat_id="@testeesaw", user_id=call.from_user.id).status:
                    bot.answer_callback_query(callback_query_id=call.id, text='Спасибо за подписку! Доступ к функционалу бота открыт')
                    cursor = connection.cursor() 
                    sql = "Select instaNik from inst Where user_id = %s  "   
                    cursor.execute(sql, ( call.from_user.id ) )  
                    connection.commit()
                    name=""
                    for row in cursor:
                        name = row["instaNik"]
                    sent_msg = bot.send_message(call.message.chat.id, name)
                    name_handler(sent_msg)
                    break
            else:
                bot.answer_callback_query(callback_query_id=call.id, text='Вы не подписались!')
        if call.data == 'da':
            delta = datetime.now() - last_time
            if delta.seconds < 60:
                bot.answer_callback_query(callback_query_id=call.id, text='Время еще не пришло :(')
                global past_time
                past_time = datetime.now()
            else:
                past_time = datetime.now()
                cursor = connection.cursor() 
                sql = "Select instaNik from inst Where user_id = %s  "   
                cursor.execute(sql, ( call.from_user.id ) )  
                connection.commit()
                name=""
                for row in cursor:
                    name = row["instaNik"]
                sent_msg = bot.send_message(call.message.chat.id, name)
                name_handler(sent_msg)
        if call.data == 'add':
            sent_msg = bot.send_message(call.message.chat.id, "Введи ник, который хочешь запарсить")
            bot.register_next_step_handler(sent_msg, name_handler)

bot.enable_saving_states()

bot.polling(none_stop=True)