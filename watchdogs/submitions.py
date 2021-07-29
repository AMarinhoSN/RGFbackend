from watchdog.events import PatternMatchingEventHandler
import watchdog.observers
import time
import os
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
            routine = line.split('=')[-1].replace('\n', '')
        if line.startswith('reads_length'):
            reads_lenght = line.split('=')[-1].replace('\n', '')
    dct = {'routine': routine, 'reads_lenght': reads_lenght}
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
    dct = {'run_code': run_code,
           'gprvdr_code': gprvdr_code,
           'full_path': path}
    return dct


def get_fastq_metadata(fastq_file):
    '''
    process fastq naming metadata
    '''
    # get list of fastq submitted
    fastq_mtdata = fastq_file.split('.')[0].split('_')
    sample_code = fastq_mtdata[0]
    plate_pos = fastq_mtdata[1]
    something = fastq_mtdata[2]
    sense = fastq_mtdata[3]
    number = fastq_mtdata[4]

    dct = {'sample_code': sample_code, 'plate_pos': plate_pos,
           'sense': sense, 'filename': fastq_file}
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

        # get run code and genome provider code
        metadata_dct = get_metadata_from_path(event.src_path)

        # get parameters from submit txt
        submit_dct = process_submit_fl(event.src_path)

        # get list of files on the submit file dir
        files_dir = os.listdir('/'.join(event.src_path.split('/')[0:-1]))
        fastq_lst = [x for x in files_dir if x.endswith('fastq.gz')]

        # get metadata from file name
        samples_lst = []
        for f in fastq_lst:
            samples_lst.append(get_fastq_metadata(f))

        # mount documents
        run_dct = {**metadata_dct, **submit_dct}
        run_dct['files_at_dir'] = files_dir
        print(" -- RUN DOCUMENT --")
        print(run_dct)
        print(' -- SAMPLE DOCUMENTS --')
        print(samples_lst)
        # [TODO] feed MONGO DB
        # feed run collection
        # feed sample collection

    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        # Event is modified, you can process it now


if __name__ == "__main__":
    #src_path = r"test_dir/users/"
    #src_path = r"/HDD/server/chagas/raw_data/"
    src_path = r"/HDD/Projects/RGFbackend/test_box/"
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
    observer.join()
