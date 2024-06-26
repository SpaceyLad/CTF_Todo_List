# CTF_Todo_List

Welcome to my first CTF challenge! Here is a nice little story for context :]

Your friend Mabel Higgins has come to you with an exciting request. She's just created a new website using Flask, a Python micro web framework. Although she's new to Flask, she's convinced that his website is 100% secure. She's asked you to put your cybersecurity skills to the test and try to find any vulnerabilities in her site.

Can you prove her wrong? Can you find the 4 hidden flags that demonstrate the vulnerabilities in her code?

The site is a simple to-do list application. Your Mabel Higgins is confident that she's followed all the best practices in her Flask application. But remember, no system is entirely secure. Keep your eyes open for any XXXXXXX XXXXXX XXXXXXX and potential XXXXXXXX issues.

Happy hacking <3

![webapp](https://github.com/SpaceyLad/CTF_Todo_List/assets/87969837/09edd5b5-8a0c-40a2-b6da-ccbd6238618a)



# General

### Getting Started

To get a local copy up and running, follow these simple steps.
#### Prerequisites

This project uses Python 3.8 or above, and pip for package management. Make sure you have them installed.

#### Installation

* Clone the repository and go into it

`git clone https://github.com/spaceylad/todo-list.git`

`cd CTF_Todo_List`

* Install the requirements and run the application

`pip install -r requirements.txt`

`python3 run.py`

## Run as Docker

* Start Docker, then in CMD, go to the App directory.

`docker build -t todo_flask_app .`

`docker run -p 5000:5000 todo_flask_app`

* Then visit the app on 127.0.0.1:5000
