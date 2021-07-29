from watchdog.events import PatternMatchingEventHandler
import watchdog.observers
import time

# === FUNCTIONS ================================================================
def process_submit_fl(flpath):
    '''
    handle submit file data
    '''
    f = open(flpath, 'r')
    # default values
    routine = 'standard'
    reads_lenght = 150

    for line in f:
        if line.startswith('routine'):
            routine = line.split('=')[-1].replace('\n','')
        if line.startswith('reads_length'):
            reads_lenght = line.split('=')[-1].replace('\n','')
    dct = {'routine':routine, 'reads_lenght':reads_lenght}
    return dct

# TODO get metadata [user name, run code, routine
def get_metadata_from_path(path):
    '''
    get sequencing run metadata from dir structure and return a dictionary
    This function assumes the following dir structure:
    /source/dir/users/user_1/INPUT/run_xx/'
    '''
    path_dirs = path.split('/')
    run_code = path_dirs[-2]
    gprvdr_code = path_dirs[-4]
    dct = {'run_code':run_code,
            'gprvdr_code':gprvdr_code,
            'full_path':path}
    return dct


# ==== Watchdog class ==========================================================
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

        # get metadata from dir structure
        metadata_dct = get_metadata_from_path(event.src_path)
        # get data from submit dct
        submit_dct = process_submit_fl(event.src_path)
        print([metadata_dct, submit_dct])
        # mount documents
        run_dct = {**metadata_dct, **submit_dct}
        print(run_dct)
        # [TODO] get data from fastq name

        # [TODO] feed MONGO DB

    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        # Event is modified, you can process it now

#/source/dir/users/ua/INPUT/
#path = '/source/dir/users/ua/INPUT/run_xx/'

if __name__ == "__main__":
    src_path = r"test_dir/users/"
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
