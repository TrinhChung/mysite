FROM nginx:1.23.3

RUN rm /etc/nginx/conf.d/default.conf
COPY default.conf /etc/nginx/conf.d/
COPY ./certificate.pem /etc/nginx/certs/certificate.pem
COPY ./privatekey.pem /etc/nginx/crets/privatekey.pem
RUN chmod +r /etc/nginx/certs/certificate.pem
RUN chmod +r /etc/nginx/crets/privatekey.pem