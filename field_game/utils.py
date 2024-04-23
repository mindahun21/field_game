from .data import *

async def is_admin(username):
    for user in admins:
        if user["username"] == username:
            return user
    
    return False

def check_code(code=""):
    if code in codes:
        if code[5:8] == 'win':
            codes.remove(code)
            return 200
        codes.remove(code)
        return int(code[4])
    else:
        return 404

def changer (ans, length):
    try:
        temp = list(ans.strip())
        if len(temp) != length:
            return False
        return temp
    except:
        return False

def unique(lis, length):
    return len(lis) == len(set(lis)) and len(lis) == length

def check_ans(user_ans, correct_ans):
    position = 0
    ans = changer(user_ans, len(correct_ans))

    if not (ans) or not unique(ans,len(correct_ans)):
        return "wrong answer❗❗ the answer is not contain all answers or any thing repeated answer"
    
    for i in range(len(correct_ans)):
        if ans[i] == correct_ans[i]:
            position += 1
    
    if position == len(user_ans):
        return "correct"
    
    return f"{position}"

async def winMsg(update):
    global winnum
    if winnum in range(1,4):
        await update.message.reply_text(f"\n\n\n🏆🏆🏆     CONGRADULATIONS     🏆🏆🏆 \n YOUR TEAM FINISHED     {winnum}\n\n")
    else:
        await update.message.reply_text(f"\n\n\nYOUR TEAM FINISHED  #{winnum}\n\n")
    
    winnum+=1

async def sendGame4(update, context, chat_id):
    global game4_voice1, game4_voice2
    await update.message.reply_text(games.get("4"))
    voice1 = open(game4_voice1,'rb')
    await context.bot.send_voice(chat_id=chat_id,voice=voice1,caption="ሕዝቡ እንዲህ ይበል : \"እግዚኦ ተሠሃለነ\" ይበሉ")
    await update.message.reply_text("ካህን(ቄስ): \"ሰላም ለኲልክሙ\" ሲሉ")
    voice2 = open(game4_voice2,'rb')
    await context.bot.send_voice(chat_id=chat_id,voice=voice2,caption="ህዝቡ እንዲህ ይበል: \"ምስለ መንፈስከ\" ይበሉ")

    await update.message.reply_text(redirect_puzzle.get("4"))

