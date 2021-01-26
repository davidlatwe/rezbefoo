

def install():
    import os
    import shutil
    import rez.cli

    script_dir = os.path.dirname(__file__)
    for script in os.listdir(script_dir):
        if script.startswith("_"):
            continue
        shutil.copy2(os.path.join(script_dir, script), rez.cli.__path__[0])


if __name__ == "__main__":
    install()
