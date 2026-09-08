import re
WORDS = {
 "theek": "ٹھیک", "hai": "ہے", "haan": "ہاں", "han": "ہاں", "nahi": "نہیں", "nahin": "نہیں",
 "ji": "جی", "acha": "اچھا", "accha": "اچھا", "shukriya": "شکریہ",
 "salaam": "سلام", "salam": "سلام", "time": "وقت", "waqt": "وقت",
 "date": "تاریخ", "tareekh": "تاریخ", "aaj": "آج", "kal": "کل", "abhi": "ابھی",
 "phir": "پھر", "bolo": "بولو", "batao": "بتاؤ", "kya": "کیا", "kyun": "کیوں",
 "kaise": "کیسے", "kese": "کیسے", "kahan": "کہاں", "kab": "کب", "kaun": "کون", "kon": "کون",
 "yeh": "یہ", "woh": "وہ", "wo": "وہ", "main": "میں", "mein": "میں",
 "hum": "ہم", "tum": "تم", "aap": "آپ", "ap": "آپ", "mera": "میرا", "meri": "میری", "mere": "میرے",
 "ho": "ہو", "hain": "ہیں", "tha": "تھا", "thi": "تھی", "karo": "کرو", "kar": "کر",
 "chahiye": "چاہیے", "sakti": "سکتی", "rehti": "رہتی",
 "folder": "فولڈر", "file": "فائل", "system": "سسٹم", "weather": "موسم", "mosam": "موسم",
 "help": "مدد", "note": "نوٹ", "whatsapp": "واٹس ایپ", "mj": "ایم جے",
 "boss": "باس", "sir": "سر", "hogaya": "ہو گیا", "band": "بند", "kholo": "کھولو",
 "karachi": "کراچی", "lahore": "لاہور", "islamabad": "اسلام آباد",
}

def to_urdu(text):
    if not text:
        return "ٹھیک ہے"
    if re.search(r"[\u0600-\u06FF]", text):
        return text
    out = []
    for raw in re.findall(r"[A-Za-z']+|[^A-Za-z']+", text):
        out.append(WORDS.get(raw.lower(), raw))
    return "".join(out)
