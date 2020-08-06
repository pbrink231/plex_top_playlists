""" Utility methods for the plex library """
import sys

def show_dict_progress(curnum, total):
    """ Displays the progress of adding to the dictionary """
    bar_length = 50
    filled_len = int(round(bar_length * curnum / float(total)))
    percents = round(100.0 * (curnum / float(total)), 1)
    prog_bar = '=' * filled_len + '-' * (bar_length - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (prog_bar, percents, '%', "{0} of {1}".format(
        curnum,
        total
    )))
    sys.stdout.flush()
