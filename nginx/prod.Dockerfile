FROM node:lts-alpine AS frontend
ARG VUE_APP_FTP_SERVER
ENV VUE_APP_FTP_SERVER=${VUE_APP_FTP_SERVER}
WORKDIR /project
COPY frontend .
RUN yarn && yarn build

FROM staticfloat/nginx-certbot
COPY nginx/prod.nginx.conf /etc/nginx/user.conf.d/nginx.conf
COPY --from=frontend /project/dist /content