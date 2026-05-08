# hipda-cli

CLI reader for the 4D4Y/HiPDA Discovery channel (`fid=2`).

The site uses browser/session checks, so direct unauthenticated requests may return a Cloudflare challenge. Normally, just use the CLI after logging in through Chrome:

```bash
uvx --from . hipda discovery list --limit 20
uvx --from . hipda discovery read 3446553
```

If the automatic import needs a nudge, run:

```bash
uvx --from . hipda login
```

This imports only 4D4Y cookies from Chrome and saves the matching Chrome user agent. Manual setup still works:

```bash
uvx --from . hipda auth save-cookie 'Cookie: your_cookie_header'
uvx --from . hipda auth save-user-agent 'Mozilla/5.0 ... Chrome/147.0.0.0 Safari/537.36'
```

The cookie is stored at `~/.config/hipda/cookie` and the user agent is stored at `~/.config/hipda/user-agent`, both with `0600` permissions. You can still override them per command with `HIPDA_COOKIE` / `--cookie` and `HIPDA_USER_AGENT` / `--user-agent`.

You can also pass a browser user agent:

```bash
HIPDA_USER_AGENT='Mozilla/5.0 ...' uvx --from . hipda discovery list
```

If Python reports `CERTIFICATE_VERIFY_FAILED` but Chrome can open the site, your network may be using a local HTTPS inspection certificate that Chrome trusts and Python does not. Prefer passing that root certificate:

```bash
uvx --from . hipda --ca-file /path/to/root-ca.pem discovery list
```

As a last resort, you can disable TLS verification for this CLI call:

```bash
uvx --from . hipda --insecure-tls discovery list
```
