from typing import Literal

Channel = Literal["system", "email", "whatsapp", "telegram"]


async def dispatch(channel: Channel, title: str, message: str) -> dict:
    payload = {"channel": channel, "title": title, "message": message}

    if channel == "system":
        print(f"[SYSTEM] {title}: {message}")
    elif channel == "email":
        print(f"[EMAIL] {title}: {message}")
    elif channel == "whatsapp":
        print(f"[WHATSAPP] {title}: {message}")
    elif channel == "telegram":
        print(f"[TELEGRAM] {title}: {message}")

    return payload
