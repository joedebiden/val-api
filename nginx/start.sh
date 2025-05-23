#!/bin/bash

if [ -z "$FLASK_SERVER_ADDR" ]; then
    echo "Erreur: FLASK_SERVER_ADDR n'est pas définie"
    exit 1
fi

echo "Configuration nginx avec FLASK_SERVER_ADDR=$FLASK_SERVER_ADDR"

envsubst '$FLASK_SERVER_ADDR' < /tmp/default.conf > /etc/nginx/conf.d/default.conf

nginx -t

if [ $? -eq 0 ]; then
    echo "Configuration nginx valide"
    exec nginx -g 'daemon off;'
else
    echo "Erreur dans la configuration nginx"
    exit 1
fi