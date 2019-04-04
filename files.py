import traceback
from fileinput import FileInput


def find_value(key, filepath):
    """looks for a given key in a given file, if it finds a key it will return its value"""

    try:
        with open(filepath, 'r') as f:
            for line in f.readlines():
                position = line.find(key)
                if position != -1:
                    line = line.rstrip()
                    return line[position + len(key) + 1:]

    except FileNotFoundError as e:
        print(traceback.format_exc())
        return False
    except FileExistsError:
        print(traceback.format_exc())
        return False


def save_value(key, value, filepath):
    """writes the given value to the given key in the given file"""

    try:
        with FileInput(filepath, inplace=1) as f:
            for line in f:
                line = line.rstrip()
                if key in line:
                    line = line.replace(line, key + ' ' + value)
                print(line)
        return True
    except Exception as e:
        print(e)
        return False


save_value('client_id', 'chuj w dupsko HWDP', 'tmp.txt')
