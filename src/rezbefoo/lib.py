

def get_message():
    from rez.config import config
    message = config.plugins.application.foo.message
    return message
