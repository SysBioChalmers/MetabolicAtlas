FROM stilliard/pure-ftpd:hardened

COPY repository /var/ftp/models
RUN useradd -d /var/ftp -s /sbin/nologin ftp

COPY ./prep-cert.sh /project/prep-cert.sh
RUN chmod +x /project/prep-cert.sh

CMD /project/prep-cert.sh && /run.sh pure-ftpd -4 -A -c 50 -C 5 -e -G -H -i -p $FTP_MIN_PORT:$FTP_MAX_PORT -P $FTP_IP -r -R -s -X -x -Z $FLAGS
