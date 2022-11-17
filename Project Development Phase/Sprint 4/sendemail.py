import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *


def send_email():
    from_email=Email('211719104145@smartinternz.com')
    to_email=To('suriyadanasekar18@gmail.com')
    subject = 'Sending with SendGrid is Fun'
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, to_email, subject, content)
    
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(mail)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
        
send_email()