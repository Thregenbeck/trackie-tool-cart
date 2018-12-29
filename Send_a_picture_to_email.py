#!/usr/bin/python

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
import picamera
import time
def take_a_picture():
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.start_preview()
        time.sleep(2)
        camera.capture('testpicture.jpg')

def send_a_picture():
    gmail_user = "pipictures314@gmail.com"
    gmail_pwd = "Robotics314"

    def mail(to, subject, text, attach):
       msg = MIMEMultipart()

       msg['From'] = gmail_user
       msg['To'] = to
       msg['Subject'] = subject

       msg.attach(MIMEText(text))

       part = MIMEBase('application', 'octet-stream')
       part.set_payload(open(attach, 'rb').read())
       Encoders.encode_base64(part)
       part.add_header('Content-Disposition',
               'attachment; filename="%s"' % os.path.basename(attach))
       msg.attach(part)

       mailServer = smtplib.SMTP("smtp.gmail.com", 587)
       mailServer.ehlo()
       mailServer.starttls()
       mailServer.ehlo()
       mailServer.login(gmail_user, gmail_pwd)
       mailServer.sendmail(gmail_user, to, msg.as_string())
       mailServer.close()

    mail("pipictures314@gmail.com",
       "Hello from python!",
       "This is a email sent with python",
       "testpicture.jpg")

#take_a_picture()
#send_a_picture()    
