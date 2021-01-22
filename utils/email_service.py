from jinja2 import Environment, Template, FileSystemLoader
from email.message import EmailMessage
from datetime import datetime
from smtplib import SMTP_SSL
import os


# GLOBAL VARIABLES
EMAIL_LOGIN = os.environ.get('EMAIL_LOGIN')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
RENDERED_TEMPLATE = 'templates/email.html'
EMAIL_BODY_PLAIN_TEXT = '''Hey, 
Next time, think about using HTML.
No country for old men, sorry'''


class EmailHandler():
    '''accepts list of headlines and sends emails'''

    def __init__(self, headlines_list=[['Sample Headline1', 'https://www.sampleurl.com'], ['Sample Headline1', 'https://www.sampleurl.com']], recipients=['edvinaspam-1@yahoo.com']):
        self.headlines_list = headlines_list
        self.recipients = recipients
        self.joke_to_mail = 'Chuck Norris doesnt read books. He stares them down until he gets the information he wants.'
        self.formated_timestamp = self.get_time()

    @staticmethod
    def get_time():
        '''returns str type time stamp like: 1998.12.21 18:05'''
        t_now = datetime.now()
        return t_now.strftime('%Y.%m.%d %H:%M')

    def render_template(self):
        '''render template and output to file'''
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('email_template.html')
        rendered_template = template.render(
            my_list=self.headlines_list,
            joke_to_mail=self.joke_to_mail,
            time_stamp=self.formated_timestamp)
        self._output_rendered_file(rendered_template)
        return rendered_template

    def _output_rendered_file(self, rendered_template):
        '''outputs html file'''
        with open(RENDERED_TEMPLATE, 'w') as f:
            f.write(rendered_template)
    
    def test_output_rendered_html(self):
        '''created for temp purposes'''
        email_html = self.render_template()
        self._output_rendered_file(email_html)
    
    def get_rendered_email_contents(self):
        '''returns rendered html data'''
        try:
            self.render_template()
            # contents = self.render_template()
            with open(RENDERED_TEMPLATE) as rendered_html:
                contents = rendered_html.read()
                print('Just read html contents. I like what\'s inside lol')
            return contents
        except Exception as e:
            print(f'Error ocurred while trying to read html file. Error: {e}')
    
    def get_message(self, recipient_email):
        '''returns a message object'''
        msg = EmailMessage()
        # Setting parameters of email:
        msg['From'] = f'Python Service <{EMAIL_LOGIN}>'
        msg['To'] = recipient_email
        msg['Subject'] = 'Python would like to inform you'

        # body:
        print('Constructing body')
        html_data = self.get_rendered_email_contents()
        msg.set_content(EMAIL_BODY_PLAIN_TEXT, subtype='plain')
        msg.add_alternative(html_data, subtype='html')
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
    # mail_service = EmailHandler()
    # mail_service.run()
    pass