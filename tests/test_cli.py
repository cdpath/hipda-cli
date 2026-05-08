from hipda_cli.auth import default_cookie_path, default_user_agent_path, load_cookie, load_user_agent, save_cookie, save_user_agent
from hipda_cli.cli import build_parser, load_discovery_page


def test_build_parser_accepts_discovery_list_options():
    parser = build_parser()

    args = parser.parse_args(["--ca-file", "/tmp/root.pem", "--insecure-tls", "discovery", "list", "--page", "2", "--limit", "5"])

    assert args.command == "discovery"
    assert args.discovery_command == "list"
    assert args.ca_file == "/tmp/root.pem"
    assert args.insecure_tls is True
    assert args.page == 2
    assert args.limit == 5


def test_build_parser_accepts_discovery_read_tid():
    parser = build_parser()

    args = parser.parse_args(["discovery", "read", "3446553", "--page", "3"])

    assert args.discovery_command == "read"
    assert args.thread == "3446553"
    assert args.page == 3


def test_build_parser_accepts_auth_save_cookie():
    parser = build_parser()

    args = parser.parse_args(["auth", "save-cookie", "foo=bar; baz=qux"])

    assert args.command == "auth"
    assert args.auth_command == "save-cookie"
    assert args.cookie == "foo=bar; baz=qux"


def test_build_parser_accepts_auth_save_user_agent():
    parser = build_parser()

    args = parser.parse_args(["auth", "save-user-agent", "Mozilla/5.0 Chrome/147.0.0.0"])

    assert args.command == "auth"
    assert args.auth_command == "save-user-agent"
    assert args.user_agent == "Mozilla/5.0 Chrome/147.0.0.0"


def test_build_parser_accepts_login():
    parser = build_parser()

    args = parser.parse_args(["login"])

    assert args.command == "login"


def test_save_cookie_strips_cookie_prefix_and_uses_private_permissions(tmp_path):
    cookie_path = tmp_path / "cookie"

    save_cookie("Cookie: foo=bar; baz=qux\n", cookie_path)

    assert load_cookie(cookie_path) == "foo=bar; baz=qux"
    assert oct(cookie_path.stat().st_mode & 0o777) == "0o600"


def test_default_cookie_path_uses_xdg_config_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert default_cookie_path() == tmp_path / "hipda" / "cookie"


def test_save_user_agent_round_trips(tmp_path):
    path = tmp_path / "user-agent"

    save_user_agent("Mozilla/5.0 Chrome/147.0.0.0\n", path)

    assert load_user_agent(path) == "Mozilla/5.0 Chrome/147.0.0.0"
    assert oct(path.stat().st_mode & 0o777) == "0o600"


def test_default_user_agent_path_uses_xdg_config_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    assert default_user_agent_path() == tmp_path / "hipda" / "user-agent"


def test_load_discovery_page_imports_browser_auth_when_saved_auth_is_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    calls = []

    class FakeClient:
        def __init__(self, cookie=""):
            self.cookie = cookie

        def get(self, path, params):
            calls.append((self.cookie, path, params))
            return "<html><a href='viewthread.php?tid=1'>ok</a></html>" if self.cookie else "您还未登录"

    monkeypatch.setattr("hipda_cli.cli.HipdaClient.from_env", lambda **kwargs: FakeClient(kwargs.get("cookie") or load_cookie()))
    monkeypatch.setattr("hipda_cli.cli.import_browser_auth", lambda: ("cdb_auth=abc", "Mozilla/5.0 Chrome/147.0.0.0"))

    html, client = load_discovery_page(
        page=1,
        path="forumdisplay.php",
        params={"fid": 2, "page": 1},
        cookie=None,
        user_agent=None,
        ca_file=None,
        insecure_tls=False,
    )

    assert "viewthread.php" in html
    assert client.cookie == "cdb_auth=abc"
    assert calls == [
        ("", "forumdisplay.php", {"fid": 2, "page": 1}),
        ("cdb_auth=abc", "forumdisplay.php", {"fid": 2, "page": 1}),
    ]
