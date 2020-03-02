import os
from smtplib import SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# GLOBAL VARIABLES
EMAIL_LOGIN = os.environ.get('EMAIL_LOGIN')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

EMAIL_BODY = '''Hey there, below you you will find what websites are talkign about:

<HEADLINE_1>
<HEADLINE_2>

So this is it. Have a good day'''

class EmailHandler():
    '''accepts list of headlines and sends emails'''

    def __init__(self, headlines_list=[['Testing hardcoded headline', 'https://www.generalistlab.com']], recipients=['edvinaspam-1@yahoo.com']):
        self.headlines_list = headlines_list
        self.recipients = recipients

    def edit_body(self):
        '''edits msg body template'''
        msg_body = EMAIL_BODY.replace('<HEADLINE_1>', self.headlines_list[0][0])
        return msg_body
    
    def get_message(self, recipient_email):
        '''returns a message object'''
        msg = MIMEMultipart()
        # Setting parameters of email:
        msg['From'] = f'Python Service <{EMAIL_LOGIN}>'
        msg['To'] = recipient_email
        msg['Subject'] = 'Python would like to inform you'

        # body:
        print('Constructing body')
        msg_body = self.edit_body()
        msg.attach(MIMEText(msg_body, 'plain'))
        print('Body constructed. Returning msg')
        return msg
    
    def run(self):
        # Open connection
        print('Creating a server')
        with SMTP_SSL(host='smtp.gmail.com', port=465) as s:
            s.login(EMAIL_LOGIN, EMAIL_PASS)
            for recipient_email in self.recipients:
                # Create msg
                msg = self.get_message(recipient_email)
                # Send message
                s.send_message(msg)
        print(f'Finished sending those emails')


if __name__ == '__main__':
    client = EmailHandler()
    client.run()
    # pass
