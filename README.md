# Curvi built with the Rasa Framework

## 🏥 Introduction 

This is an open source starter pack for developers to show how to automate full conversations in education / professional sector.

It supports the following user goals:

- Help user to build a resume easy and fast.
- After resume is done, its connected to a API which generates the resume. So, user can easily download as pdf.

## 💾 How to install and setup Curvi

**Optional (but important)**: Install virtual environment
Its used to install specific packages to a project directory instead of installing the package globally on your system. This allow to use different versions of the same package for different projects. Venv is recommended.
```
Create the virtual environment:
1 - Create a project directory
	mkdir project_folder_name
	cd project_folder_name

2 - Install venv python package:
	pip install virtualenv

3 - Create a virtual environment run:
	python3 -m venv ./venv

4 - Activate the environment:
	source ./venv/bin/activate

5 - To deactivate, run:
    deactivate

6 - Go to step 1 if you do not want to use virtual environment or to continue.
```

**Step 1**: To install Curvi, please clone the repo:
```
git clone https://github.com/MarcosAllysson/curvi2.0.git
cd curvi2.0
```
The Curvi uses **Python 3.8.5** and has not been tested with other versions.
Use the requirements.txt file to install the appropriate dependencies
via pip for Python 3. If you do not have pip installed yet first do:
```
$ sudo apt update
$ sudo apt install python3-pip
```
otherwise move to the next step directly.

**Step 2**: Install requirements:
```
pip3 install -r requirements.txt
```

This will install the bot and all of its requirements.

## 🤖 How to run Curvi

**Step 1**: Train the core model by running:
```
rasa train
```
This will train the Rasa Core model and store it inside the `/models/` folder of your project directory.

**Step 2**: Train the NLU model by running:
```
rasa train nlu
```
This will train the NLU model and store it inside the `/models/` folder of your project directory.

**Step 3**: Start the server for the custom action by running:
```
rasa run actions
```

**Step 4**: Now to test the Curvi with both these models you can run in a new terminal tab:
```
rasa shell
```
After the bot has loaded you can start chatting to it. If you start by saying `Hi` for example,
the bot will reply by saying hello and asking you if you what to start your resume.


## 📱 Use Telegram as Chat platform
In order to chat to the Curvi through Telegram you can do the following:

**Step 1**: First if you don't already use Telegram, download it and set it up with your phone.
Once you are registered with Telegram you start by setting up a Telegram bot.

**Step 2**: To setup your own bot go to the [Telegram BotFather](https://web.telegram.org/#/im?p=@BotFather),
enter `/newbot` and follow the instructions.
You should get your `access_token`, and the username you set will be your `verify`. Save this information as you will need it later.

**Step 3**: Now you will need to connect to Telegram via a webhook. To create a local webhook from your machine you can use [Ngrok](https://ngrok.com/). Follow the instructions on their site to
set it up on your computer. Move `ngrok` to your working directory and in a new terminal run:
```
./ngrok http 5005
```
Ngrok will create a https address for your computer. For Telegram you need the address in this format:
`https://xxxxxx.ngrok.io/webhooks/telegram/webhook`

**Step 4**: Go to the *credentials.yml* file that you downloaded from the repo and input your personal `access_token`, `verify` and `webhook_url`.
You will have to update the `webhook_url` everytime you do redo Step 3, the `access_token` and `verify` will stay the same.

**Step 5**: In a new terminal start the server for the custom action by running:
```
rasa run actions
```

**Step 6**: In a new terminal connect to Telegram by running:
```
rasa run
```

**Step 7**: Now you and anyone on Telegram are able to chat to your bot. You can find it by searching for its name on Telegram.

Detailed information about this can also be found in the [Rasa Docs](https://rasa.com/docs/core/connectors/#telegram-connector).


#### In case you want to install Rasa X on Google Cloud with Docker Compose:
- > curl -sSL -o install.sh https://storage.googleapis.com/rasa-x-releases/0.35.1/install.sh
- > sudo bash ./install.sh

- > cd /etc/rasa
- > sudo docker-compose up -d

- > cd /etc/rasa
- > sudo python3 rasa_x_commands.py create --update admin me <your_password>

- > sudo docker-compose restart

Open your IP address in a tab.


## 👩‍💻 Overview of the files

`data/stories.yml` - contains stories for Rasa Core

`data/nlu.yml` - contains example NLU training data

`data/rules.yml` - contains rules that is executed once is triggered

`actions/actions.py` - contains custom action/api code

`domain.yml` - the domain file for Core

`config.yml` - the config file

`credentials.yml` - contains credentials for the use with Telegram

`endpoints.yml` - contains url for endpoint


## 🛠 Makefile overview
Run `rasa -h` to see an overview of all make commands available.

`rasa train nlu` - Train the NLU model.

`rasa train` - Train the Core model.

`rasa interactive` - Run the Curvi interactive learning mode.

`rasa shell` - Run the bot on the command line.

`rasa run actions` - Start the action server.

`rasa run` - Run the bot in the Telegram channel.

## Resume of Curvi
So, now is pretty easy and fast to anyone who would like to make a resume. It takes some minutes and you'll be able to 
apply for as many jobs as you want.