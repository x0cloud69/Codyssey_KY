FROM nginx:alpine

LABEL org.opencontainers.image.authors="My custom NGINX image created by KY SONG"
LABEL maintainer="KY SONG "

ENV APP_ENV=dev
COPY sites/ /usr/share/nginx/html/

EXPOSE 80
