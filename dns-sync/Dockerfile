FROM python:3.12-alpine

RUN apk add --no-cache curl dnsmasq

WORKDIR /app
COPY sync.py .

CMD ["python", "sync.py"]
