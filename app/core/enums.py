import random
from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def random_choice(cls):
        return random.choice(cls.list())


class Status(ExtendedEnum):
    APPLIED = 'Applied'
    FORWARDED = 'Forwarded'
    INTERVIEWED = 'Interviewed'
    SELECTED = 'Selected'
    REJECTED = 'Rejected'


class Priority(ExtendedEnum):
    HIGH = 'High'
    LOW = 'Low'
    MEDIUM = 'Medium'


class Clan(ExtendedEnum):
    JS = 'JS'
    GOLANG = 'GoLang'
    PYTHON = 'Python'
    UI_UX = 'UI/UX'
    DOT_NET = 'Dot Net'
    JAVA = 'Java'
    MANAGEMENT = 'Management'
    MARKETING = 'Marketing'
    PIHR = 'PiHR'
    PHP = 'PHP'
    MOBILE_APPS = 'Mobile Apps'
    SQA = 'SQA'


class MailType(ExtendedEnum):
    SIGN_UP = 'Sign up'
    APPLICATION_CREATE = 'Application Create'
    REMARK_CONTENT_MENTION = 'Remark Content Mention'
    RESET_PASSWORD = 'Reset Password'
    USER_INVITE = 'User Invite'
