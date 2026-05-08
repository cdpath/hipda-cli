import ssl

from http.cookiejar import Cookie, CookieJar

from hipda_cli.auth import cookie_header_from_browser, chrome_user_agent
from hipda_cli.client import HipdaClient


def test_from_env_accepts_ca_file_and_insecure_tls():
    client = HipdaClient.from_env(cookie="a=b", ca_file="/tmp/root.pem", insecure_tls=True)

    assert client.ca_file == "/tmp/root.pem"
    assert client.insecure_tls is True


def test_ssl_context_uses_ca_file(monkeypatch):
    calls = {}

    def fake_create_default_context(*, cafile=None):
        calls["cafile"] = cafile
        return "context"

    monkeypatch.setattr(ssl, "create_default_context", fake_create_default_context)

    assert HipdaClient(ca_file="/tmp/root.pem").ssl_context() == "context"
    assert calls == {"cafile": "/tmp/root.pem"}


def test_ssl_context_can_disable_verification():
    context = HipdaClient(insecure_tls=True).ssl_context()

    assert context.check_hostname is False
    assert context.verify_mode == ssl.CERT_NONE


def test_cookie_header_from_browser_filters_4d4y_cookies(monkeypatch):
    jar = CookieJar()
    jar.set_cookie(_cookie("cdb_auth", "abc", ".4d4y.com"))
    jar.set_cookie(_cookie("cf_clearance", "def", "www.4d4y.com"))
    jar.set_cookie(_cookie("other", "nope", ".example.com"))

    monkeypatch.setattr("hipda_cli.auth.browser_cookie3.chrome", lambda domain_name: jar)

    assert cookie_header_from_browser("4d4y.com") == "cdb_auth=abc; cf_clearance=def"


def test_chrome_user_agent_uses_chrome_version_from_plist(monkeypatch, tmp_path):
    import plistlib

    plist = tmp_path / "Info.plist"
    plist.write_bytes(plistlib.dumps({"CFBundleShortVersionString": "147.0.1.2"}))
    monkeypatch.setattr("hipda_cli.auth.CHROME_INFO_PLIST_PATHS", (plist,))

    assert chrome_user_agent() == (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
    )


def _cookie(name: str, value: str, domain: str) -> Cookie:
    return Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=domain.startswith("."),
        path="/",
        path_specified=True,
        secure=True,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest={},
    )
