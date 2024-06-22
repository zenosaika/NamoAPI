# docs: https://poeyza.medium.com/วิธีทำ-line-bot-ด้วย-line-python-sdk-5ceb9b138a84

from fastapi import FastAPI, Request, Response
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,  LocationMessage, AudioMessage, ImageMessage, ImageSendMessage
)

import os
import asr
import llm
import earth
from pydub import AudioSegment

app = FastAPI()

CHANNEL_ACCESS_TOKEN = '26i4XBXKTjIMN0uJs8NRX9jgxQBMyI7yNrt1ehnk6tE8/MRusauH7e1rOfDuwZ/DES05tX6bOKJ60iclJs8nOSszdm68PziJ2eBJ0kYSnB4xl0bEZh0ER0Ea0asNXq+pZTnKx0fX4265/OIntm2MZAdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '9d9478e100309e97d672acbe1614cae9'

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.get('/hello')
def hello_word():
    return {"hello" : "world"}

@app.post('/message')
async def hello_word(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    
    try:
      handler.handle(body.decode('UTF-8'), signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
    return 'OK'

@handler.default()
def default(event):
    print(event)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
        print(f'type: {event.message.type}')
        print(f'type: {event.message.text}')

        text = llm.llm(system="You are a helpful assistant who're always speak Thai.",
                   user=event.message.text
                )
        
        print(f'llm: {text}')
        sendMessage(event, text)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
        print(f'type: {event.message.type}')
        print(f'id: {event.message.id}')

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio(event):
        print(f'type: {event.message.type}')
        print(f'duration: {event.message.duration}')
        print(f'id: {event.message.id}')

        if not os.path.exists('audio'):
             os.makedirs('audio')

        filepath = f'audio/{event.message.id}'
        get_content_and_write(event, filepath)

        # convert from m4a to wav format before pass to torchaudio
        sound = AudioSegment.from_file(filepath, format='m4a')
        file_handle = sound.export(filepath, format='wav')

        text = asr.speech2text(filepath)
        os.remove(filepath)

        print(f'speech2text: {text}')
        sendMessage(event, ''.join(text))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
        print(f'type: {event.message.type}')
        print(f'address: {event.message.address}')
        print(f'latitude: {event.message.latitude}')
        print(f'longitude: {event.message.longitude}')

        img_url = earth.get_map(event.message.longitude, event.message.latitude)

        sendImage(event, img_url)
    
def echo(event):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))
        
def sendMessage(event, message):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message))
        
def sendImage(event, img_url):
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(img_url, img_url))
        
def get_content_and_write(event, write_to_path):
    message_content = line_bot_api.get_message_content(event.message.id)

    with open(write_to_path, 'wb') as f:
        for chunk in message_content.iter_content():
            f.write(chunk)