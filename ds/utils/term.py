import subprocess


def get_tty_size(fallback=None):
    try:
        return map(int, subprocess.check_output(['stty', 'size']).split())
    except:
        pass
    return fallback or (None, None)


def get_tty_width():
    _, width = get_tty_size()
    return width
