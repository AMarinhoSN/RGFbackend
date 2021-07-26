from watchdog.events import PatternMatchingEventHandler
import watchdog.observers
import time


class Handler(PatternMatchingEventHandler):
    def __init__(self):
        # Set the patterns for PatternMatchingEventHandler
        PatternMatchingEventHandler.__init__(self,
                                             patterns=['submit.txt'],
                                             ignore_directories=True,
                                             case_sensitive=True)

    def on_created(self, event):
        # Event is created
        print("Watchdog received created event - % s." % event.src_path)
        # TODO get metadata [user name, run code, routine
        # feed MONGO DB

    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        # Event is modified, you can process it now


if __name__ == "__main__":
    src_path = r"test_box/users/"
    event_handler = Handler()
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
