from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import json

count = 0

def load_config():
    global config, TOKEN, ADMIN, connect, userid
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    TOKEN = config['TOKEN'] 
    ADMIN = config['ADMIN']
    connect = config['connect']
    userid = config['userid']

def record_connect():
    global config, connect
    config['connect'] = connect
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def record_user():
    global userid, config
    config['userid'] = userid
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def cut(update, context):
    global connect, count
    msg = update.message
    user = msg.from_user.id
    if str(user) == ADMIN:
        count = 0
        connect = ""
        record_connect()
        msg.reply_text('已断开当前会话\n/clear 清除用户信息')
    else:
        msg.reply_text('不要乱按喵')

def clear(update, context):
    global connect, userid, count
    msg = update.message
    user = msg.from_user.id
    if str(user) == ADMIN:
        count = 0
        userid = ""
        record_user()
        connect = ""
        record_connect()
        msg.reply_text('已清除用户信息')
    else:
        msg.reply_text('不要乱按喵')

def start(update, context):
    update.message.reply_text(f'Hello {update.effective_user.first_name}')
    context.bot.send_sticker(
        chat_id=update.effective_message.chat_id,
        sticker='CAACAgEAAxkBAAIBmGJ1Mt3gP0VaAvccwfw1lwgt53VlAAIXCQACkSkAARB0sik1UbskECQE'
        )

def help(update, context):
    update.message.reply_text('还需要做些什么？')
    context.bot.send_sticker(chat_id=update.effective_message.chat_id, sticker='CAACAgEAAxkBAAIBmGJ1Mt3gP0VaAvccwfw1lwgt53VlAAIXCQACkSkAARB0sik1UbskECQE')

def check():
    global connect, userid
    if (userid != connect):
        return 0
    else:
        return 1

def chat(update, context):
    global connect, userid, count
    bot = context.bot
    msg = update.message
    user = msg.from_user.id
    if msg:
        if str(user) != ADMIN:
            userid = user
            record_user()
        if connect == "":
            connect = userid
            record_connect()
        if check():
            if count == 0:
                if str(user) == ADMIN:
                    msg.from_user.first_name =  userid
                if userid != "":
                    msg.reply_text('成功连接会话')
                    bot.send_message(
                        chat_id=ADMIN,
                        text=(f'当前会话 {msg.from_user.first_name}')
                    )
                    count = count + 1
                else:
                    msg.reply_text('喵？')
            if str(user) == ADMIN:
                if msg.text:
                    bot.send_message(
                        chat_id=connect,
                        text=msg.text
                    )
                elif msg.sticker:
                    bot.send_sticker(
                        chat_id=connect,
                        sticker=msg.sticker
                    )
                elif msg.photo:
                    bot.send_photo(
                        chat_id=connect,
                        photo=msg.photo[-1].file_id
                    )
                elif msg.document:
                    bot.send_document(
                        chat_id=connect,
                        document=msg.document
                    )
                elif msg.video:
                    bot.send_video(
                        chat_id=connect,
                        video=msg.video
                    )
                else:
                    msg.reply_text('不支持这种类型的消息哦')
            else:
                bot.forward_message(
                    chat_id=ADMIN,
                    from_chat_id=connect,
                    message_id=msg.message_id
                )
            userid = connect
            record_user()
        else:
            if count == 1:
                msg.reply_text('其他用户正在会话中，请稍等')
                bot.forward_message(
                            chat_id=ADMIN,
                            from_chat_id=userid,
                            message_id=msg.message_id
                )
                bot.send_message(
                    chat_id=ADMIN,
                    text=(f'{msg.from_user.first_name} 准备连接会话\n/cut 断开当前会话')
                )
                count = count - 1

def main():
    load_config()
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('cut', cut))
    dispatcher.add_handler(CommandHandler('clear', clear))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(MessageHandler(Filters.all & (~Filters.command), chat))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
