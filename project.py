from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
from flask import Flask, Response, jsonify, request, send_file
from threading import Thread
import json
from pydub import AudioSegment

app = Flask(__name__)

WAV_SPEED = 1.35

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

    # для русского языка отдельно нужно прописать utf-8
    # if lang == 'ru':
    #     json_string = json.dumps(transcript, ensure_ascii=False)
    #     return Response(json_string,
    #                     content_type="application/json; charset=utf-8")
    #
    # return jsonify(transcript_list)


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
            text = transcript[i]['text']
            tts = gTTS(text=text, lang=lang, slow=False)

            file_name = video_id + '_' + str(i)
            tts.save(file_name + '.mp3')

            # gtts не может сделать нормальный .wav
            AudioSegment.from_mp3(file_name + '.mp3').export(file_name + '.wav', format='wav')

            wav = AudioSegment.from_file(file_name + '.wav')

            # изменение скорости
            new_wav = wav._spawn(wav.raw_data, overrides={"frame_rate": int(wav.frame_rate * WAV_SPEED)})
            new_wav = new_wav.set_frame_rate(wav.frame_rate)
            new_wav.export(file_name + '.wav', format='wav')

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
