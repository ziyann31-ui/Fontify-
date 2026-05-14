import logging
import os
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ChatMemberHandler, filters, ContextTypes
)

# ============================================================
#                     CONFIGURATION
# ============================================================

BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = int(os.environ["OWNER_ID"])
BOT_USERNAME = os.environ["BOT_USERNAME"]

# ============================================================
#                     DATABASE (MongoDB)
# ============================================================

from pymongo import MongoClient

MONGO_URI = os.environ["MONGO_URI"]

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client["fontify_db"]
        self.users = self.db["users"]
        self.groups = self.db["groups"]
        self.usage_log = self.db["usage_log"]

    def add_user(self, user_id, username, name):
        uid = str(user_id)
        existing = self.users.find_one({"user_id": uid})
        if not existing:
            self.users.insert_one({
                "user_id": uid,
                "username": username,
                "name": name,
                "usage_count": 0,
                "joined_date": datetime.now().strftime("%Y-%m-%d"),
            })
        else:
            self.users.update_one(
                {"user_id": uid},
                {"$set": {"username": username, "name": name}}
            )

    def log_usage(self, user_id):
        uid = str(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        self.users.update_one(
            {"user_id": uid},
            {"$inc": {"usage_count": 1}, "$set": {"last_used": today}}
        )
        self.usage_log.insert_one({"user_id": user_id, "date": today})

    def get_user_stats(self, user_id):
        uid = str(user_id)
        user = self.users.find_one({"user_id": uid})
        if user:
            return {"usage_count": user.get("usage_count", 0), "joined_date": user.get("joined_date", "N/A"), "last_used": user.get("last_used", "N/A")}
        return {"usage_count": 0, "joined_date": "N/A"}

    def get_global_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        total_users = self.users.count_documents({})
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$usage_count"}}}]
        result = list(self.users.aggregate(pipeline))
        total_usage = result[0]["total"] if result else 0
        today_logs = list(self.usage_log.find({"date": today}))
        today_users = len(set(l["user_id"] for l in today_logs))
        today_usage = len(today_logs)
        return {
            "total_users": total_users,
            "total_usage": total_usage,
            "today_users": today_users,
            "today_usage": today_usage,
        }

    def add_group(self, chat_id, title):
        gid = str(chat_id)
        self.groups.update_one(
            {"chat_id": gid},
            {"$set": {"chat_id": gid, "title": title, "added_date": datetime.now().strftime("%Y-%m-%d")}},
            upsert=True
        )

    def remove_group(self, chat_id):
        self.groups.delete_one({"chat_id": str(chat_id)})

    def get_all_groups(self):
        return [int(g["chat_id"]) for g in self.groups.find()]

    def get_all_users(self):
        return [int(u["user_id"]) for u in self.users.find()]

    def get_recent_users(self, limit=10):
        return list(self.users.find().sort("usage_count", -1).limit(limit))

db = Database()

# ============================================================
#                     FONTS (37+)
# ============================================================

ALPHA = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def make_map(normal, styled):
    return dict(zip(normal, styled))

MAPS = {
    "bold": make_map(ALPHA,
        "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"),
    "italic": make_map(ALPHA,
        "𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍0123456789"),
    "bold_italic": make_map(ALPHA,
        "𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"),
    "cursive": make_map(ALPHA,
        "𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"),
    "cursive2": make_map(ALPHA,
        "𝒶𝒷𝒸𝒹𝑒𝒻𝑔𝒽𝒾𝒿𝓀𝓁𝓂𝓃𝑜𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵0123456789"),
    "fraktur": make_map(ALPHA,
        "𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ0123456789"),
    "fraktur_bold": make_map(ALPHA,
        "𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅0123456789"),
    "double_struck": make_map(ALPHA,
        "𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"),
    "monospace": make_map(ALPHA,
        "𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"),
    "sans": make_map(ALPHA,
        "𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫"),
    "sans_bold": make_map(ALPHA,
        "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"),
    "sans_italic": make_map(ALPHA,
        "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡0123456789"),
    "sans_bold_italic": make_map(ALPHA,
        "𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕0123456789"),
}

def map_convert(text, mapping):
    return "".join(mapping.get(c, c) for c in text)

def small_caps(text):
    sc = {'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ',
          'i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ',
          'q':'Q','r':'ʀ','s':'ꜱ','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x',
          'y':'ʏ','z':'ᴢ'}
    return "".join(sc.get(c.lower(), c) for c in text)

def wide_text(text):
    result = ""
    for c in text:
        if 'a' <= c <= 'z':
            result += chr(ord(c) - ord('a') + 0xFF41)
        elif 'A' <= c <= 'Z':
            result += chr(ord(c) - ord('A') + 0xFF21)
        elif '0' <= c <= '9':
            result += chr(ord(c) - ord('0') + 0xFF10)
        elif c == ' ':
            result += '　'
        else:
            result += c
    return result

def upside_down(text):
    flip = {'a':'ɐ','b':'q','c':'ɔ','d':'p','e':'ǝ','f':'ɟ','g':'ƃ','h':'ɥ',
            'i':'ı','j':'ɾ','k':'ʞ','l':'l','m':'ɯ','n':'u','o':'o','p':'d',
            'q':'b','r':'ɹ','s':'s','t':'ʇ','u':'n','v':'ʌ','w':'ʍ','x':'x',
            'y':'ʎ','z':'z','A':'∀','B':'q','C':'Ɔ','D':'p','E':'Ǝ','F':'Ⅎ',
            'G':'פ','H':'H','I':'I','J':'ɾ','K':'ʞ','L':'˥','M':'W','N':'N',
            'O':'O','P':'Ԁ','Q':'Q','R':'ɹ','S':'S','T':'┴','U':'∩','V':'Λ',
            'W':'M','X':'X','Y':'⅄','Z':'Z','0':'0','1':'Ɩ','2':'ᄅ','3':'Ɛ',
            '4':'ㄣ','5':'ϛ','6':'9','7':'ㄥ','8':'8','9':'6',' ':' '}
    return "".join(flip.get(c, c) for c in reversed(text))

def mirror_text(text):
    mirror = {'a':'ɒ','b':'d','d':'b','e':'ɘ','f':'ʇ','g':'ϱ','h':'d','j':'ᒐ',
              'k':'ʞ','n':'ᴎ','p':'q','q':'p','r':'ɿ','s':'ƨ','y':'γ','z':'ƹ',
              'B':'ᗺ','C':'Ɔ','D':'ᗡ','E':'Ǝ','F':'ᖷ','G':'ᓜ','J':'Ⴑ','K':'ᴲ',
              'N':'ᴎ','P':'ꟼ','Q':'Ọ','R':'Я','S':'Ƨ','Z':'Ƹ'}
    return "".join(mirror.get(c, c) for c in reversed(text))

def zalgo_text(text):
    zalgo_chars = ['\u0300','\u0301','\u0302','\u0303','\u0304','\u0305','\u0306',
                   '\u0307','\u0308','\u030A','\u030B','\u030D','\u030E','\u0311',
                   '\u0340','\u0341','\u0342','\u0343','\u0344','\u0346','\u034A']
    result = ""
    for c in text:
        result += c
        if c != ' ':
            for _ in range(random.randint(1, 4)):
                result += random.choice(zalgo_chars)
    return result

def strikethrough(text):
    return "".join(c + "\u0336" if c != " " else c for c in text)

def underline_text(text):
    return "".join(c + "\u0332" if c != " " else c for c in text)

def overline_text(text):
    return "".join(c + "\u0305" if c != " " else c for c in text)

def circle_text(text):
    circ = {'a':'ⓐ','b':'ⓑ','c':'ⓒ','d':'ⓓ','e':'ⓔ','f':'ⓕ','g':'ⓖ','h':'ⓗ',
            'i':'ⓘ','j':'ⓙ','k':'ⓚ','l':'ⓛ','m':'ⓜ','n':'ⓝ','o':'ⓞ','p':'ⓟ',
            'q':'ⓠ','r':'ⓡ','s':'ⓢ','t':'ⓣ','u':'ⓤ','v':'ⓥ','w':'ⓦ','x':'ⓧ',
            'y':'ⓨ','z':'ⓩ','A':'Ⓐ','B':'Ⓑ','C':'Ⓒ','D':'Ⓓ','E':'Ⓔ','F':'Ⓕ',
            'G':'Ⓖ','H':'Ⓗ','I':'Ⓘ','J':'Ⓙ','K':'Ⓚ','L':'Ⓛ','M':'Ⓜ','N':'Ⓝ',
            'O':'Ⓞ','P':'Ⓟ','Q':'Ⓠ','R':'Ⓡ','S':'Ⓢ','T':'Ⓣ','U':'Ⓤ','V':'Ⓥ',
            'W':'Ⓦ','X':'Ⓧ','Y':'Ⓨ','Z':'Ⓩ','0':'⓪','1':'①','2':'②','3':'③',
            '4':'④','5':'⑤','6':'⑥','7':'⑦','8':'⑧','9':'⑨'}
    return "".join(circ.get(c, c) for c in text)

def filled_circle(text):
    circ = {'a':'🅐','b':'🅑','c':'🅒','d':'🅓','e':'🅔','f':'🅕','g':'🅖','h':'🅗',
            'i':'🅘','j':'🅙','k':'🅚','l':'🅛','m':'🅜','n':'🅝','o':'🅞','p':'🅟',
            'q':'🅠','r':'🅡','s':'🅢','t':'🅣','u':'🅤','v':'🅥','w':'🅦','x':'🅧',
            'y':'🅨','z':'🅩','A':'🅐','B':'🅑','C':'🅒','D':'🅓','E':'🅔','F':'🅕',
            'G':'🅖','H':'🅗','I':'🅘','J':'🅙','K':'🅚','L':'🅛','M':'🅜','N':'🅝',
            'O':'🅞','P':'🅟','Q':'🅠','R':'🅡','S':'🅢','T':'🅣','U':'🅤','V':'🅥',
            'W':'🅦','X':'🅧','Y':'🅨','Z':'🅩'}
    return "".join(circ.get(c, c) for c in text)

def square_text(text):
    sq = {'a':'🄰','b':'🄱','c':'🄲','d':'🄳','e':'🄴','f':'🄵','g':'🄶','h':'🄷',
          'i':'🄸','j':'🄹','k':'🄺','l':'🄻','m':'🄼','n':'🄽','o':'🄾','p':'🄿',
          'q':'🅀','r':'🅁','s':'🅂','t':'🅃','u':'🅄','v':'🅅','w':'🅆','x':'🅇',
          'y':'🅈','z':'🅉','A':'🄰','B':'🄱','C':'🄲','D':'🄳','E':'🄴','F':'🄵',
          'G':'🄶','H':'🄷','I':'🄸','J':'🄹','K':'🄺','L':'🄻','M':'🄼','N':'🄽',
          'O':'🄾','P':'🄿','Q':'🅀','R':'🅁','S':'🅂','T':'🅃','U':'🅄','V':'🅅',
          'W':'🅆','X':'🅇','Y':'🅈','Z':'🅉'}
    return "".join(sq.get(c, c) for c in text)

def superscript(text):
    sup = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷',
           '8':'⁸','9':'⁹','a':'ᵃ','b':'ᵇ','c':'ᶜ','d':'ᵈ','e':'ᵉ','f':'ᶠ',
           'g':'ᵍ','h':'ʰ','i':'ⁱ','j':'ʲ','k':'ᵏ','l':'ˡ','m':'ᵐ','n':'ⁿ',
           'o':'ᵒ','p':'ᵖ','r':'ʳ','s':'ˢ','t':'ᵗ','u':'ᵘ','v':'ᵛ','w':'ʷ',
           'x':'ˣ','y':'ʸ','z':'ᶻ','A':'ᴬ','B':'ᴮ','D':'ᴰ','E':'ᴱ','G':'ᴳ',
           'H':'ᴴ','I':'ᴵ','J':'ᴶ','K':'ᴷ','L':'ᴸ','M':'ᴹ','N':'ᴺ','O':'ᴼ',
           'P':'ᴾ','R':'ᴿ','T':'ᵀ','U':'ᵁ','V':'ⱽ','W':'ᵂ'}
    return "".join(sup.get(c, c) for c in text)

