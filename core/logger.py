from datetime import datetime
from config import DATA_DIR


def log(action, detail=""):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "actions.log"
    line = "%s  %s  %s\n" % (datetime.now().isoformat(timespec="seconds"), action, detail)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
