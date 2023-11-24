FROM alpine
RUN apk update && apk add php composer php-fileinfo
WORKDIR /app
RUN composer require polygon-io/api -W