def subscript(text):
    sub = {'0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇',
           '8':'₈','9':'₉','a':'ₐ','e':'ₑ','h':'ₕ','i':'ᵢ','j':'ⱼ','k':'ₖ',
           'l':'ₗ','m':'ₘ','n':'ₙ','o':'ₒ','p':'ₚ','r':'ᵣ','s':'ₛ','t':'ₜ',
           'u':'ᵤ','v':'ᵥ','x':'ₓ'}
    return "".join(sub.get(c, c) for c in text)

def leet_speak(text):
    leet = {'a':'4','e':'3','g':'9','i':'1','l':'1','o':'0','s':'5','t':'7','z':'2',
            'A':'4','E':'3','G':'9','I':'1','L':'1','O':'0','S':'5','T':'7','Z':'2'}
    return "".join(leet.get(c, c) for c in text)

def fullwidth(text):
    c2 = {'a':'ａ','b':'ｂ','c':'ｃ','d':'ｄ','e':'ｅ','f':'ｆ','g':'ｇ','h':'ｈ',
          'i':'ｉ','j':'ｊ','k':'ｋ','l':'ｌ','m':'ｍ','n':'ｎ','o':'ｏ','p':'ｐ',
          'q':'ｑ','r':'ｒ','s':'ｓ','t':'ｔ','u':'ｕ','v':'ｖ','w':'ｗ','x':'ｘ',
          'y':'ｙ','z':'ｚ','A':'Ａ','B':'Ｂ','C':'Ｃ','D':'Ｄ','E':'Ｅ','F':'Ｆ',
          'G':'Ｇ','H':'Ｈ','I':'Ｉ','J':'Ｊ','K':'Ｋ','L':'Ｌ','M':'Ｍ','N':'Ｎ',
          'O':'Ｏ','P':'Ｐ','Q':'Ｑ','R':'Ｒ','S':'Ｓ','T':'Ｔ','U':'Ｕ','V':'Ｖ',
          'W':'Ｗ','X':'Ｘ','Y':'Ｙ','Z':'Ｚ'}
    return "".join(c2.get(c, c) for c in text)

