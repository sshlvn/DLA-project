from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
from flask import Flask, Response, jsonify, request, send_file
from threading import Thread
import json
# import librosa
from pydub import AudioSegment

# AudioSegment.converter = '/app/.apt/usr/local/bin/ffmpeg'

app = Flask(__name__)

# сохраняем video_id: (transcript, language)
TRANSCRIPT_DICT = dict()


@app.route('/json/<video_id>')
def get_json(video_id):
    # если транскрипт уже делали
    if video_id in TRANSCRIPT_DICT:
        transcript, lang = TRANSCRIPT_DICT[video_id]
        if lang == 'ru':
            json_string = json.dumps(transcript, ensure_ascii=False)
            return Response(json_string,
                            content_type="application/json; charset=utf-8")
        return jsonify(transcript)

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except:
        return 'Subtitles not found for video ' + video_id

    # языки, для которых уже доступен транскрипт
    languages = set()

    for item in transcript_list:
        lang = str(item).split()[0]
        languages.add(lang)
        if 'auto-generated' in str(item) or 'создано автоматически' in str(
                item):
            original_lang = str(item).split()[0]

    # если видео русскоязычное, то переводим на англ, с любого другого языка переводим на русский
    if original_lang == 'ru':
        language = 'en'
    else:
        language = 'ru'

    # если есть уже сделанный автором транскрипт, то берем его, если нет, то переводим
    if language in languages:
        transcript = transcript_list.find_transcript([language])
    else:
        transcript = transcript_list.find_transcript([original_lang]).translate(
            language)

    transcript_list = transcript.fetch()

    # генерятся первые 10
    def generate():
        for i in range(10):
            text = transcript_list[i]['text']
            tts = gTTS(text=text, lang=language, slow=False)

            file_name = video_id + '_' + str(i)
            tts.save(file_name + '.mp3')

            AudioSegment.from_mp3(file_name + '.mp3').export(file_name + '.wav', format='wav')
            
            sound = AudioSegment.from_file(file_name + '.wav')


            sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
                 "frame_rate": int(sound.frame_rate * 2.0)
              })
            new_sound = sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
            
            new_sound.export(file_name + '.wav', format='wav')

    thread = Thread(target=generate)
    thread.start()

    TRANSCRIPT_DICT[video_id] = (transcript_list, language)

    # для русского языка отдельно нужно прописать utf-8
    if language == 'ru':
        json_string = json.dumps(transcript_list, ensure_ascii=False)
        return Response(json_string,
                        content_type="application/json; charset=utf-8")

    return jsonify(transcript_list)


@app.route('/10wavs/<video_id>&&<int:start_fragment>')
def generate_10_wavs(video_id, start_fragment):
    try:
        transcript, lang = TRANSCRIPT_DICT[video_id]
    except:
        return 'Transcript not found for video ' + video_id

    def generate():
        for i in range(start_fragment, start_fragment + 10):
            text = transcript[i]['text']
            tts = gTTS(text=text, lang=lang, slow=False)

            file_name = video_id + '_' + str(i)
            tts.save(file_name + '.mp3')

            AudioSegment.from_mp3(file_name + '.mp3').export(file_name + '.wav', format='wav')
            
            sound = AudioSegment.from_file(file_name + '.wav')


            sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
                 "frame_rate": int(sound.frame_rate * 2.0)
              })
            new_sound = sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
            
            new_sound.export(file_name + '.wav', format='wav')

    thread = Thread(target=generate)
    thread.start()

    return 'OK, generating ' + str(start_fragment) + ' - ' + str(
        start_fragment + 9)
