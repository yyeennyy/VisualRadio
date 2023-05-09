@echo off
echo audio_path: %1
set output_path= %2
set terminal_command=whisper %1 --device cpu --model base --fp16 False --language Korean --no_speech_threshold 0.6 --threads 8 --output_dir %2
%terminal_command%
pause