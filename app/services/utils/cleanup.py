import re


def clean_ai_response(text: str) -> str:

    if not text:
        return "AI response unavailable."

    text = text.strip()

    # markdown temizliği
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"#+", "", text)

    # fazla boşluk
    text = re.sub(r"\n{3,}", "\n\n", text)

    # yasaklı ifadeler
    banned_phrases = [
        "Tabii ki",
        "Elbette",
        "İşte",
        "Merhaba",
        "Sayın Yetkili",
    ]

    for phrase in banned_phrases:
        text = text.replace(phrase, "")

    return text.strip()  