import sys
from functools import wraps
import traceback
import os

def log(msg):
    # get current frame
    try:
        raise Exception
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        f = exc_traceback.tb_frame.f_back

    co = f.f_code
    sys.stderr.write("%s:%s :: %s : %s\n" %
                     (co.co_filename, f.f_lineno, co.co_name, msg))
    sys.stderr.flush()


def catch_err(f):
    @wraps(f)
    def __try(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseException:
            log("caught exception in function %s:\n %s" % \
                (f.__name__, traceback.format_exc()))
            print(("Current process UID: {0}, GID: {1}, GIDS: {2}".format(
                os.getuid(), os.getgid(), os.getgroups())))

    return __try


def main():
    log("test message")


if __name__ == "__main__":
    main()
