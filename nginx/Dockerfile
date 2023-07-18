FROM nginx:1.23.3

RUN rm /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d/
COPY ./certificate.pem /etc/nginx/certs/
COPY ./private.pem /etc/nginx/crets/
RUN chmod +r /etc/nginx/certs/certificate.pem \
    chmod +r /etc/nginx/certs/private.pem