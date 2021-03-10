

def say():
    from rez.config import config
    message = config.plugins.application.foo.message
    print(message)
