from telethon import TelegramClient, events, errors
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import InputPhoto
import re
import asyncio
import random, os
from datetime import datetime
import json
import logging



logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

api_id = 
api_hash = ''
MY_ID = 

allowed_users = {}

session_name = 'my_user_session'  

client = TelegramClient(session_name, api_id, api_hash)
client.flood_sleep_threshold = 120


rp_replies_enabled = {}




SAVE_FOLDER = "saved_messages"
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

chat_monitoring = {}

uk_rf_articles = {
    "105": "Убийство, то есть умышленное причинение смерти другому человеку - наказывается лишением свободы на срок от шести до пятнадцати лет с ограничением свободы на срок до двух лет либо без такового.",
    "111": "Умышленное причинение тяжкого вреда здоровью, опасного для жизни человека - наказывается лишением свободы на срок до восьми лет.",
    "112": "Умышленное причинение средней тяжести вреда здоровью - наказывается лишением свободы на срок до трех лет.",
    "115": "Умышленное причинение легкого вреда здоровью - наказывается штрафом в размере до сорока тысяч рублей, либо обязательными работами на срок до четырехсот восьмидесяти часов, либо исправительными работами на срок до одного года.",
    "116": "Побои - наказываются штрафом в размере до сорока тысяч рублей, либо обязательными работами на срок до четырехсот восьмидесяти часов, либо исправительными работами на срок до одного года.",
    "119": "Угроза убийством или причинением тяжкого вреда здоровью - наказывается обязательными работами на срок до четырехсот восьмидесяти часов, либо ограничением свободы на срок до двух лет, либо лишением свободы на срок до двух лет.",
    "158": "Кража, то есть тайное хищение чужого имущества - наказывается штрафом в размере до восьмидесяти тысяч рублей, либо обязательными работами на срок до трехсот шестидесяти часов, либо исправительными работами на срок до одного года.",
    "159": "Мошенничество, то есть хищение чужого имущества или приобретение права на чужое имущество путем обмана или злоупотребления доверием - наказывается штрафом в размере до ста двадцати тысяч рублей, либо обязательными работами на срок до трехсот шестидесяти часов, либо исправительными работами на срок до одного года.",
    "161": "Грабеж, то есть открытое хищение чужого имущества - наказывается обязательными работами на срок до четырехсот восьмидесяти часов, либо исправительными работами на срок до двух лет, либо лишением свободы на срок до четырех лет.",
    "162": "Разбой, то есть нападение в целях хищения чужого имущества, совершенное с применением насилия, опасного для жизни или здоровья, либо с угрозой применения такого насилия - наказывается лишением свободы на срок до восьми лет со штрафом в размере до пятисот тысяч рублей.",
    "163": "Вымогательство, то есть требование передачи чужого имущества под угрозой применения насилия - наказывается ограничением свободы на срок до четырех лет, либо лишением свободы на срок до четырех лет со штрафом в размере до восьмидесяти тысяч рублей.",
    "213": "Хулиганство, то есть грубое  нарушение общественного порядка, выражающее явное неуважение к обществу - наказывается обязательными работами на срок до четырехсот восьмидесяти часов, либо исправительными работами на срок от одного года до двух лет, либо лишением свободы на срок до пяти лет.",
    "228": "Незаконные приобретение, хранение, перевозка, изготовление, переработка наркотических средств - наказываются штрафом в размере до сорока тысяч рублей, либо обязательными работами на срок до четырехсот восьмидесяти часов, либо лишением свободы на срок до трех лет.",
    "228.1": "Незаконные производство, сбыт или пересылка наркотических средств - наказываются лишением свободы на срок от четырех до восьми лет.",
    "260": "Незаконная рубка лесных насаждений - наказывается штрафом в размере до пятисот тысяч рублей, либо обязательными работами на срок до четырехсот восьмидесяти часов, либо лишением свободы на срок до двух лет.",
    "282": "Возбуждение ненависти либо вражды, а равно унижение человеческого достоинства - наказываются штрафом в размере от трехсот тысяч до пятисот тысяч рублей, либо принудительными работами на срок от одного года до четырех лет, либо лишением свободы на срок от двух до пяти лет.",
    "322": "Незаконное пересечение Государственной границы Российской Федерации - наказывается штрафом в размере до двухсот тысяч рублей, либо лишением свободы на срок до двух лет."
}

