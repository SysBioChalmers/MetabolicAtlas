#!/bin/bash

if [ -e /etc/letsencrypt/live/$PUBLICHOST/privkey.pem ]
then
  cat /etc/letsencrypt/live/$PUBLICHOST/privkey.pem /etc/letsencrypt/live/$PUBLICHOST/cert.pem > /etc/ssl/private/pure-ftpd.pem
fi