from __future__ import annotations

import os
import ssl
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .auth import load_cookie, load_user_agent


BASE_URL = "https://www.4d4y.com/forum/"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class HipdaClientError(RuntimeError):
    pass


@dataclass(frozen=True)
class HipdaClient:
    cookie: str = ""
    user_agent: str = DEFAULT_USER_AGENT
    ca_file: str | None = None
    insecure_tls: bool = True
    base_url: str = BASE_URL
    timeout: float = 20.0

    @classmethod
    def from_env(
        cls,
        cookie: str | None = None,
        user_agent: str | None = None,
        ca_file: str | None = None,
        insecure_tls: bool = True,
        verify_tls: bool = False,
    ) -> "HipdaClient":
        return cls(
            cookie=cookie or os.environ.get("HIPDA_COOKIE", "") or load_cookie(),
            user_agent=user_agent or os.environ.get("HIPDA_USER_AGENT", "") or load_user_agent() or DEFAULT_USER_AGENT,
            ca_file=ca_file or os.environ.get("HIPDA_CA_FILE"),
            insecure_tls=(
                not verify_tls
                and (insecure_tls or os.environ.get("HIPDA_INSECURE_TLS", "").lower() in {"1", "true", "yes"})
            ),
        )

    def ssl_context(self) -> ssl.SSLContext | None:
        if self.insecure_tls:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
        if self.ca_file:
            return ssl.create_default_context(cafile=self.ca_file)
        return None

    def get(self, path: str, params: dict[str, str | int] | None = None) -> str:
        url = self.base_url + path
        if params:
            url = f"{url}?{urlencode(params)}"

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "User-Agent": self.user_agent,
        }
        if self.cookie:
            headers["Cookie"] = self.cookie

        try:
            with urlopen(Request(url, headers=headers), timeout=self.timeout, context=self.ssl_context()) as response:
                body = response.read()
                encoding = response.headers.get_content_charset() or "utf-8"
                return body.decode(encoding, errors="replace")
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:300]
            raise HipdaClientError(f"HTTP {exc.code} fetching {url}: {body}") from exc
        except URLError as exc:
            if isinstance(exc.reason, ssl.SSLCertVerificationError):
                raise HipdaClientError(
                    f"Could not verify TLS certificate for {url}: {exc.reason}. "
                    "If you use a trusted local proxy, pass --ca-file /path/to/root.pem. "
                    "As a last resort, pass --insecure-tls."
                ) from exc
            raise HipdaClientError(f"Could not fetch {url}: {exc.reason}") from exc
