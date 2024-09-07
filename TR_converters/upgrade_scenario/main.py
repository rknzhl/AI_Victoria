import requests
import json
import sys
import os

IAM_path = os.path.join(os.path.dirname(__file__), '../../IAM_TOKEN.txt')


IAM_KEY = ''

with open(IAM_path, 'r') as token_file:
    IAM_KEY = token_file.read()

IAM_KEY = IAM_KEY[:-1]


def get_good_scenario(bad_scenario, output_path):
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    headers = {
        'Authorization': 'Bearer ' + IAM_KEY,
        'Content-Type': 'application/json',
    }

    with open(os.path.join(os.path.dirname(__file__), 'upgrade_prompt.txt'), 'r') as text_file:
        role_text = text_file.read()
    
    
    
    data = {
        "modelUri": "gpt://b1g72uajlds114mlufqi/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": role_text
            },
            {
                "role": "user",
                "text": bad_scenario
            }
        ]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    good_scenario = response.json()['result']['alternatives'][0]['message']['text']
    data['messages'][1]['text'] = good_scenario.replace('*', '')

    with open(os.path.join(os.path.dirname(__file__), 'split_prompt.txt'), 'r') as text_file:
        role_text = text_file.read()

    data['messages'][0]['text'] = role_text
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    split_good_scenario = response.json()['result']['alternatives'][0]['message']['text']

    
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(split_good_scenario)
    

input_path = os.path.join(os.path.dirname(__file__), sys.argv[1])
output_path = os.path.join(os.path.dirname(__file__), sys.argv[2])


with open(input_path, 'r') as bad:
    bad_scenario = bad.read()

get_good_scenario(bad_scenario, output_path)