def glitch_text(text):
    glitch_chars = ['̾','̈','̧','̨','̡','̢','̛','̗','̘','̙','̚']
    result = ""
    for c in text:
        result += c
        if c != ' ' and random.random() > 0.5:
            result += random.choice(glitch_chars)
    return result

def bubble_text(text):
    bubbles = {'a':'꒒','b':'ꋰ','c':'ꉓ','d':'꒯','e':'꒷','f':'ꊰ','g':'ꃳ','h':'꒣',
               'i':'ꂑ','j':'ꀤ','k':'꒐','l':'꒒','m':'ꂵ','n':'ꈤ','o':'ꂦ','p':'ꉣ',
               'q':'꒘','r':'ꋪ','s':'ꉔ','t':'꓄','u':'ꋩ','v':'ꃴ','w':'ꅐ','x':'ꊼ',
               'y':'ꌦ','z':'ꊶ','A':'꒒','B':'ꋰ','C':'ꉓ','D':'꒯','E':'꒷','F':'ꊰ',
               'G':'ꃳ','H':'꒣','I':'ꂑ','J':'ꀤ','K':'꒐','L':'꒒','M':'ꂵ','N':'ꈤ',
               'O':'ꂦ','P':'ꉣ','Q':'꒘','R':'ꋪ','S':'ꉔ','T':'꓄','U':'ꋩ','V':'ꃴ',
               'W':'ꅐ','X':'ꊼ','Y':'ꌦ','Z':'ꊶ'}
    return "".join(bubbles.get(c, c) for c in text)

