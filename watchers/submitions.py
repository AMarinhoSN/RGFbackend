from watchdog.events import PatternMatchingEventHandler
import watchdog.observers
import time
import os
from datetime import datetime
# database interface
import dbInterface.mongoInterface
# === FUNCTIONS ================================================================

def process_submit_fl(flpath):
    '''
    handle submit file data
    '''
    f = open(flpath, 'r')
    # default values
    routine = 'standard'
    reads_lenght = 150

    # dd/mm/YY
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    for line in f:
        if line.startswith('routine'):
            routine = line.split('=')[-1].replace('\n', '')
        if line.startswith('reads_length'):
            reads_lenght = line.split('=')[-1].replace('\n', '')
    dct = {'routine': routine, 'reads_lenght': reads_lenght,
            'submition_date':dt_string}
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
    '''
    TO DO add description
    '''
    def __init__(self, cred_flpath, database_name):
        '''
        '''
        # Set the patterns for PatternMatchingEventHandler
        PatternMatchingEventHandler.__init__(self,
                                             patterns=['submit.txt'],
                                             ignore_directories=True,
                                             case_sensitive=True)
        # credential file
        self.cred_flpath = cred_flpath
        self.database_name = database_name

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
        run_dct['fastq_at_dir'] = fastq_lst
        # feed MONGO DB

        # connect to database
        # TODO - handle failed connection
        DBclient = dbInterface.mongoInterface.DataBase(self.cred_flpath,
                                               database_name=self.database_name)

        # feed run collection
        print("  > Adding new sequencing batch document")
        DBclient.insert_new_seqBatch(run_dct)

        # feed sample collection
        # TODO - compliance test
        # TODO - implement feeding database

        # [TODO] status notification system

    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        # Event is modified, you can process it now


if __name__ == "__main__":
    #src_path = r"test_dir/users/"
    #src_path = r"/HDD/server/chagas/raw_data/"
    cred_flpath='/HDD/Projects/module_2_dev/tutorials/mongo_sing/mongo_credentials'
    src_path = r"/HDD/Projects/git_stuff/RGFbackend/test_dir/"
    dbName = 'rgf_db'
    event_handler = Handler(cred_flpath, dbName)
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
