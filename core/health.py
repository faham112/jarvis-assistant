import platform
import shutil

from core import logger


def system_health():
    lines = ["OS: " + platform.platform()]
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=0.4)
        ram = psutil.virtual_memory()
        lines.append("CPU: %s%%" % cpu)
        lines.append("RAM used: %s%% (%s GB / %s GB)" % (
            int(ram.percent),
            round((ram.total - ram.available) / (1024 ** 3), 1),
            round(ram.total / (1024 ** 3), 1),
        ))
        hogs = []
        for p in psutil.process_iter(["name", "memory_info"]):
            try:
                rss = p.info["memory_info"].rss if p.info["memory_info"] else 0
                hogs.append((rss, p.info["name"] or "?"))
            except Exception:
                continue
        hogs.sort(reverse=True)
        top = ", ".join("%s" % n for _, n in hogs[:4])
        lines.append("RAM hogs: " + top)
    except Exception:
        lines.append("psutil missing — pip install psutil")

    usage = shutil.disk_usage("/")
    lines.append("Disk free: %s GB" % round(usage.free / (1024 ** 3), 1))
    msg = " | ".join(lines)
    logger.log("system_health", msg)
    return msg