def creepy_text(text):
    creepy = {'a':'ą','b':'ҍ','c':'ç','d':'ժ','e':'ҽ','f':'ƒ','g':'ց','h':'հ',
              'i':'ì','j':'ʝ','k':'κ','l':'Ӏ','m':'ʍ','n':'ղ','o':'օ','p':'ρ',
              'q':'զ','r':'ɾ','s':'ʂ','t':'է','u':'մ','v':'ѵ','w':'ա','x':'×',
              'y':'վ','z':'Հ','A':'Ą','B':'Ҍ','C':'Ç','D':'Ժ','E':'Ҽ','F':'Ƒ',
              'G':'Ց','H':'Հ','I':'Ì','J':'Ʝ','K':'Κ','L':'Լ','M':'Μ','N':'Ν',
              'O':'Օ','P':'Ρ','Q':'Զ','R':'Ʀ','S':'Ʂ','T':'Է','U':'Մ','V':'Վ',
              'W':'Ա','X':'×','Y':'Վ','Z':'Հ'}
    return "".join(creepy.get(c, c) for c in text)

def matrix_text(text):
    matrix = {'a':'ム','b':'乃','c':'匚','d':'刀','e':'乇','f':'下','g':'ム','h':'卄',
              'i':'工','j':'丿','k':'长','l':'乙','m':'爪','n':'几','o':'口','p':'尸',
              'q':'夕','r':'尺','s':'丂','t':'丅','u':'凵','v':'リ','w':'山','x':'乂',
              'y':'ㄚ','z':'乙','A':'ム','B':'乃','C':'匚','D':'刀','E':'乇','F':'下',
              'G':'ム','H':'卄','I':'工','J':'丿','K':'长','L':'乙','M':'爪','N':'几',
              'O':'口','P':'尸','Q':'夕','R':'尺','S':'丂','T':'丅','U':'凵','V':'リ',
              'W':'山','X':'乂','Y':'ㄚ','Z':'乙'}
    return "".join(matrix.get(c, c) for c in text)