async def save_chat_history(chat_id):
    try:
        chat = await client.get_entity(chat_id)
        chat_folder = os.path.join(SAVE_FOLDER, str(chat_id))
        if not os.path.exists(chat_folder):
            os.makedirs(chat_folder)

        filename = os.path.join(chat_folder, "messages.txt")
        
        messages_list = []
        async for message in client.iter_messages(chat, limit=100):
            sender = await message.get_sender()
            sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() if sender else "Unknown"
            username = f"(@{sender.username})" if sender and sender.username else ""
            timestamp = message.date.strftime('%Y-%m-%d %H:%M:%S')
            
            message_text = f"[{timestamp}] {sender_name} {username}:\n{message.text or ''}\n"
            if message.media:
                message_text += "[медиа]\n"
            message_text += "-\n"
            messages_list.append(message_text)

        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(messages_list)
        
        return True
        
    except Exception as e:
        print(f"ошибка сохранения {chat_id}: {e}")
        return False

async def check_messages():
    while True:
        for chat_id in list(chat_monitoring.keys()):
            await save_chat_history(chat_id)
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern='.вид'))
async def view_handler(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    
    chat = await event.get_chat()
    chat_id = chat.id
    
    if chat_id in chat_monitoring:
        del chat_monitoring[chat_id]
        await event.reply("сохранение выключено")
    else:
        chat_monitoring[chat_id] = True
        await save_chat_history(chat_id)
        await event.reply(f"сохранение включено для {chat.title if hasattr(chat, 'title') else 'чата'}")
    
    raise events.StopPropagation



nicknames = [
    "we a verified",
    "jugg reals fuck", 
    "operplugg",
    "pullup via moscow",
    "> have monsters in the telegram",
    "xozhu pod nebesami pochti polzhizni zhivu v odnoy travme",
    "celestriada/archive/2006",
    "celestriada",
    'детектив оползень',
    'эмси черемушки',
    'арлекин 40000 извинений',
    'анонимнэ имбирь',
    'темнiй прiнц',
    'апендикс рыжий',
    'алиналудоманка',
    'sleepy typing',
    'гта 5рп твич.тв',
    'пркосет',
    'лирика ксанакс алпразoлам цевики40 экстази сидативики',
    'pod oblakami nayden budto solnce',
    'stripe accounts refeed guals',
    'coding via russia',
    'non stop workin everyday'
]

nickname_changing = False
nickname_task = None

@client.on(events.NewMessage(pattern='.ник'))
async def nickname_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    global nickname_changing, nickname_task
    
    if nickname_changing:
        nickname_changing = False
        if nickname_task:
            nickname_task.cancel()
        await event.reply("смена ника остановлена")
    else:
        nickname_changing = True
        nickname_task = asyncio.create_task(change_nickname_periodically())
        await event.reply("смена ника запущена")
    
    raise events.StopPropagation

async def change_nickname_periodically():
    global nickname_changing
    try:
        while nickname_changing:
            new_nick = random.choice(nicknames)
            try:
                await client(UpdateProfileRequest(
                    first_name=new_nick,
                    last_name=""
                ))
                print(f"ник изменен на: {new_nick}")
            except errors.FloodWaitError as e:
                print(f"Телеграм просит подождать {e.seconds} секунд")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"ошибка смены ника: {e}")
            
            await asyncio.sleep(30)  
    except asyncio.CancelledError:
        print("смена ника остановлена")

@client.on(events.NewMessage(pattern='.добник'))
async def add_nickname_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    message_text = event.text or ""
    new_nick = message_text.replace('.добник', '').strip()
    
    if not new_nick:
        await event.reply("напиши: .добник новый_ник")
        return
    
    nicknames.append(new_nick)
    await event.reply(f"ник добавлен! всего ников: {len(nicknames)}")
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.никлист'))
async def nicklist_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    if not nicknames:
        await event.reply("список ников пуст")
        return
    
    nick_list = "список ников:\n"
    for i, nick in enumerate(nicknames, 1):
        nick_list += f"{i}. {nick}\n"
    
    await event.reply(nick_list)
    raise events.StopPropagation

avatar_changing = False
avatar_task = None

