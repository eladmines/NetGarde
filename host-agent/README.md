# NetGarde WireGuard host agent

This is a tiny HTTP service that runs **on the EC2 host as root** and applies:

`wg set <iface> peer <client_pubkey> allowed-ips <ip>/32`

It exists because the `netgarde-api` container cannot safely mutate the host `wg0` interface.

## Install (EC2)

1) Copy files to `/opt/netgarde/`:

- `netgarde-wg-agent.py`
- `netgarde-wg-agent.service`

2) Set a strong token (must match backend `WG_AGENT_TOKEN`):

Edit `/etc/systemd/system/netgarde-wg-agent.service` (or use a drop-in) and replace `CHANGE_ME`.

3) Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now netgarde-wg-agent
sudo systemctl status netgarde-wg-agent --no-pager
```

4) Smoke test from the host:

```bash
curl -sS http://172.17.0.1:9109/health
```

## Backend configuration

The backend container should call:

- `WG_AGENT_URL=http://172.17.0.1:9109` (default)
- `WG_AGENT_TOKEN=<same token as NETGARDE_WG_AGENT_TOKEN>`

## Security notes

- The agent binds to the Docker bridge IP by default (`172.17.0.1`) so it is not exposed on the public interface.
- Use a long random bearer token.
