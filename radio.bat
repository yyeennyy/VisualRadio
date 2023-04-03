cd .\

set RADIO_NAME=%0

if not exist %cd%\VisualRadio\radio_storage\%RADIO_NAME%\ (
    mkdir %cd%\VisualRadio\radio_storage\%RADIO_NAME%
)

set RADIO_DATE=%date:~2,2%%date:~5,2%%date:~8,2%
if not exist %cd%\VisualRadio\radio_storage\%RADIO_NAME%\%RADIO_DATE%\ (
    mkdir %cd%\VisualRadio\radio_storage\%RADIO_NAME%\%RADIO_DATE%
)

set PROGRAM_NAME=raw
 
set MP3_FILE_NAME=VisualRadio\radio_storage\%RADIO_NAME%\%RADIO_DATE%\%PROGRAM_NAME%.wav

set RECORD_MINS=10

@ echo off
python radio_mbcfm4u.py > output
for /f "tokens=1" %%a in (output) do (
    set RADIO_ADDR=%%a
)

ffmpeg -t %RECORD_MINS% -i %RADIO_ADDR% %MP3_FILE_NAME%