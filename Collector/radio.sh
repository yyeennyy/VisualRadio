#!/bin/bash
# mkdir -p "/radio_storage"
BROADCAST=$1
RADIO_NAME=$2
RECORD_MINS=$3
RADIO_DATE=$(date +"%Y-%m-%d")

mkdir -p "./radio_storage/$BROADCAST/$RADIO_NAME/$RADIO_DATE"

PROGRAM_NAME="raw"
MP3_FILE_NAME="./radio_storage/$BROADCAST/$RADIO_NAME/$RADIO_DATE/$PROGRAM_NAME.wav"

RADIO_ADDR=$(python "$BROADCAST.py")

ffmpeg -t "$RECORD_MINS" -y -i "$RADIO_ADDR" "$MP3_FILE_NAME"