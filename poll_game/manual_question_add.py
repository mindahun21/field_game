from app.models import Quiz, User, Question
from app.handlers import register_handler
from app import db_utils
from app.db import access_db
from sqlalchemy.orm import Session

from telegram import(
    Update
)

from telegram.ext import(
    CommandHandler,
    ContextTypes,
)


questions =[
    {
        "question": "የዐቢይ ጾም ስምንተኛው ሳምንት ምን ይባላል?",
        "options": ["ገብርኄር", "ኒቆዲሞስ", "ሆሳዕና", "ደብረ ዘይት"],
        "ans_index": 2
    },
    {
        "question": "የሐዲስ ኪዳን መጻሕፍት ብዛታቸው ስንት ነው?",
        "options": ["27", "46", "35", "18"],
        "ans_index": 2
    },
    {
        "question": "ከሰባቱ ምስጢራተ ቤተክርስቲያን ያልሆነው የትኛው ነው?",
        "options": ["ምስጢረ ቀንዲል", "ምስጢረ ቁርባን", "ምስጢረ ክህነት", "ምስጢረ ትንሳኤ ሙታን"],
        "ans_index": 3
    },
    {
        "question": "ሴቶች በልማደ አንስት(የወር አበባ) ጊዜ የማይከለከሉት ከየትኛው ነው?",
        "options": ["ሩካቤ", "ቤተ መቅደስ መግባት እና ማስቀደስ", "ጠበል መጠጣትና ቅዱሳት መጻህፍትን መንካት", "ቅዱስ ቁርባንን መቀበል"],
        "ans_index": 2
    },
    {
        "question": "ከብሉይ ኪዳን መጻሕፍት ምድብ ውስጥ የማይካታተው የትኛው ነው?",
        "options": ["የመልዕክት መጻሕፍት", "የታሪክ መጻሕፍት", "የሕግ መጻሕፍት", "የትንቢት መጻሕፍት"],
        "ans_index": 0
    },
    {
        "question": "ከአስራ ሁለቱ ሐዋርያት አንዱ የሆነው ማን ነው?",
        "options": ["ቅዱስ ማርቆስ", "ቅዱስ ማቴዎስ", "ቅዱስ ጳውሎስ", "ቅዱስ ሉቃስ"],
        "ans_index": 1
    },
    {
        "question": "በኢትዮጵያ ኦርቶዶክስ ተዋህዶ ቤተክርስቲያን የመጅመሪያው ኢትዮጵያውያዊ ፓትሪያርክ ማን ነበሩ?",
        "options": ["አቡነ ባስልዮስ", "አቡነ ቴዎፍሎስ", "አቡነ ጴጥሮስ", "አቡነ መርቆሬዎስ"],
        "ans_index": 0
    },
    {
        "question": "በማቴዎስ ወንጌል የጌታችንና መድኃኒታችን ኢየሱስ ክርስቶስ የትውልድ ሐረግ ውስጥ የተጠቀሰችው ሴት ማን ናት?",
        "options": ["ሩት", "ሳራ", "ዮዲት", "አስቴር"],
        "ans_index": 0
    },
    {
        "question": "የ13ቱ ሕማማተ መስቀል ውስጥ የማይገባው የማይቆጠረው የቱ ነው?",
        "options": ["ተከይዶ በእግረ አይሁድ (በአይሁድ እግር መረገጡ)", "አክሊለ ሦክ (የእሾህ አክሊል)", "ወሪቀ ምራቅ (የምራቅ መተፋት) "," ተቀሥፎ ዘባን (ጀርባን መገረፍ)"],
        "ans_index": 0
    },
    {
        "question": "በኢትዮጵያ ቤተክርስቲያን አስተምህሮ እመቤታችን ቅድስት ድንግል ማርያም የተጸነሰችው መቼ ነው?",
        "options": ["ጥር 21", "መስከረም 21", "ነሐሴ 7", "ግንቦት 1"],
        "ans_index": 2
    },
    {
        "question": "ቅዱሳን አዳምና ሔዋን አትብሉ የተባሉትን ዕፀ በለስ በልተው ከገነት ከመውጣታቸው በፊት ገነት ለስንት አመት ቆዩ?",
        "options": ["ለ 10 ዓመት", "ለ 15 ዓመት", "ለ 20 ዓመት", "ለ 7 ዓመት"],
        "ans_index": 3
    },
    {
        "question": "የ\"ሥላሴ\" የግብር ሶስትነት እንዴት ነው?",
        "options": ["አብ፣ ወልድ፣ መንፈስ ቅዱስ", "ልብነት፣ ቃልነት፣ እስትንፋስነት", "ወላዲ፣ ተወላዲ፣ ሰራጺ", "አካል፣ ገጽ፣ መልክ"],
        "ans_index": 2
    },
    {
        "question": "በያስቆርቱ ይሁዳ የተተካው ሐዋርያ ማን ይባላል?",
        "options": ["ፊልጶስ", "ፊልሞና", "ማትያስ", "ቶማስ"],
        "ans_index": 2
    },
    {
        "question": "በእግዚአብሔር ትዕዛዝ ቅዱስ ዳዊትን ቀብቶ ያነገሠው ማን ነው?",
        "options": ["ነቢዩ ዳንኤል", "ነቢዩ ናታን", "ነቢዩ ሳሙኤል", "ነቢዩ ኤርሚያስ"],
        "ans_index": 2
    }
]

@access_db
async def add_questions(update:Update, context: ContextTypes.DEFAULT_TYPE,db:Session=None):
    username="Mindahun21"
    admin = await db_utils.get_entry(User,db=db,username=username)

    global questions

    quiz = Quiz(
        name="robel_quiz",
        subject="hmamat questions",
        creator_id=admin.id
    )
    await db_utils.add_obj(quiz,db=db)


    for question in questions:
        question_obj = Question(
            question=question["question"],
            options=question["options"],
            ans_index=question["ans_index"],
            quiz_id=quiz.id,
        )

        await db_utils.add_obj(question_obj,db=db)


handler = CommandHandler("manual_add",add_questions)
register_handler(handler)