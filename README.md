# AutoIFTTT
Automatically create/update [IFTTT](https://ifttt.com/) applets without using the web UI.

## Purpose
Creating applets for IFTTT can be a painful process. It requires a lot of typing and clicking and the web UI has the following limitations:
- There is no way to clone an applet; creating several similar automations requires each be built from scratch
- There is no way to privately share an applet; if I have multiple accounts, each account must have it's own unique applet which won't stay in sync
- Applets cannot be exported; if you lose your account, you lose all over your work
- Applets cannot be imported/created in bulk; that is, until AutoIFTTT...

AutoIFTTT will take a JSON configuration and automatically create applets within seconds.

This project was developed to support some of my other projects such as Plex voice commands and Tesla voice commands.

## Limitations
Equipment/accounts are required for creating/testing applets. Without said accounts, I am limited with what I am able to develop. You may request I support specific services but you may be better off submitting a PR.
Currently supported services:
- Google Assistant ==> Webhook

Without an official API, ReST endpoints had to be reverse engineered. You will need to do some web debugging in order to get your session token. In the future, maybe we can generate a token using login credentials.

Applets are not actually 'updated'. They are instead deleted and then recreated. Not very efficient but it has the same result.

Only a single account is supported. Multiple accounts could be added in the future but for now, just have two instances of this project.

## Installation
1. Download/Install [Python 3](https://www.python.org/downloads/)
   - Include installation of PIP
   - Select to add Python to PATH (if using Windows)
2. Install project requirements
   - `pip install -r requirements.txt`
3. Populate config (instructions for Chromium browser such as Chrome or Edge)
   - Log in to https://ifttt.com/
   - Open _Developer Tools_ `F12`
   - Select the _Network_ tab and ensure it is recording network activity
   - Create any applet (you may immediately delete it afterwards)
   - After clicking _Finish_, find the **POST** to **create/api** which should have a **201** status (it can be found by filtering by the term _create_)
   - Selecting the item, look at the _Request Headers_
   - Copy the values for both `cookie` and `x-csrf-token` into this project's `config.py` file
   - Execute `auto_ifttt.py` once to create all required directories

## Usage
1. Acquire applet **JSON** configuration
   - This may come from one of the project mentioned above or created yourself using the [sample JSON](sample.json)
2. Place **JSON** file in `applets` directory
3. Execute `auto_ifttt.py`
   - Applets should now exist in IFTTT
   - JSON will have moved to the `processed` directory
   - A new text file, containing applet IDs, was placed in the `created` directory
4. Update applets by repeating steps 1-3
   - Existing applets, as defined in the `created` directory, will be deleted before creating the updated applets