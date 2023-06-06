#!/bin/bash

BROADCAST=$1
if [ ! -d "$PWD/VisualRadio/radio_storage/$BROADCAST" ]; then
    mkdir -p "$PWD/VisualRadio/radio_storage/$BROADCAST"
fi

RADIO_NAME=$2
if [ ! -d "$PWD/VisualRadio/radio_storage/$BROADCAST/$RADIO_NAME" ]; then
    mkdir -p "$PWD/VisualRadio/radio_storage/$BROADCAST/$RADIO_NAME"
fi

RADIO_DATE=$(date +"%Y-%m-%d")
if [ ! -d "$PWD/VisualRadio/radio_storage/$BROADCAST/$RADIO_NAME/$RADIO_DATE" ]; then
    mkdir -p "$PWD/VisualRadio/radio_storage/$BROADCAST/$RADIO_NAME/$RADIO_DATE"
fi

PROGRAM_NAME="raw"

MP3_FILE_NAME="$PWD/VisualRadio/radio_storage/$BROADCAST/$RADIO_NAME/$RADIO_DATE/$PROGRAM_NAME.wav"

RECORD_MINS=$3

RADIO_ADDR=$(python "$BROADCAST.py")

ffmpeg -t "$RECORD_MINS" -i "$RADIO_ADDR" "$MP3_FILE_NAME"
