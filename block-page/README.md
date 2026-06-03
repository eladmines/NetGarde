# NetGarde block page

Served when dnsmasq returns the WireGuard gateway IP (`10.0.0.1`) for blocked domains.

| Port | Use |
|------|-----|
| 80 | HTTP — block page loads directly |
| 443 | HTTPS — TLS with a self-signed cert (`CN=NetGarde Block Page`) |

HTTPS blocked sites (e.g. `https://facebook.com`) will show a **certificate warning** first; after proceeding, the same HTML is shown. Browsers cannot show a trusted page for arbitrary hostnames without a custom CA or TLS proxy.

## Deploy

```bash
docker compose build block-page
docker compose up -d block-page
sudo bash scripts/setup-block-page-wg.sh
```

Test:

```bash
curl -s http://10.0.0.1/ | head
curl -sk https://10.0.0.1/ | head
```
