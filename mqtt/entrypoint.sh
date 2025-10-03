#!/bin/sh
set -e

PASSFILE="/mosquitto/config/passwordfile"

if [ -z "$MQTT_USER" ] || [ -z "$MQTT_PASSWORD" ]; then
  echo "MQTT_USER et MQTT_PASSWORD doivent être définis"
  exit 1
fi

# Créer le passwordfile s'il n'existe pas
if [ ! -f "$PASSFILE" ]; then
  echo "Création du fichier passwordfile"
  mosquitto_passwd -b -c "$PASSFILE" "$MQTT_USER" "$MQTT_PASSWORD"
else
  # Mettre à jour/créer l'utilisateur
  if grep -q "^$MQTT_USER:" "$PASSFILE"; then
    echo "Utilisateur $MQTT_USER déjà présent → mise à jour du mot de passe"
    mosquitto_passwd -b "$PASSFILE" "$MQTT_USER" "$MQTT_PASSWORD"
  else
    echo "Ajout de l'utilisateur $MQTT_USER"
    mosquitto_passwd -b "$PASSFILE" "$MQTT_USER" "$MQTT_PASSWORD"
  fi
fi

chmod 0640 "$PASSFILE"
chown mosquitto:mosquitto "$PASSFILE"

exec mosquitto -c /mosquitto/config/mosquitto.conf
