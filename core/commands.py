import wikipedia
from duckduckgo_search import DDGS

from core.system import now_text, date_text, open_url, open_app, search_web, youtube


def _wiki(query: str) -> str:
    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(query, sentences=2)
    except Exception:
        return f"I could not find a short Wikipedia answer for {query}."


def _web_answer(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=1))
        if results:
            item = results[0]
            title = item.get("title", "")
            body = item.get("body", "")
            return f"{title}. {body}"
    except Exception:
        pass
    search_web(query)
    return "I opened a web search for that."


def handle(command: str) -> str:
    q = command.lower().strip()

    if any(w in q for w in ("exit", "quit", "goodbye", "sleep", "band karo", "band ho")):
        return "__EXIT__"

    if "your name" in q or "tumhara naam" in q:
        return "I am Jarvis, your personal assistant."

    if "time" in q or "kitna baja" in q:
        return f"The time is {now_text()}."

    if "date" in q or "tareekh" in q or "aaj ka din" in q:
        return f"Today is {date_text()}."

    if q.startswith("open ") or q.startswith("kholo "):
        target = q.split(" ", 1)[1]
        if target.startswith("http") or "." in target:
            open_url(target if target.startswith("http") else f"https://{target}")
            return f"Opening {target}."
        return open_app(target)

    if "youtube" in q:
        query = q.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
        youtube(query or "music")
        return "Opening YouTube."

    if q.startswith("search ") or q.startswith("google ") or "search karo" in q:
        query = q.replace("search", "").replace("google", "").replace("karo", "").strip()
        search_web(query)
        return f"Searching for {query}."

    if "wikipedia" in q or "who is" in q or "what is" in q or "kaun hai" in q:
        topic = (
            q.replace("wikipedia", "")
            .replace("who is", "")
            .replace("what is", "")
            .replace("kaun hai", "")
            .strip()
        )
        return _wiki(topic or q)

    if "joke" in q or "joke sunao" in q:
        return "Why do programmers prefer dark mode? Because light attracts bugs."

    if "hello" in q or "hi jarvis" in q or "salam" in q or "assalam" in q:
        return "Hello. I am online and ready."

    return _web_answer(q)
