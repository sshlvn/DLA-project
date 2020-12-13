# from youtube_transcript_api import YouTubeTranscriptApi
# from gtts import gTTS
from flask import Flask #, Response, jsonify
# from threading import Thread
# import json

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'


# @app.route('/')
# def get_json_and_wavs():
    
#     video_id = 'ttPXXyUyx6Q'

#     transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

#     # языки, для которых уже доступен транскрипт
#     languages = set()

#     for item in transcript_list:
#         lang = str(item).split()[0]
#         languages.add(lang)
#         if 'auto-generated' in str(item) or 'создано автоматически' in str(item):
#             original_lang = str(item).split()[0]

#     # если видео русскоязычное, то переводим на англ, с любого другого языка переводим на русский
#     if original_lang == 'ru':
#         language = 'en'
#     else:
#         language = 'ru'

#     # если есть уже сделанный транскрипт, то берем его, если нет, то переводим
#     if language in languages:
#         transcript = transcript_list.find_transcript([language])
#     else:
#         transcript = transcript_list.find_transcript([original_lang]).translate(language)

#     transcript_list = transcript.fetch()

#     def generation():
#         for i in range(len(transcript_list)):
#             text = transcript_list[i]['text']
#             tts = gTTS(text=text, lang=language, slow=False)

#             file_name = video_id + '_' + str(i) + '.wav'

#             tts.save(file_name)

#     thread = Thread(target=generation)
#     thread.start()

#     # для русского языка отдельно нужно прописать utf-8
#     if language == 'ru':
#         json_string = json.dumps(transcript_list, ensure_ascii=False)
#         return Response(json_string,
#                         content_type="application/json; charset=utf-8")

#     return jsonify(transcript_list)
