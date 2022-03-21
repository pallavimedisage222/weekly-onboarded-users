from postmarker.core import PostmarkClient

class EmailService():

    def __init__(self, key):
        self.postmark = PostmarkClient(key)

    def send_email(self, fromEmail, to, cc, subject, textbody, attachments, **kwargs):
        return self.postmark.emails.send(
            From=fromEmail,
            To=to,
            Cc=cc,
            Subject=subject,
            TextBody=textbody,
            Attachments=attachments
        )