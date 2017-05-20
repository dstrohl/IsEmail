import logging
import sys


log = logging.getLogger('EmailParser')
log.setLevel(0)
stream_handler = logging.StreamHandler(sys.stdout)
log.addHandler(stream_handler)

log_critical = log.critical
log_error = log.error
log_warning = log.warning
log_info = log.info
log_debug = log.debug


def log_ddebug(msg, *args, **kwargs):
    # print(msg % args)
    log.log(9, msg, *args, **kwargs)

