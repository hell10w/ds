FROM nginx:latest

ADD nginx.conf /etc/nginx/conf.d/default.conf
ADD proxy_params /etc/nginx/proxy_params
ADD nginx.htpasswd /etc/nginx/nginx.htpasswd
RUN \
  chown root:www-data /etc/nginx/nginx.htpasswd && \
  chmod 0777 /etc/nginx/nginx.htpasswd