def runic_text(text):
    runes = {'a':'ᚨ','b':'ᛒ','c':'ᚲ','d':'ᛞ','e':'ᛖ','f':'ᚠ','g':'ᚷ','h':'ᚺ',
             'i':'ᛁ','j':'ᛃ','k':'ᚲ','l':'ᛚ','m':'ᛗ','n':'ᚾ','o':'ᛟ','p':'ᛈ',
             'q':'ᚴ','r':'ᚱ','s':'ᛊ','t':'ᛏ','u':'ᚢ','v':'ᚡ','w':'ᚹ','x':'ᚢ',
             'y':'ᛃ','z':'ᛉ'}
    return "".join(runes.get(c.lower(), c) for c in text)

def space_out(text):
    return " ".join(text)

def dots_between(text):
    return "·".join(text)

def star_between(text):
    return "★".join(text)

def wave_text(text):
    return "~≈~" + text + "~≈~"

def morse_code(text):
    morse = {'a':'.-','b':'-...','c':'-.-.','d':'-..','e':'.','f':'..-.','g':'--.','h':'....',
             'i':'..','j':'.---','k':'-.-','l':'.-..','m':'--','n':'-.','o':'---','p':'.--.',
             'q':'--.-','r':'.-.','s':'...','t':'-','u':'..-','v':'...-','w':'.--','x':'-..-',
             'y':'-.--','z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-',
             '5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',
             'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....',
             'I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.',
             'Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-',
             'Y':'-.--','Z':'--..'}
    return " ".join(morse.get(c, c) for c in text)

