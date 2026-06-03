# NetGarde block page

Shown when dnsmasq returns the WireGuard gateway IP (`10.0.0.1`) for blocked domains.

| Port | Use |
|------|-----|
| 80 | HTTP block page |
| 443 | HTTPS with cert SANs matching blocked hostnames |

## HTTPS (recommended)

1. On EC2, after dns-sync:

```bash
sudo bash scripts/block-page-tls/generate-certs.sh
docker compose up -d block-page
```

2. Copy the CA to your Mac (VPN on):

```bash
scp ubuntu@YOUR_EC2:/etc/netgarde/block-page-tls/ca.crt ~/Downloads/netgarde-policy-ca.crt
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/Downloads/netgarde-policy-ca.crt
```

3. Open `https://facebook.com` — you should see **Access Blocked** (no “can’t be reached”).

Certs are regenerated when you run `scripts/refresh-block-page-after-sync.sh` (also hooked from `run-sync.sh`).

## Test

```bash
curl -s http://10.0.0.1/ | head
curl -sk https://10.0.0.1/ | head
```
