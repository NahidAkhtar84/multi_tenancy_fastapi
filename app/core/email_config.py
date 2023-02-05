import smtplib
from email.message import EmailMessage

from fastapi import status, Request, HTTPException

from app.core.utils import encode_token
from app.core.enums import MailType
from app.core.config import settings
from app.templates import sign_up_mail, application_creation_mail, user_invitation_mail, remark_mentioned_email, reset_password_mail
from app.core.log_config import logger


def send_email(email, type: int = None, **kwargs):
    if type == MailType.SIGN_UP.value:
        subject = "ATS Verification Mail"
        _data = kwargs.get('data', None)
        body = sign_up_mail(data=_data)

    elif type == MailType.APPLICATION_CREATE.value:
        if not settings.APPLICATION_CREATE_MAIL:
            return
        subject = "ATS Verification Mail"
        _data = kwargs.get('data', None)
        body = application_creation_mail(data=_data)

    elif type == MailType.RESET_PASSWORD.value:
        subject = "ATS Reset Password Mail"
        _data = kwargs.get('data', None)
        body = reset_password_mail(data=_data)

    elif type == MailType.USER_INVITE.value:
        subject = "ATS User Verification Mail"
        _data = kwargs.get('data', None)
        body = user_invitation_mail(data=_data)

    elif type == MailType.REMARK_CONTENT_MENTION.value:
        subject = "ATS | Mentioned on a job application"
        _data = kwargs.get('data', None)
        body = remark_mentioned_email(data=_data)
    else:
        logger.error("Couldn't recognize Email type")
        return


    # Email Send configuration
    email_message = EmailMessage()
    email_message['subject'] = subject
    email_message['From'] = settings.MAIL_USER
    email_message['To'] = email
    email_message.add_alternative(body, subtype='html')

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(settings.MAIL_USER, settings.MAIL_PASSWORD)
        smtp.send_message(email_message)
