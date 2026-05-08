from __future__ import annotations

import os
import plistlib
import subprocess
from pathlib import Path

import browser_cookie3


LOGIN_URL = "https://www.4d4y.com/forum/forumdisplay.php?fid=2"

CHROME_INFO_PLIST_PATHS = (
    Path("/Applications/Google Chrome.app/Contents/Info.plist"),
    Path.home() / "Applications/Google Chrome.app/Contents/Info.plist",
)


def default_cookie_path() -> Path:
    return _config_path("cookie")


def default_user_agent_path() -> Path:
    return _config_path("user-agent")


def _config_path(name: str) -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "hipda" / name
    return Path.home() / ".config" / "hipda" / name


def normalize_cookie(cookie: str) -> str:
    cookie = cookie.strip()
    if cookie.lower().startswith("cookie:"):
        cookie = cookie.split(":", 1)[1].strip()
    return cookie


def load_cookie(path: Path | None = None) -> str:
    cookie_path = path or default_cookie_path()
    if not cookie_path.exists():
        return ""
    return normalize_cookie(cookie_path.read_text(encoding="utf-8"))


def save_cookie(cookie: str, path: Path | None = None) -> Path:
    normalized = normalize_cookie(cookie)
    if not normalized:
        raise ValueError("cookie is empty")

    cookie_path = path or default_cookie_path()
    cookie_path.parent.mkdir(parents=True, exist_ok=True)
    cookie_path.write_text(normalized + "\n", encoding="utf-8")
    cookie_path.chmod(0o600)
    return cookie_path


def load_user_agent(path: Path | None = None) -> str:
    user_agent_path = path or default_user_agent_path()
    if not user_agent_path.exists():
        return ""
    return user_agent_path.read_text(encoding="utf-8").strip()


def save_user_agent(user_agent: str, path: Path | None = None) -> Path:
    normalized = user_agent.strip()
    if not normalized:
        raise ValueError("user-agent is empty")

    user_agent_path = path or default_user_agent_path()
    user_agent_path.parent.mkdir(parents=True, exist_ok=True)
    user_agent_path.write_text(normalized + "\n", encoding="utf-8")
    user_agent_path.chmod(0o600)
    return user_agent_path


def cookie_header_from_browser(domain: str = "4d4y.com") -> str:
    jar = browser_cookie3.chrome(domain_name=domain)
    cookies = []
    for cookie in jar:
        if cookie.domain.lstrip(".") == domain or cookie.domain.endswith("." + domain):
            cookies.append(f"{cookie.name}={cookie.value}")
    return "; ".join(cookies)


def chrome_user_agent() -> str:
    major = "147"
    for plist_path in CHROME_INFO_PLIST_PATHS:
        if not plist_path.exists():
            continue
        with plist_path.open("rb") as file:
            version = str(plistlib.load(file).get("CFBundleShortVersionString", ""))
        if version:
            major = version.split(".", 1)[0]
            break
    return (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major}.0.0.0 Safari/537.36"
    )


def import_browser_auth(domain: str = "4d4y.com") -> tuple[str, str]:
    cookie = cookie_header_from_browser(domain)
    if not cookie:
        raise ValueError(f"no {domain} cookies found in Chrome")
    user_agent = chrome_user_agent()
    save_cookie(cookie)
    save_user_agent(user_agent)
    return cookie, user_agent


def open_login_page() -> None:
    subprocess.run(["open", "-a", "Google Chrome", LOGIN_URL], check=False)
