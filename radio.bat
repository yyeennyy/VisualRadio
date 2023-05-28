set BROADCAST=%1
if not exist %cd%\VisualRadio\radio_storage\%BROADCAST%\ (
    mkdir %cd%\VisualRadio\radio_storage\%BROADCAST%
)

set RADIO_NAME=%2
if not exist %cd%\VisualRadio\radio_storage\%BROADCAST%\%RADIO_NAME%\ (
    mkdir %cd%\VisualRadio\radio_storage\%BROADCAST%\%RADIO_NAME%
)

set RADIO_DATE=%date%
if not exist %cd%\VisualRadio\radio_storage\%BROADCAST%\%RADIO_NAME%\%RADIO_DATE%\ (
    mkdir %cd%\VisualRadio\radio_storage\%BROADCAST%\%RADIO_NAME%\%RADIO_DATE%
)

set PROGRAM_NAME=raw
 
set MP3_FILE_NAME=%cd%\VisualRadio\radio_storage\%BROADCAST%\%RADIO_NAME%\%RADIO_DATE%\%PROGRAM_NAME%.wav

set RECORD_MINS=%3

@ echo off
python %BROADCAST%.py > output
for /f "tokens=1" %%a in (output) do (
    set RADIO_ADDR=%%a
)

del output

ffmpeg -t %RECORD_MINS% -i %RADIO_ADDR% %MP3_FILE_NAME% 