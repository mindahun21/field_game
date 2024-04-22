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
            print("length is not wright")
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
        print("not unique.... answer")
        return "wrong answer❗❗ the answer is not contain all answers or any thing repeated answer"
    
    for i in range(len(correct_ans)):
        if ans[i] == correct_ans[i]:
            position += 1
    
    if position == len(user_ans):
        print("correct answer")
        return "correct"
    
    print("position is ......")
    
    return f"{position}"

async def winMsg(update):
    global winnum
    if winnum in range(1,4):
        await update.message.reply_text(f"\n\n\n🏆🏆🏆congradulations🏆🏆🏆 \n YOUR TEAM FINISHED {winnum}\n\n")
    else:
        await update.message.reply_text(f"\n\n\nYOUR TEAM FINISHED  #{winnum}\n\n")
    
    winnum+=1

async def sendVoice(context, chat_id,voice_file:str):
    voice = open(voice_file,'rb')
    await context.bot.send_voice(chat_id=chat_id,voice=voice)
