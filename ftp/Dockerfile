FROM stilliard/pure-ftpd:hardened

COPY ftp-models /var/ftp/models
RUN useradd -d /var/ftp -s /sbin/nologin ftp

CMD /run.sh pure-ftpd -4 -A -c 50 -C 5 -e -G -H -i -p $FTP_MIN_PORT:$FTP_MAX_PORT -P $PUBLICHOST -r -R -s -X -x -Z -Y 0 $FLAGS