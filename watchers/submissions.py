from watchdog.events import PatternMatchingEventHandler
import watchdog.observers
import time
import os
from datetime import datetime
import sys
# database interface
import dbInterface.mongoInterface
# routines classes
import movingParts
# === FUNCTIONS ================================================================


def process_submit_fl(flpath):
    '''
    handle submit file data
    '''

    # get date and time of submition
    # dd/mm/YY
    now = datetime.now()

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    dct = {'submition_date': dt_string}
    # get keys and values on submit file
    # WARNING: key and values should not have spaces
    f = open(flpath, 'r')
    for line in f:
        try:
            ln_data = line.split('=')
            assert(len(ln_data) == 2)
            key = ln_data[0].replace(' ', '').replace('\n', '')
            value = ln_data[1].replace(' ', '').replace('\n', '')
            dct[key] = value
        # if there is indefined value
        except(IndexError):
            return 'Invalid line at submit file: "'+line+'"'
    return dct


def get_run_parameters(submit_flpath, submit_def_flpath, log_flpath):
    '''
    get parameters for a given run based on default submit files and submit
    file. In addition, update log file.
    Parameters
    ==========

    '''
    # open log file
    log_fl = open(log_flpath, 'a')

    # load default arguments
    submit_def_dct = process_submit_fl(submit_def_flpath)
    run_parameters = {}
    blocked_keys = []
    for def_keys in submit_def_dct.keys():
        if def_keys.startswith('b_'):
            # check for blocked arguments
            key_nm = def_keys[2:len(def_keys)]
            blocked_keys.append(key_nm)
            run_parameters[key_nm] = submit_def_dct[def_keys]
        else:
            run_parameters[def_keys] = submit_def_dct[def_keys]

    # load arguments set at submit
    submit_dct = process_submit_fl(submit_flpath)
    if type(submit_dct) == str:
        # write invalid argument provided and kill the submition
        log_fl.write('!! ERROR : ', submit_dct, '\n')

    for prov_key in submit_dct.keys():
        if prov_key in blocked_keys:
            wln = '! WARNING : '+prov_key+' was ignored (set by admins only)'
            log_fl.write(wln+'\n')
            continue
        else:
            run_parameters[prov_key] = submit_dct[prov_key]

    # write detected parameters at log file
    log_fl.write(' > Detected parameters:\n')
    for k in run_parameters:
        log_fl.write(' >> '+k+' = '+str(run_parameters[k])+'\n')
    # return the parameters
    return run_parameters


# get metadata [user name, run code, routine]


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

    def __init__(self, cred_flpath, database_name, params_dir):
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
    # parameters directory
    self.params_dir = params_dir

    def on_created(self, event):
        # Event is created
        print("Watchdog received created event - % s." % event.src_path)
        # create log file
        log_fl = open(event.src_path+'/submition.log', 'a')
        # write submition detected date on log
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        log_fl.write(
            '! sequence batch submition request detected at '+dt_string+'\n'
            )
        # --- LOAD METADATA CONTENT -------------------------------------------
        log_fl.write('@ loading metadata from paths...\n')
        # get run code and genome provider code
        metadata_dct = get_metadata_from_path(event.src_path)

        # update log file
        log_fl.write(' > run_code = '+metadata_dct['run_code']+'\n')
        log_fl.write(' > gprvdr_code = '+metadata_dct['gprvdr_code']+'\n')

        # get list of files on the submit file dir
        files_dir = os.listdir('/'.join(event.src_path.split('/')[0:-1]))
        fastq_lst = [x for x in files_dir if x.endswith('fastq.gz')]

        # get metadata from file name
        samples_lst = []
        for f in fastq_lst:
            samples_lst.append(get_fastq_metadata(f))
        # --- GET ROUTINE PARAMATERS ------------------------------------------
        # get parameters from submit txt
        log_fl.write('@ parsing submit.txt from paths...\n')
        # submit_dct = process_submit_fl(event.src_path)

        submit_dct = get_run_parameters(
                            event.src_path+'submit.txt',
                            self.params_dir+'submit_def.txt',
                            event.src_path+'submition.log')

        # get default parameters

        # get parameters [check for default routine values]
        # ----------------------------------------------------------------------
        # WARNING TEMPORARY SOLUTION
        # the default values will be hardset here just for convenience
        # Those keys and values should be
        # ----------------------------------------------------------------------

        # mount documents
        run_dct = {**metadata_dct, **submit_dct}
        run_dct['files_at_dir'] = files_dir
        run_dct['fastq_at_dir'] = fastq_lst
        log_fl.write('> '+str(len(fastq_lst)), ' total fastq files detected')
        # --- START ANALISES ROUTINE -------------------------------------------
        #
        # create sequence batch object
        seqbatch_obj = movingParts.routines.seqBatch(
            run_code=metadata_dct['run_code'],
            gprvdr_code=metadata_dct['gprvdr_code'],
            dir_path=metadata_dct['full_path'],
            submition_date=dt_string)
        # [to do] create routine object and check arguments complaince
        # [to do] submit jobs
        # [TODO] status notification system

        # --- FEED MONGO DB ----------------------------------------------------
        # connect to database
        # TODO - handle failed connection
        DBclient = dbInterface.mongoInterface.DataBase(self.cred_flpath,
                                                       database_name=self.database_name)

        # feed run collection
        print("  > Adding new sequencing batch document")
        DBclient.insert_new_seqBatch(run_dct)

    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        # Event is modified, you can process it now


class subm_watcher:
    '''
    TO DO add description

    '''

    def __init__(self, cred_flpath, src_path, db_name, params_dir):
        '''
        '''
        self.cred_flpath = cred_flpath
        self.dir_path = src_path
        self.db_name = db_name
        self.params_dir = params_dir

    def activate(self):
        '''
        activate submissions watcher
        '''
        # create event handler
        event_handler = Handler(self.cred_flpath, self.db_name, self.params_dir)
        # create observer and add event handler routines
        self.observer = watchdog.observers.Observer()
        self.observer.schedule(event_handler, path=self.dir_path,
                               recursive=True)
        # activate observer
        self.observer.start()

    def deactivate(self):
        '''
        stop submissions watcher
        '''
        self.observer.stop()
        self.observer.join()


if __name__ == "__main__":
    cred_flpath = sys.argv[1]
    src_path = sys.argv[2]
    dbName = sys.argv[3]
    params_dir = sys.argv[4]
    watcher = subm_watcher(cred_flpath, src_path, dbName, params_dir)
    watcher.activate()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.deactivate()
