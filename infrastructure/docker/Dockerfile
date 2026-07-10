FROM ubuntu:latest

RUN apt-get update && apt-get install -y nginx

ENV SECRET_KEY=super_secret_123

USER root

COPY . /app
ADD https://example.com/bad.sh /app/bad.sh

CMD ["nginx", "-g", "daemon off;"]
