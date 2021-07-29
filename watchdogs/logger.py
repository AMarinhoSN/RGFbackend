import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import os

# -------------- CLASSES ------------------------------------------------------


class directory_watcher:
    '''
    this class handles objects designed to monitor changes on a specified dir
    and writes every change on a log file

    ps: this code is based on the example available at
        https://github.com/gorakhargosh/watchdog

    '''

    def __init__(self, path, log_flpath):
        # set attributes
        self.dir_path = path
        self.log_flpth = log_flpath

    def activate(self):
        '''
        start watchdog logging procedure
        '''
        # set logging strings configuration
        logging.basicConfig(filename=self.log_flpth,
                            level=logging.INFO,
                            format='%(asctime)s - %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        # create event handler
        self.event_handler = LoggingEventHandler()

        # create observer
        self.observer = Observer()
        self.observer.schedule(self.event_handler,  path=self.dir_path,
                               recursive=True)
        # start
        self.observer.start()

    def deactivate(self):
        '''
        stop watchdog logging procedure
        '''
        self.observer.stop()
        self.observer.join()


if __name__ == "__main__":
    # start watchdog
    # log_watchdog = dir_watchdog(path=sys.argv[1], log_flpath=sys.argv[2])
    path = sys.argv[1]
    log_flpth = sys.argv[2]
    assert(os.path.isdir(path)), 'path provided is not a directory'
    log_watchdog = directory_watcher(path=path,
                                     log_flpath=log_flpth)
    log_watchdog.activate()

    # set stop condition
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_watchdog.deactivate()
    print(" WATCHDOG WAS MURDERED... by a keyboard interruption.")