FONTS = {
    "bold":              lambda t: map_convert(t, MAPS["bold"]),
    "italic":            lambda t: map_convert(t, MAPS["italic"]),
    "bold italic":       lambda t: map_convert(t, MAPS["bold_italic"]),
    "cursive":           lambda t: map_convert(t, MAPS["cursive"]),
    "cursive 2":         lambda t: map_convert(t, MAPS["cursive2"]),
    "fraktur":           lambda t: map_convert(t, MAPS["fraktur"]),
    "fraktur bold":      lambda t: map_convert(t, MAPS["fraktur_bold"]),
    "double struck":     lambda t: map_convert(t, MAPS["double_struck"]),
    "monospace":         lambda t: map_convert(t, MAPS["monospace"]),
    "sans":              lambda t: map_convert(t, MAPS["sans"]),
    "sans bold":         lambda t: map_convert(t, MAPS["sans_bold"]),
    "sans italic":       lambda t: map_convert(t, MAPS["sans_italic"]),
    "sans bold italic":  lambda t: map_convert(t, MAPS["sans_bold_italic"]),
    "small caps":        small_caps,
    "wide":              wide_text,
    "upside down":       upside_down,
    "mirror":            mirror_text,
    "zalgo":             zalgo_text,
    "strikethrough":     strikethrough,
    "underline":         underline_text,
    "overline":          overline_text,
    "circle":            circle_text,
    "filled circle":     filled_circle,
    "square":            square_text,
    "superscript":       superscript,
    "subscript":         subscript,
    "leet":              leet_speak,
    "morse":             morse_code,
    "spaced":            space_out,
    "dots":              dots_between,
    "stars":             star_between,
    "wave":              wave_text,
    "glitch":            glitch_text,
    "bubble":            bubble_text,
    "creepy":            creepy_text,
    "matrix":            matrix_text,
    "runic":             runic_text,
    "fullwidth":         fullwidth,
}

FONT_CATEGORIES = {
    "bold":    ["bold","italic","bold italic","sans bold","sans italic","sans bold italic","double struck","monospace"],
    "cursive": ["cursive","cursive 2","fraktur","fraktur bold","sans","creepy"],
    "small":   ["small caps","superscript","subscript","spaced","dots"],
    "symbols": ["circle","filled circle","square","strikethrough","underline","overline","stars","wave"],
    "fancy":   ["wide","fullwidth","bubble","matrix","runic","leet","morse","upside down","mirror","small caps"],
    "glitch":  ["zalgo","glitch","upside down","mirror","strikethrough","creepy","matrix"],
}
FONT_CATEGORIES["all"] = list(FONTS.keys())

CATEGORY_LABELS = {
    "bold":    "🔤 Bold & Italic",
    "cursive": "✍️ Cursive & Fancy",
    "small":   "🔡 Small & Spaced",
    "symbols": "🔷 Symbols & Effects",
    "fancy":   "✨ Fancy & Exotic",
    "glitch":  "👾 Glitch & Creepy",
    "all":     "📋 All Fonts",
}

def convert_text(text, font_name):
    fn = font_name.lower()
    if fn in FONTS:
        return FONTS[fn](text)
    return text

