cd .\

set PROGRAM_NAME=raw

set REC_DATE=%date:~0,4%%date:~5,2%%date:~8,2%
 
set MP3_FILE_NAME=%PROGRAM_NAME%.wav

set RECORD_MINS=3600

@ echo off
python radio_mbcfm4u.py > output
for /f "tokens=1" %%a in (output) do (
    set RADIO_ADDR=%%a
)

ffmpeg -t %RECORD_MINS% -i %RADIO_ADDR% %MP3_FILE_NAME%