import requests
import json
from docx import Document

doc = Document('transcription.docx')

# Инициализируем переменную для хранения текста
transcription_text = ""

# Проходимся по каждому параграфу и добавляем его в переменную
for paragraph in doc.paragraphs:
    transcription_text += paragraph.text + "\n"

IAM_KEY = ''

with open('IAM_TOKEN.txt', 'r') as token_file:
    IAM_KEY = token_file.read()
IAM_KEY = IAM_KEY[:-1]    
def get_answer(role_text):
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        'Authorization': 'Bearer ' + IAM_KEY,
        'Content-Type': 'application/json',
    }

    data = {
        "modelUri": "gpt://b1g72uajlds114mlufqi/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.07,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": role_text
            },
            {
                "role": "user",
                "text": transcription_text
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    final = response.json()['result']['alternatives'][0]['message']['text']
    with open('output.txt', 'w', encoding='utf-8') as file:
        file.write(final)

    
    
def generate(official_flag):
    role_text = ''
    with open("official_text.txt" if official_flag else "unofficial_text.txt" , 'r') as text_file:
        role_text = text_file.read()
    get_answer(role_text)
    
    



flag = int(input())
generate(flag)