@client.on(events.NewMessage(pattern='.ава'))
async def avatar_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    global avatar_changing, avatar_task
    
    if avatar_changing:
        avatar_changing = False
        if avatar_task:
            avatar_task.cancel()
        await event.reply("смена авы остановлена")
    else:
        if not os.path.exists("avs"):
            os.makedirs("avs")
            await event.reply("создана папка avs. добавь туда фото")
            return
        
        photos = [f for f in os.listdir("avs") if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        if not photos:
            await event.reply("в папке avs нет фото")
            return
        
        avatar_changing = True
        avatar_task = asyncio.create_task(change_avatar_periodically())
        await event.reply("смена авы запущена")
    
    raise events.StopPropagation

async def change_avatar_periodically():
    global avatar_changing

    try:
        while avatar_changing:
            photos = [f for f in os.listdir("avs") if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            if not photos:
                await asyncio.sleep(15)
                continue

            random_photo = random.choice(photos)
            photo_path = os.path.join("avs", random_photo)


            if not os.path.exists(photo_path):
                print(f"Файл не найден: {photo_path}")
                await asyncio.sleep(15)
                continue

            try:

                current_photos = await client.get_profile_photos('me')
                if current_photos:
                    await client(DeletePhotosRequest([
                        InputPhoto(
                            id=photo.id,
                            access_hash=photo.access_hash,
                            file_reference=photo.file_reference
                        ) for photo in current_photos
                    ]))
            except Exception as e:
                print(f"Ошибка удаления авы: {e}")


            await client(UploadProfilePhotoRequest(
                file=await client.upload_file(photo_path)  
            ))

            print(f"Ава изменена на: {random_photo}")
            await asyncio.sleep(15)  

    except asyncio.CancelledError:
        print("Смена авы остановлена")
    except Exception as e:
        print(f"Ошибка в change_avatar_periodically: {e}")
@client.on(events.NewMessage(pattern='.добава'))
async def add_avatar_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    reply_msg = await event.get_reply_message()
    if not reply_msg or not reply_msg.media:
        await event.reply("ответь на фото")
        return
    
    if not os.path.exists("avs"):
        os.makedirs("avs")
    
    try:
        file_path = await reply_msg.download_media(file="avs")
        await event.reply("фото добавлено в avs")
    except Exception as e:
        await event.reply(f"ошибка загрузки: {e}")
    
    raise events.StopPropagation

allowed_users = {}

response_templates = [
    "привет! иди нахуй",
    "не пиши сюда",
    "соси мне пидорас ебаный!",
    "ты просто слабый педик",
    "да чисто подсоси мой хуй",
    "сходи нахуй",
    "да прост соси ок?",
    "у тебя мать шлюха!",
    "ты сын шлюхи?",
    "а еще че скажешь фрик ебаный",
    'да соси ты фрик ебучий',
    'съеби нахуй отсюда',
    'чисто нищий пидорас сельский',
    'гнилозубый хуесос не пиши в чат',
    'отродье ебаное ты!',
    'да закрой ебыч свой',
    'педик ты мерзкий нахуй',
    'че ты пидорас ебаный',
    'да вбей ебальник свой',
    'да нах ты пишешь в чат?',
    'закрой ебальник свой хач ебаный',
    'фрик ебучий в чате',
    'ты ща на мой хуй сядешь',
    'уебище блядское ты прост',
    'да стяни пасть псина ебучая',
    'маме твоей решетку выбил нахуй',
    'слабонервный пидорас пойди нахуй']


@client.on(events.NewMessage(pattern='.реп'))
async def rep_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    message_text = event.text or ""
    args = message_text.replace('.реп', '').strip().split()
    
    if len(args) < 1:
        await event.reply("напиши: .реп ID_пользователя")
        return
    
    user_id = args[0]
    
    try:
        user = await client.get_entity(int(user_id))
        allowed_users[user_id] = True
        await event.reply(f"ок ща я отвечу {user_id}")
        await event.delete()
    except:
        await event.reply(f"не нашел пользователя {user_id}")
        await event.delete()
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.анрпл'))
async def disable_rp_replies(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    message_text = event.text or ""
    args = message_text.replace('.анрпл', '').strip().split()
    
    if len(args) < 1:
        await event.reply("напиши: .анрпл ID_пользователя")
        return
    
    user_id = args[0]
    
    if user_id in rp_replies_enabled:
        del rp_replies_enabled[user_id]
        await event.reply(f"бот больше не отвечает рпл {user_id}")
    else:
        await event.reply(f"пользователь {user_id} не в списке рпл")
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.анреп'))
async def unrep_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    message_text = event.text or ""
    args = message_text.replace('.анреп', '').strip().split()
    
    if len(args) < 1:
        await event.reply("напиши: .анреп ID_пользователя")
        return
    
    user_id = args[0]
    
    if user_id in allowed_users:
        del allowed_users[user_id]
        await event.reply(f"больше не отвечаю {user_id}")
        await event.delete()
    else:
        await event.reply(f"пользователь {user_id} не в списке")
    
    raise events.StopPropagation

@client.on(events.NewMessage)
async def auto_reply_handler(event):

    sender_id = str(event.sender_id)
    if sender_id not in allowed_users:
        return
    

    if event.text.startswith('.') or event.sender_id == MY_ID:
        return
    
    try:
 
        sender = await event.get_sender()
        first_name = sender.first_name or ""
        
 
        template = random.choice(response_templates)
        reply_text = template.format(first_name)
        

        await event.reply(reply_text)
        
    except Exception as e:
        print(f"Ошибка в auto_reply_handler: {e}")


@client.on(events.NewMessage(pattern='.вид'))
async def view_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    chat = await event.get_chat()
    chat_id = chat.id
    
    if chat_id in chat_monitoring:
        del chat_monitoring[chat_id]
        await event.reply("сохранение выключено")
    else:
        chat_monitoring[chat_id] = True
        await event.reply(f"сохранение включено для {chat.title if hasattr(chat, 'title') else 'чата'}")
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.статус'))
async def status_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    chat = await event.get_chat()
    status = "включено" if chat.id in chat_monitoring else "выключено"
    
    chat_folder = os.path.join(SAVE_FOLDER, str(chat.id))
    filename = os.path.join(chat_folder, "messages.txt")
    file_exists = os.path.exists(filename)
    
    await event.reply(f"Сохранение: {status}\nФайл существует: {file_exists}\nАктивные чаты: {len(chat_monitoring)}")

@client.on(events.NewMessage(pattern='.овнер'))
async def start(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    await event.reply('создатель кода @juggstalker чат @juggstalkers')
    await event.delete()
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.фото'))
async def photo_handler(event):
    try:
        if event.sender_id != MY_ID:
            return
        
        reply_msg = await event.get_reply_message()
        if not reply_msg:
            return
        
        user = await reply_msg.get_sender()
        await event.delete()
        
        photo = await client.download_profile_photo(user.id, file=bytes)

        if photo:            
            await client.send_file(
                event.chat_id,
                photo,
                caption="че эта наху",
                force_document=False 
            )
    except Exception as e:
        print(f"Ошибка в photo_handler: {e}")

@client.on(events.NewMessage(pattern='.дел'))
async def delete_my_messages(event):
    try:
        if event.sender_id != MY_ID:
            return
        
        await event.delete()
        chat = await event.get_chat()
        me = await event.get_sender()
        
        async for msg in client.iter_messages(chat, from_user=me.id):
            try:
                await msg.delete()
            except Exception as e:
                print(f"Не удалось удалить сообщение {msg.id}: {e}")
        
        confirm = await client.send_message(chat, "я удалил пошел ты нахуй")
        await asyncio.sleep(2)
        await confirm.delete()
        
    except Exception as e:
        print(f"Ошибка в delete_my_messages: {e}")

@client.on(events.NewMessage(pattern='айд'))
async def id_handler(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    sender = await event.get_sender()
    user_info = (
        f'ID = {sender.id}\n'
        f'Username = {sender.username}\n'
    )
    await event.delete()
    await event.reply(user_info)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.чат'))
async def chat_id_handler(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    chat = await event.get_chat()
    await event.reply(f'ID чата {chat.id}')
    await event.delete()
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.мур'))
async def cat_handler(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    await event.reply('Мур мяу.')
    await event.delete()
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.хелп'))
async def bad_handler(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    await event.reply('команды: ' \
    '.чат, айд, .лан, рпл, .худ, .моястатья')
    await event.delete()
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.лан'))
async def bad_handler(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    await event.reply('Лан без обид окей?')
    raise events.StopPropagation



@client.on(events.NewMessage(pattern='рпл'))
async def bad_handler(event):
    if event.sender_id != MY_ID and str(event.sender_id) not in rp_replies_enabled:
        return
    
    reply_msg = await event.get_reply_message()
    await event.delete()


    if not templates_cache:
        await event.reply("❌ Нет доступных шаблонов")
        return


    shuffled_templates = templates_cache.copy()
    random.shuffle(shuffled_templates)
    

    for template in shuffled_templates:
        await reply_msg.reply(template)
        await asyncio.sleep(0.0001)
    
    raise events.StopPropagation
@client.on(events.NewMessage(pattern='.худ'))
async def mention_handler(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    message_text = event.text or ""
    mentions = re.findall(r'@(\w+)', message_text)
    if mentions:
        for username in mentions:
            try:
                user = await client.get_entity(f"@{username}")
                await event.reply(f"ID = @{username} {user.id}")
            except Exception:
                await event.reply(f"Не удалось найти пользователя @{username}")
                await event.delete()
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.моно'))
async def mono_handler(event):
    if event.sender_id != MY_ID:
        return
    await event.delete()
    
    message_text = event.text or ""
    mono_text = message_text.replace('.моно', '').strip()
    
    if mono_text:
        formatted_text = f"```\n{mono_text}\n```"
        await event.reply(formatted_text)
    else:
        await event.reply("Использование: `.моно ваш текст`")
        await event.delete()
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.экспорт'))
async def export_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    try:
        chat = await event.get_chat()
        chat_id = chat.id
        
        chat_folder = os.path.join(SAVE_FOLDER, str(chat_id))
        messages_file = os.path.join(chat_folder, "messages.txt")
        
        if not os.path.exists(messages_file):
            await event.reply("нету сообщений для экспорта")
            return
        
 
        export_filename = os.path.join(chat_folder, f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        with open(messages_file, 'r', encoding='utf-8') as source:
            with open(export_filename, 'w', encoding='utf-8') as target:
                target.write(f"Экспорт сообщений из чата: {chat.title if hasattr(chat, 'title') else 'личка'}\n")
                target.write(f"Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                target.write("=" * 50 + "\n\n")
                target.write(source.read())
        

        await client.send_file(
            event.chat_id,
            export_filename,
            caption=f"экспорт сообщений из {chat.title if hasattr(chat, 'title') else 'чата'}"
        )
        

        await asyncio.sleep(2)
        os.remove(export_filename)
        
    except Exception as e:
        await event.reply(f"ошибка при экспорте: {e}")
    
    raise events.StopPropagation



@client.on(events.NewMessage(pattern='.лк'))
async def mention_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    message_text = event.text or ""
    args = message_text.replace('.лк', '').strip().split()
    
    if len(args) < 1:
        await event.reply("напиши: .лк @username")
        return
    
    username = args[0]
    
    try:
        user = await client.get_entity(username)
        template = random.choice(response_templates)
        message = f"{username} {template.format(user.first_name or 'ты')}"
        await event.reply(message)
        
    except Exception as e:
        await event.reply(f"не нашел {username}")
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.добшаб'))
async def add_template_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    message_text = event.text or ""
    new_template = message_text.replace('.добшаб', '').strip()
    
    if not new_template:
        await event.reply("напиши: .добшаб твой текст {}")
        return
    
    if '{}' not in new_template:
        await event.reply("должен быть {} для имени")
        return
    
    response_templates.append(new_template)
    await event.reply(f"шаблон добавлен. всего: {len(response_templates)}")
    
    raise events.StopPropagation

kazakh_enabled = False
kazakh_task = None

@client.on(events.NewMessage(pattern='.казах'))
async def kazakh_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    global kazakh_enabled, kazakh_task
    
    if kazakh_enabled:
        kazakh_enabled = False
        if kazakh_task:
            kazakh_task.cancel()
        
    else:
        kazakh_enabled = True
        kazakh_task = asyncio.create_task(kazakh_message_periodically(event.chat_id))
        
    
    raise events.StopPropagation

async def kazakh_message_periodically(chat_id):
    global kazakh_enabled
    try:
        while kazakh_enabled:
            await client.send_message(chat_id, "наш тг заходи к нам @juggstalkers")
            await asyncio.sleep(5)  
    except asyncio.CancelledError:
        print("")
    except Exception as e:
        print(f"Ошибка в kazakh_message_periodically: {e}")


@client.on(events.NewMessage(pattern='.моястатья'))
async def my_article_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    message_text = event.text or ""
    args = message_text.replace('.моястатья', '').strip().split()
    
    if len(args) < 1:

        article_num = random.choice(list(uk_rf_articles.keys()))
        article_text = uk_rf_articles[article_num]
        response = f"Статья {article_num} УК РФ:\n\n{article_text}"
    else:
        article_num = args[0]
        if article_num in uk_rf_articles:
            article_text = uk_rf_articles[article_num]
            response = f"Статья {article_num} УК РФ:\n\n{article_text}"
        else:
            response = f"Статья {article_num} не найдена в базе\n\nДоступные статьи: {', '.join(sorted(uk_rf_articles.keys()))}"
    
    await event.reply(response)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.найдистатью'))
async def find_article_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    message_text = event.text or ""
    search_term = message_text.replace('.найдистатью', '').strip().lower()
    
    if not search_term:
        await event.reply("напиши: .найдистатью ключевое_слово")
        return
    
    found_articles = []
    for article_num, article_text in uk_rf_articles.items():
        if search_term in article_text.lower():
            found_articles.append((article_num, article_text))
    
    if found_articles:
        response = f"Найдено статей по запросу '{search_term}':\n\n"
        for i, (art_num, art_text) in enumerate(found_articles[:5], 1):  # максимум 5 статей
            preview = art_text[:100] + "..." if len(art_text) > 100 else art_text
            response += f"{i}. Статья {art_num}: {preview}\n\n"
        
        if len(found_articles) > 5:
            response += f"... и еще {len(found_articles) - 5} статей"
    else:
        response = f"По запросу '{search_term}' статей не найдено"
    
    await event.reply(response)
    raise events.StopPropagation



TARGET_GROUP_ID = -1003291027615
def load_templates_from_file(filename="pizda.txt"):
    templates = []
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                templates = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"loaded {len(templates)} templates")
        else:
            templates = [
                "привет! иди нахуй",
                "не пиши сюда",
                "соси мне пидорас ебаный!",
                "ты просто слабый педик", 
                "да чисто подсоси мой хуй"
            ]
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(templates))
            print("created templates.txt")
    except Exception as e:
        print(f"error loading templates: {e}")
        templates = ["ошибка загрузки шаблонов"]
    
    return templates

templates_cache = load_templates_from_file()

reply_to_all_enabled = False

@client.on(events.NewMessage(pattern='.алл'))
async def reply_all_handler(event):
    if event.sender_id != MY_ID:
        return
    

    if event.chat_id != TARGET_GROUP_ID:
        return
    
    await event.delete()
    
    global reply_to_all_enabled
    
    if reply_to_all_enabled:
        reply_to_all_enabled = False
        
    else:
        reply_to_all_enabled = True

    
    raise events.StopPropagation

@client.on(events.NewMessage)
async def auto_reply_all_handler(event):

    if event.chat_id != TARGET_GROUP_ID or not reply_to_all_enabled:
        return
    
    if (event.sender_id == MY_ID or 
        not event.text or 
        event.text.startswith('.')):
        return
    
    try:
        if templates_cache:
            template = random.choice(templates_cache)
            await event.reply(template)
            print(f"replied to {event.sender_id} in {event.chat_id}")
    except Exception as e:
        print(f"error: {e}")

@client.on(events.NewMessage(pattern='.обновитьшаблоны'))
async def reload_templates_handler(event):
    if event.sender_id != MY_ID:
        return
    

    await event.delete()
    
    global templates_cache
    templates_cache = load_templates_from_file()
    await event.reply(f"шаблонов: {len(templates_cache)}")
    
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.аллстатус'))
async def reply_all_status_handler(event):
    if event.sender_id != MY_ID:
        return
    
    await event.delete()
    
    status_text = f"шаблонов: {len(templates_cache)}\n"
    
    if not reply_to_all_enabled:
        status_text += "не отвечаю"
    else:
        status_text += "отвечаю в целевой группе"
    
    await event.reply(status_text)
    raise events.StopPropagation



def main():
    print("Запускаю...")
    
    client.start()
    client.run_until_disconnected()
    asyncio.create_task(check_messages())
    

if __name__ == '__main__':
    main()
    client.loop.run_until_complete(main())
