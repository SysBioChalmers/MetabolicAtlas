FROM stilliard/pure-ftpd:hardened

COPY ftp-models /var/ftp/models
RUN useradd -d /var/ftp -s /sbin/nologin ftp

CMD cat /etc/letsencrypt/live/$PUBLICHOST/privkey.pem /etc/letsencrypt/live/$PUBLICHOST/cert.pem > /etc/ssl/private/pure-ftpd.pem && \
  /run.sh pure-ftpd -4 -A -c 50 -C 5 -e -G -H -i -p $FTP_MIN_PORT:$FTP_MAX_PORT -P $PUBLICHOST -r -R -s -X -x -Z -Y 1 $FLAGS