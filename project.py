from youtube_transcript_api import YouTubeTranscriptApi
from flask import Flask, Response, jsonify, request, send_file
from threading import Thread
import json
from pydub import AudioSegment
from yandex_speech import TTS

tts = TTS('jane', 'wav', '60589d42-0e42-b742-8942-thekeyisalie', speed=2.0)

app = Flask(__name__)

# получение субтитров на нужном языке
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except:
        return 'Subtitles not found for video ' + video_id

    # языки, для которых уже доступен транскрипт
    languages = set()
    first_lang = True

    for item in transcript_list:
        lang = str(item).split()[0]
        languages.add(lang)
        if first_lang:
            original_lang = lang
            first_lang = False
        if 'auto-generated' in str(item) or 'создано автоматически' in str(item):
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

    return transcript_list, language


# получение json с субтитрами и временем
@app.route('/json/<video_id>')
def get_json(video_id):
    transcript, lang = get_transcript(video_id)

    json_string = json.dumps(transcript, ensure_ascii=False)
    return Response(json_string,
                    content_type="application/json; charset=utf-8")


# генерация 10 wav начиная со  start_fragment
@app.route('/10wavs/<video_id>&&<int:start_fragment>')
def generate_10_wavs(video_id, start_fragment):
    transcript, lang = get_transcript(video_id)

    if start_fragment >= len(transcript):
        return 'There are only ' + str(len(
            transcript)) + ' fragments in video ' + video_id + ' but you asked for fragment №' + str(
            start_fragment)

    end_fragment = min(start_fragment + 10, len(transcript))

    def generate():
        for i in range(start_fragment, end_fragment):
            file_name = video_id + '_' + fragment_id + '.wav'
            text = transcript[i]['text']
            tts.generate(text=text)
            tts.save(file_name)

    thread = Thread(target=generate)
    thread.start()

    return 'OK, generating ' + str(start_fragment) + ' - ' + str(end_fragment)


# получить wav файл
@app.route('/wavs/<video_id>&&<fragment_id>')
def get_wav(video_id, fragment_id):
    file_name = video_id + '_' + fragment_id + '.wav'
    try:
        return send_file(file_name, as_attachment=True)
    except:
        return 'File ' + file_name + ' not found'