# ============================================================
#                     LOGGING
# ============================================================

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
#                     HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username or "", user.first_name or "")
    keyboard = [
        [InlineKeyboardButton("✨ Fonts List", callback_data="fonts_list"),
         InlineKeyboardButton("📊 My Stats", callback_data="my_stats")],
        [InlineKeyboardButton("ℹ️ How to Use", callback_data="how_to_use"),
         InlineKeyboardButton("📢 Channel", url="https://t.me/botverse_updates")],
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
    ]
    await update.message.reply_text(
        f"🎨 *Welcome to Font Crafter Bot!*\n\n"
        f"Hello {user.first_name}! 👋\n\n"
        f"Transform your boring text into *amazing stylish fonts!*\n\n"
        f"🔥 *{len(FONTS)}+ Unique Font Styles Available!*\n\n"
        f"➡️ Just type any text to get started...",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message
    text = message.text.strip()
    if text.startswith("/"):
        return

    chat_type = message.chat.type
    if chat_type in ("group", "supergroup"):
        bot_username = f"@{BOT_USERNAME}"
        is_mentioned = bot_username.lower() in text.lower()
        is_reply_to_bot = (
            message.reply_to_message is not None
            and message.reply_to_message.from_user is not None
            and message.reply_to_message.from_user.username == BOT_USERNAME
        )
        if not is_mentioned and not is_reply_to_bot:
            return
        text = text.replace(bot_username, "").replace(bot_username.lower(), "").strip()
        if not text:
            await message.reply_text(f"Text bhi likho! Jaise: @{BOT_USERNAME} Hello World")
            return

    db.add_user(user.id, user.username or "", user.first_name or "")
    db.log_usage(user.id)

    preview = text[:30]
    keyboard = [
        [InlineKeyboardButton("🔤 Bold & Italic",    callback_data=f"cat_bold|{preview}"),
         InlineKeyboardButton("✍️ Cursive",          callback_data=f"cat_cursive|{preview}")],
        [InlineKeyboardButton("🔡 Small & Spaced",   callback_data=f"cat_small|{preview}"),
         InlineKeyboardButton("🔷 Symbols",          callback_data=f"cat_symbols|{preview}")],
        [InlineKeyboardButton("✨ Fancy & Exotic",   callback_data=f"cat_fancy|{preview}"),
         InlineKeyboardButton("👾 Glitch & Creepy",  callback_data=f"cat_glitch|{preview}")],
        [InlineKeyboardButton("📋 All Fonts",        callback_data=f"cat_all|{preview}")],
    ]
    await update.message.reply_text(
        f"🎨 *Choose a font category for:*\n`{text[:50]}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("cat_"):
        parts = data.split("|", 1)
        cat = parts[0].replace("cat_", "")
        text = parts[1] if len(parts) > 1 else ""
        fonts_in_cat = FONT_CATEGORIES.get(cat, [])
        keyboard = []
        row = []
        for i, font in enumerate(fonts_in_cat):
            converted = convert_text(text, font)
            label = converted[:20] if len(converted) > 20 else converted
            row.append(InlineKeyboardButton(label, callback_data=f"font_{font}|{text}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"back_main|{text}")])
        await query.edit_message_text(
            f"🎨 *{CATEGORY_LABELS.get(cat, cat.title())}*\n\nTap a style to copy it:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("font_"):
        parts = data.split("|", 1)
        font_key = parts[0].replace("font_", "")
        text = parts[1] if len(parts) > 1 else ""
        result = convert_text(text, font_key)
        keyboard = [
            [InlineKeyboardButton("⬅️ Back to Categories", callback_data=f"back_main|{text}")],
        ]
        await query.edit_message_text(
            f"✅ *{font_key.title()}*\n\n`{result}`\n\n_Tap the text above to copy it!_",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data.startswith("back_main|"):
        text = data.replace("back_main|", "")
        preview = text[:30]
        keyboard = [
            [InlineKeyboardButton("🔤 Bold & Italic",   callback_data=f"cat_bold|{preview}"),
             InlineKeyboardButton("✍️ Cursive",         callback_data=f"cat_cursive|{preview}")],
            [InlineKeyboardButton("🔡 Small & Spaced",  callback_data=f"cat_small|{preview}"),
             InlineKeyboardButton("🔷 Symbols",         callback_data=f"cat_symbols|{preview}")],
            [InlineKeyboardButton("✨ Fancy & Exotic",  callback_data=f"cat_fancy|{preview}"),
             InlineKeyboardButton("👾 Glitch & Creepy", callback_data=f"cat_glitch|{preview}")],
            [InlineKeyboardButton("📋 All Fonts",       callback_data=f"cat_all|{preview}")],
        ]
        await query.edit_message_text(
            f"🎨 *Choose a font category for:*\n`{text}`",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif data == "my_stats":
        user = query.from_user
        stats = db.get_user_stats(user.id)
        await query.edit_message_text(
            f"📊 *Your Stats*\n\n"
            f"👤 Name: {user.first_name}\n"
            f"🔢 Total Uses: {stats.get('usage_count', 0)}\n"
            f"📅 Joined: {stats.get('joined_date', 'N/A')}\n"
            f"🕐 Last Used: {stats.get('last_used', 'N/A')}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]),
            parse_mode="Markdown"
        )

    elif data == "fonts_list":
        font_list = "\n".join(f"• {f}" for f in FONTS.keys())
        await query.edit_message_text(
            f"🎨 *All Available Fonts ({len(FONTS)})*\n\n{font_list}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]),
            parse_mode="Markdown"
        )

    elif data == "how_to_use":
        await query.edit_message_text(
            "ℹ️ *How to Use Font Crafter Bot*\n\n"
            "1️⃣ Just *type any text* in the chat\n"
            "2️⃣ Choose a *font category*\n"
            "3️⃣ Tap a *font style* you like\n"
            "4️⃣ *Tap the result* to copy it\n"
            "5️⃣ Paste it *anywhere* you want! 🎉\n\n"
            "💡 *Tip:* Works in groups too!\n"
            "Add me to your group and use the same way.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]]),
            parse_mode="Markdown"
        )

    elif data == "back_start":
        user = query.from_user
        keyboard = [
            [InlineKeyboardButton("✨ Fonts List", callback_data="fonts_list"),
             InlineKeyboardButton("📊 My Stats", callback_data="my_stats")],
            [InlineKeyboardButton("ℹ️ How to Use", callback_data="how_to_use"),
             InlineKeyboardButton("📢 Channel", url="https://t.me/botverse_updates")],
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        ]
        await query.edit_message_text(
            f"🎨 *Welcome to Font Crafter Bot!*\n\n"
            f"Hello {user.first_name}! 👋\n\n"
            f"Transform your boring text into *amazing stylish fonts!*\n\n"
            f"🔥 *{len(FONTS)}+ Unique Font Styles Available!*\n\n"
            f"➡️ Just type any text to get started...",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


# ============================================================
#                  GROUP JOIN / LEAVE HANDLER
# ============================================================

async def track_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if not result:
        return
    chat = result.chat
    new_status = result.new_chat_member.status
    if chat.type in ("group", "supergroup", "channel"):
        if new_status in ("member", "administrator"):
            db.add_group(chat.id, chat.title or "")
            logger.info(f"Added to group: {chat.title} ({chat.id})")
        elif new_status in ("left", "kicked", "banned"):
            db.remove_group(chat.id)
            logger.info(f"Removed from group: {chat.title} ({chat.id})")


# ============================================================
#                  OWNER / ADMIN COMMANDS
# ============================================================

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return
    s = db.get_global_stats()
    top = db.get_recent_users(5)
    top_text = "\n".join(
        f"  {i+1}. {u.get('name','?')} (@{u.get('username','?')}) — {u.get('usage_count',0)} uses"
        for i, u in enumerate(top)
    )
    await update.message.reply_text(
        f"📊 Bot Statistics\n\n"
        f"👥 Total Users: {s['total_users']}\n"
        f"📈 Total Usage: {s['total_usage']}\n"
        f"🗓 Today Users: {s['today_users']}\n"
        f"⚡ Today Usage: {s['today_usage']}\n\n"
        f"🏆 Top 5 Users:\n{top_text}"
    )


async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    users = db.get_all_users()
    groups = db.get_all_groups()
    all_chats = users + groups
    sent, failed = 0, 0
    for cid in all_chats:
        try:
            await context.bot.send_message(chat_id=cid, text=msg)
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(
        f"✅ Broadcast done!\n"
        f"👤 Users: {len(users)} | 👥 Groups: {len(groups)}\n"
        f"📤 Sent: {sent} | ❌ Failed: {failed}"
    )


async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return
    users = db.get_recent_users(10)
    lines = []
    for u in users:
        lines.append(f"• {u.get('name','?')} (@{u.get('username','?')}) — {u.get('usage_count',0)} uses")
    await update.message.reply_text(
        "👥 Top Users\n\n" + "\n".join(lines)
    )


# ============================================================
#                     MAIN
# ============================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(ChatMemberHandler(track_group, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast_cmd))
    app.add_handler(CommandHandler("users", users_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()