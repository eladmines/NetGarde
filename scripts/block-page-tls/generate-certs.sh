#!/usr/bin/env bash
# Build CA + server TLS cert with SANs for blocked domains (HTTPS block page).
# Usage: sudo bash scripts/block-page-tls/generate-certs.sh [/etc/dnsmasq.d/blocked-domains.conf]
set -euo pipefail

TLS_DIR="${BLOCK_PAGE_TLS_DIR:-/etc/trustedge/block-page-tls}"
BLOCKED_CONF="${1:-/etc/dnsmasq.d/blocked-domains.conf}"
MAX_SANS="${BLOCK_PAGE_MAX_SANS:-80}"
DAYS="${BLOCK_PAGE_CERT_DAYS:-825}"

mkdir -p "$TLS_DIR"
chmod 700 "$TLS_DIR"

extract_domains() {
  if [[ ! -f "$BLOCKED_CONF" ]]; then
    echo "warning: $BLOCKED_CONF missing; using built-in social sample domains" >&2
    printf '%s\n' facebook.com instagram.com twitter.com x.com tiktok.com
    return
  fi
  grep -E '^address=/' "$BLOCKED_CONF" | sed -n 's|^address=/\([^/]*\)/.*|\1|p' | sort -u
}

build_san_file() {
  local san_path="$1"
  local count=0
  : >"$san_path"
  echo "subjectAltName = @alt_names" >>"$san_path"
  echo "[alt_names]" >>"$san_path"
  while IFS= read -r domain; do
    [[ -z "$domain" || "$domain" == "#" ]] && continue
    [[ "$domain" == *.* ]] || continue
    count=$((count + 1))
    if [[ "$count" -gt "$MAX_SANS" ]]; then
      echo "warning: SAN list capped at $MAX_SANS domains" >&2
      break
    fi
    echo "DNS.${count} = ${domain}" >>"$san_path"
    if [[ "$domain" != www.* ]]; then
      count=$((count + 1))
      [[ "$count" -gt "$MAX_SANS" ]] && break
      echo "DNS.${count} = www.${domain}" >>"$san_path"
    fi
  done < <(extract_domains)
  # Always allow direct access by gateway IP / name
  echo "DNS.${count} = 10.0.0.1" >>"$san_path"
  echo "IP.1 = 10.0.0.1" >>"$san_path"
}

echo "Generating TrustEdge block-page TLS in $TLS_DIR"

if [[ ! -f "$TLS_DIR/ca.key" ]]; then
  openssl genrsa -out "$TLS_DIR/ca.key" 4096
  chmod 600 "$TLS_DIR/ca.key"
  openssl req -x509 -new -nodes -key "$TLS_DIR/ca.key" -sha256 -days "$DAYS" \
    -out "$TLS_DIR/ca.crt" \
    -subj "/CN=TrustEdge Policy CA/O=TrustEdge/C=US"
fi

SAN_EXT="$(mktemp)"
build_san_file "$SAN_EXT"

openssl genrsa -out "$TLS_DIR/block-page.key" 2048
chmod 600 "$TLS_DIR/block-page.key"
openssl req -new -key "$TLS_DIR/block-page.key" \
  -out "$TLS_DIR/block-page.csr" \
  -subj "/CN=10.0.0.1/O=TrustEdge/C=US"

openssl x509 -req -in "$TLS_DIR/block-page.csr" \
  -CA "$TLS_DIR/ca.crt" -CAkey "$TLS_DIR/ca.key" -CAcreateserial \
  -out "$TLS_DIR/block-page.crt" -days "$DAYS" -sha256 \
  -extfile "$SAN_EXT"

rm -f "$SAN_EXT" "$TLS_DIR/block-page.csr" "$TLS_DIR/ca.srl"
chmod 644 "$TLS_DIR/block-page.crt" "$TLS_DIR/ca.crt"

echo "TLS ready. Install CA on clients: $TLS_DIR/ca.crt"
echo "  macOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $TLS_DIR/ca.crt"
