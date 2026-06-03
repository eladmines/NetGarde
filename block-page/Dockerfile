FROM nginx:1.27-alpine

RUN apk add --no-cache openssl \
    && mkdir -p /etc/nginx/ssl \
    && openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/block-page.key \
        -out /etc/nginx/ssl/block-page.crt \
        -subj "/CN=NetGarde Block Page/O=NetGarde/C=US" \
    && chmod 600 /etc/nginx/ssl/block-page.key

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
