from tkinter import filedialog

from flask import Flask, request, render_template
import subprocess
import time
import os
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import filedialog, font
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler

# main for listener
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

app = Flask(__name__)
path =""
email=""
thisdict = {"path": path , "email":email}

@app.route("/")
def index():
    return render_template('index.html',path=thisdict["path"],email=thisdict["email"])


@app.route("/browse", methods=['POST'])
def browse():
    command = request.form['x']
    thisdict['path'] = filedialog.askdirectory()
    thisdict['email'] = request.form['email']
    return index()

@app.route("/execute", methods=['POST'])
def execute():
    search()
    return index()


def search():  # command of search button
    path = thisdict['path']
    thisdict["email"] = thisdict['email']
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()

    return ''

def Sendm(s, x):
    subject = "new file"
    body = "This is an email with attachment sent from Python"
    sender_email = "project24smtp@gmail.com"
    receiver_email = x
    password = "1312Smtp"
    #
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    filename = s.replace('\\', '/')
    # filename = "123a.jpg"  # In same directory as script

    # Open  file in binary mode

    with open(filename, "rb+") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    print(filename)
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


def on_created(event):
    email = thisdict.get("email")
    Sendm(str(event.src_path), email)
    print("the mail was sent")
    


my_event_handler.on_created = on_created




if __name__ == "__main__":
    app.run(debug='True')
