import json
import os
import requests

import config

created_dir = 'created/'
applets_dir = 'applets/'
processed_dir = applets_dir + 'processed/'
json_ext = '.json'

headers = {
    'Content-Type': 'application/json',
    'cookie': config.cookie,
    'x-csrf-token': config.x_csrf_token
}


def get_url(base_url, path, token):
    url = base_url + path
    if token and len(token) > 0:
        url += '&' if '?' in url else '?'
        url += 'token=' + token
    return url


def delete_previous_applets(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                delete_applet(line.rstrip('\n'))


def delete_applet(applet_id):
    r = requests.delete('https://ifttt.com/connections/' + applet_id + '.json', headers=headers)
    if r.ok and r.text == '{"redirect_to":"/"}':
        print('Deleted applet ' + applet_id)
    else:
        print('Failed to delete applet ' + applet_id + ': ' + str(r.status_code) + ' - ' + r.reason)


def create_applets(json_file_name):
    ids = []
    with open(applets_dir + json_file_name, 'r') as json_file:
        obj = json.load(json_file)
        for applet in obj['applets']:
            url = get_url(obj['base_url'], applet['path'], obj['token'])
            triggers = applet['triggers']
            while len(triggers) > 3:
                first_three = triggers[:3]
                ids.append(create_applet(applet['name'], url, first_three, applet['response']))
                triggers = triggers[3:]
            ids.append(create_applet(applet['name'], url, triggers, applet['response']))
    return ids


def create_applet(name, url, triggers, response):
    step_identifier = 'google_assistant.'
    if set(triggers[0]) >= set('#$'):
        step_identifier += 'voice_trigger_with_one_text_and_one_number_ingredient'
    elif '$' in triggers[0]:
        step_identifier += 'voice_trigger_with_one_text_ingredient'
    elif '#' in triggers[0]:
        step_identifier += 'voice_trigger_with_one_number_ingredient'
    else:
        step_identifier += 'simple_voice_trigger'

    body = {
        'name': name,
        'push_enabled': False,
        'channel_id': '65067518',
        'trigger':
            {
                'step_identifier': step_identifier,
                'fields':
                    [
                        {
                            'name': 'voice_input_1',
                            'hidden': True,
                            'value': triggers[0]
                        },
                        {
                            'name': 'voice_input_2',
                            'hidden': True,
                            'value': triggers[1] if len(triggers) > 1 else ''
                        },
                        {
                            'name': 'voice_input_3',
                            'hidden': True,
                            'value': triggers[2] if len(triggers) > 2 else ''
                        },
                        {
                            'name': 'tts_response',
                            'hidden': True,
                            'value': response
                        },
                        {
                            'name': 'supported_languages_for_user',
                            'hidden': True,
                            'value': config.lang
                        }
                    ],
                'channel_id': '65067518'
            },
        'actions':
            [
                {
                    'step_identifier': 'maker_webhooks.make_web_request',
                    'fields':
                        [
                            {
                                'name': 'url',
                                'hidden': True,
                                'value': url
                            },
                            {
                                'name': 'body',
                                'hidden': True,
                                'value': ''
                            },
                            {
                                'name': 'method',
                                'hidden': True,
                                'value': 'GET'
                            },
                            {
                                'name': 'content_type',
                                'hidden': True,
                                'value': 'application/json'
                            }
                        ],
                    'channel_id': '1004582012'
                }
            ]
    }

    r = requests.post('https://ifttt.com/create/api', headers=headers, data=json.dumps(body))
    if r.ok:
        applet_id = r.text[len('{"return_to":"/applets/'):-len('"}')]
        print('Created applet ' + name + ': ' + applet_id)
        return applet_id
    else:
        print(r.text)
        raise Exception('Failed to create applet ' + name + ': ' + str(r.status_code) + ' - ' + r.reason)


if not os.path.exists(created_dir):
    os.makedirs(created_dir)
if not os.path.exists(applets_dir):
    os.makedirs(applets_dir)
if not os.path.exists(processed_dir):
    os.makedirs(processed_dir)

for file in os.listdir(applets_dir):
    if file.endswith(json_ext):
        created_file_path = created_dir + file[:-len(json_ext)]
        delete_previous_applets(created_file_path)
        with open(created_file_path, 'w') as out:
            for new_id in create_applets(file):
                out.write(new_id)
                out.write('\n')
        os.rename(file, processed_dir + file)
