""" Logger for displaying info based on Verbosity """
import time
import global_vars

def log_timer(marker="", verbose=0):
    """ Shows the time since app started """
    if global_vars.VERBOSE >= verbose and marker:
        print("{:.4f} -- {}".format(
            (time.time() - global_vars.START_TIME),
            marker
        ))

def log_output(text, verbose):
    """ Prints log text if it has the right verbosity """
    if global_vars.VERBOSE >= verbose and text:
        print(text)
