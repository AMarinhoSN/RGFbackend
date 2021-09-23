from pathlib import Path
import subprocess
import os
# parser for rtn files
REQUIRED_DCTS = ['metadata', 'paths', 'input_names', 'default_params',
                 'dependencies']

# --- FUNCTIONS ----------------------------------------------------------------
#
# RTN FILES --------------------------------------------------------------------


def catalog_missing_keys(rtn_flpth):
    '''
    check if required keys are present at an rtn_flpth
    '''
    rtn_f = open(rtn_flpth, 'r')
    keys_at_file = []
    # get keys defined on file
    for line in rtn_f:
        if line.startswith('>'):
            field_name = line.split('>')[1].replace(' ', '').replace('\n', '')
            keys_at_file.append(field_name)
    # check missing keys
    missing_keys = []
    for req_key in REQUIRED_DCTS:
        if req_key not in keys_at_file:
            missing_keys.append(req_key)
    return missing_keys


def load_rtn_data(rtn_path):
    '''
    load routine information from a rtn file

    Parameters
    ----------
    rtn_path : path
        path of a .rtn file

    Returns
    -------
    A python dictionary
    '''

    # --- sanity check ---------------------------------------------------------
    # check if required keys are present at rtn file
    missing_keys = catalog_missing_keys(rtn_path)
    try:
        assert(len(missing_keys) == 0)
    except(AssertionError):
        print("!ERROR! the following keys are missing:", )
        print("        ", missing_keys)
        msg = 'Required keys are missing'
        raise Exception(msg)
    # --------------------------------------------------------------------------
    # --- PARSE FILE -----------------------------------------------------------
    equal_fmt_fields = ['paths', 'metadata', 'default_params', 'dependencies']
    curr_field_name = None
    dct = {}
    rtn_f = open(rtn_path)
    for line in rtn_f:
        # skip comments
        if line.startswith('#') or line.startswith('\n'):
            continue

        # check if new section creation
        if line.startswith('>'):
            curr_field_name = line.split('>')[1].replace(
                ' ', '').replace('\n', '')
            dct[curr_field_name] = {}
            continue

        # handle 'key = value' format
        if curr_field_name in equal_fmt_fields:
            ln_data = line.split('=')
            key = ln_data[0].replace(' ', '')
            value = ln_data[1].replace(' ', '').replace('\n', '')
            dct[curr_field_name][key] = value
            continue

        # handle input names format (key :: value)
        if curr_field_name in ['input_names']:
            # handle args order line
            if line.startswith('<'):
                args_lst = []
                ln_data = line.split('<')
                for arg_prvd in ln_data:
                    if arg_prvd == '':
                        continue
                    arg_nm = arg_prvd.replace('>', '').replace(
                        ' ', '').replace('\n', '')
                    # be sure the arguments provided were previously defined
                    try:
                        assert(arg_nm in dct[curr_field_name].keys())
                    except(AssertionError):
                        msg = 'Invalid argument referenced at order of arguments line'
                        print('!ERROR!: ', arg_nm, 'not defined.')
                        raise Exception(msg)
                    args_lst.append(arg_nm)
                # store
                dct[curr_field_name]['order_of_args'] = args_lst
                continue
            ln_data = line.split('::')
            key = ln_data[0].replace(' ', '')
            value = ln_data[1].replace(' ', '').replace('\n', '')
            dct[curr_field_name][key] = value
            continue

    return dct


def get_args_command_line(routine, sample, reference_genome, depth, num_threads,
                          min_len, adapters_file):
    '''
    Get arguments values of a given pair of routine and sample according to
    the order set at routine config file ('.rtn').

    Parameters
    ----------
    [TO DO] add description
    '''

    cmd_lst = [routine.bash_path]
    for key in routine.input_names['order_of_args']:
        # get routine specific values
        if key.endswith('container_path'):
            value = routine.paths[key]

        # get sample specific values
        if key == 'source_dir':
            value = sample.source_dir
        # check if sample read files paths
        if key in ['R1_read', 'R2_read']:
            if key.startswith('R1'):
                value = sample.R1_read
            if key.startswith('R2'):
                value = sample.R2_read
        # get remaining settings [TODO get default values from routine]
        if key == 'reference_genome':
            value = reference_genome
        if key == 'sample_code':
            value = sample.code
        if key == 'num_threads':
            value = num_threads
        if key == 'depth':
            value = depth
        if key == 'min_len':
            value = min_len
        if key == 'adapters_file':
            value = adapters_file

        cmd_lst.append(str(value))

    return cmd_lst

# --- SAMPLE PREPARATION -------------------------------------------------------


def get_fastq_metadata(fastq_file):
    '''
    process fastq naming metadata
    '''
    # get list of fastq submitted
    fastq_mtdata = fastq_file.split('.')[0].split('_')
    sample_code = fastq_mtdata[0]
    plate_pos = fastq_mtdata[1]
    # something = fastq_mtdata[2]
    sense = fastq_mtdata[3].capitalize()
    try:
        assert(sense in ['R1', 'R2'])
    except(AssertionError):
        raise Exception("Invalid sense naming. Sense must be 'R1' or 'R2'")

    # number = fastq_mtdata[4]

    dct = {'sample_code': sample_code, 'plate_pos': plate_pos,
           sense+'_read': fastq_file}
    return dct


def get_samples_dct(data_dir):
    '''
    given a list fastq files, process filenames and create dictionaries containg
    samples file data.

    Parameters
    ----------
    data_dir : path
        path of sequence batch data files

    Returns
    -------
    A list of dictionaries containing samples data
    '''
    # santy check --------------------------------------------------------------
    # be sure the input is a valid directory
    assert(Path(data_dir).is_dir()), data_dir+' is not a dir'
    # --------------------------------------------------------------------------
    # get fastq files list
    files_at_dir = os.listdir(data_dir)
    fastq_lst = [x for x in files_at_dir if x.endswith('fastq.gz')]

    # for each pairs of fastq, create a dictionary containing samples data
    samples_dct_lst = []
    sample_codes_lst = []

    for fastq in fastq_lst:
        # get metadata
        sample_dct = get_fastq_metadata(fastq)
        # add source dir
        sample_dct['source_dir'] = data_dir
        scode = sample_dct['sample_code']
        # get sense of current fastq
        sense = [x for x in list(sample_dct.keys())
                 if x.startswith('R1') or x.startswith('R2')]
        assert(len(sense) == 1), 'more then one key starting with R1 or R2'
        sense = sense[0]
        # avoid process files of same sample more then once
        if scode not in sample_codes_lst:
            sample_codes_lst.append(scode)
            # get pair name
            if sense.startswith('R1'):
                comp_sense = 'R2'
            if sense.startswith('R2'):
                comp_sense = 'R1'
            fastq_mtdata = fastq.split('.')[0].split('_')
            fastq_mtdata[3] = comp_sense
            comp_filename = '_'.join(fastq_mtdata)+'.fastq.gz'
            # sanity check -----------------------------------------------------
            # be sure the pair file exist
            assert(Path(data_dir+comp_filename).is_file())
            # ------------------------------------------------------------------
            # store complementary sense filename
            sample_dct[comp_sense+'_read'] = comp_filename
            samples_dct_lst.append(sample_dct)
            continue
    return samples_dct_lst

# --- QUEUE SUBMITION ----------------------------------------------------------


def write_subfl(template_flpth, new_flpath, job_name, bash_line,
                out_dir, prefix, num_threads=8, nodes=1):
    '''
    write a new queue submition file for a sample processing based on a template
    provided.
    A command line file will be added bellow any line starting with
    "#>add_bash_here<"

    Parameters
    ----------
    template_flpth:<path>
        file path of a template file
    '''

    # [TO DO] Sanity checks

    if out_dir.endswith('/') is False:
        out_dir = out_dir+'/'

    # Copy lines from template file and add specific command line to new
    # submition file
    with open(template_flpth, 'r') as temp:
        new_fl = open(new_flpath, 'w')
        for line in temp:
            # add job name
            if line.startswith('#PBS -N '):
                new_fl.write('#PBS -N '+job_name+'\n')
                continue
            # add threads and nodes
            if line.startswith('#PBS -l '):
                new_line = '#PBS -l nodes=' + \
                    str(nodes)+':ppn='+str(num_threads)+"#shared"
                new_fl.write(new_line)
                continue
            # add output files
            if line.startswith('#PBS -o '):
                new_line = '#PBS -o ' + out_dir+prefix+'_pbs_out.dat'
                new_fl.write(new_line)
                continue

            if line.startswith('#PBS -e '):
                new_line = '#PBS -e ' + out_dir+prefix+'_pbs_err.dat'
                new_fl.write(new_line)
                continue

            # add bash line
            if line.startswith('#>add_bash_here<'):
                new_fl.write(bash_line+'\n')
                continue
            # copy everything else
            else:
                new_fl.write(line)



class sample:
    '''
    class to handle individual sample information
    '''

    def __init__(self, sample_code, plate_pos, R1_read, R2_read, source_dir):
        '''

        '''
        self.code = sample_code
        self.plate_pos = plate_pos
        self.R1_read = R1_read
        self.R2_read = R2_read
        self.source_dir = source_dir

    def assembly_genome(self, routine_obj):
        '''
        run locally the genome assembly routine
        '''
        # [TO DO] adapt bash Filipe script to handle multiple sources
        #         for params and outputs
        pass


class gnmAssembly:
    '''
    class to handle routine genome assembly workflow
    '''

    def __init__(self, rtn_path):
        '''
        create a routine for genome assembly handling.
        '''
        self.rtn_path = rtn_path
        # load parameters content
        self.params_content = load_rtn_data(self.rtn_path)
        self.paths = self.params_content['paths']
        self.input_names = self.params_content['input_names']
        self.default_params = self.params_content['default_params']
        self.dependencies = self.params_content['dependencies']
        self.metadata = self.params_content['metadata']
        # ---- expose some usefull data as atributes
        self.routine_name = self.metadata['routine_name']
        self.bash_path = self.paths['bash_path']

    def run(self, sample_obj, reference_genome, adapters_file, num_threads,
            min_len, depth, source_dir):
        '''
        Run genome assembly routine.

        Parameters
        ----------
        sample_obj : <sample class object>

        reference_genome> <path>
            path to reference genome fasta file

        adapters_file : <path>
            path for adpaters/primers files

        num_threads: <int>
            number of threads
        min_len: <int>

        depth: <int>

        source_dir:<path>
            directory of input files
        '''

        # --- Local functions --------------------------------------------------
        def __prep_directory():
            '''
            this function will copy parameters file to the input dir.

            Parameters
            ----------
            ref_file : <path>
                path to reference genome file

            adapt_file: <path>
                path to adapters file

            source_dir: <path>
                path to input directory

            Return
            ------
            None
            '''
            # create parameters directory
            mkdir_cmd = "mkdir " + source_dir+'/params/'
            process = subprocess.run(mkdir_cmd, shell=True, check=True)
            # copy reference genome file
            copy_ref_cmd = "cp " + reference_genome + ' ' + source_dir+'/params/'
            process = subprocess.run(copy_ref_cmd, shell=True, check=True)
            # copy adapaters file
            copy_adp_cmd = "cp " + adapters_file + ' ' + source_dir+'/params/'
            process = subprocess.run(copy_adp_cmd, shell=True, check=True)

            return None

        # copy parameters files to source dir
        #__prep_directory()
        # get bash line
        # get only file names
        ref_gnm = reference_genome.split('/')[-1]
        adpt_fln = adapters_file.split('/')[-1]

        cmd_lst = get_args_command_line(self, sample_obj, 'params/'+ref_gnm,
                                        depth, num_threads, min_len,
                                        'params/'+adpt_fln)
        # run locally
        # run bash command
        process = subprocess.run(' '.join(cmd_lst), shell=True, check=True)
        # [TO DO] check output files
        # [TO DO] move output files

    def submit_to_queue(self, sample_obj, ref_gnm, adpt_fln, template_flpth,
                        num_threads=8, min_len=75, depth=5, nodes=1):
        '''
        submit routine analyses
        '''
        # [TO DO] sanity checks

        # get bash line to add
        cmd_lst = get_args_command_line(self, sample_obj, ref_gnm, depth,
                                        num_threads, min_len, adpt_fln)
        bash_line = ' '.join(cmd_lst)

        # write submition file
        job_name = sample_obj.code
        new_flpath = sample_obj.source_dir+'/'+job_name+'_job.sh'
        write_subfl(template_flpth, new_flpath, job_name, bash_line,
                    sample_obj.source_dir, job_name, nodes=nodes, 
                    num_threads=num_threads)
        # submit to queue
        sample_obj.jobSbmPath = new_flpath
        # submit to queue according to engine
        subprocess.run('qsub '+new_flpath, shell=True, check=True)
        # [TO DO] monitor output files


class seqBatch:
    '''
    [TO DO] add description
    '''

    def __init__(self, run_code, gprvdr_code, dir_path, submition_date):
        '''
        [TO DO] add description
        '''
        self.run_code = run_code
        self.gprvdr_code = gprvdr_code
        self.dir_path = dir_path
        self.submition_date = submition_date
        # get list of sample code and fastq pairs
        # load sample data
        sample_dct_lst = get_samples_dct(self.dir_path)
        self.samples_obj_lst = []
        for dct in sample_dct_lst:
            sample_i = sample(**dct)
            self.samples_obj_lst.append(sample_i)
        # store codes for easy access
        self.sample_codes = [x.code for x in self.samples_obj_lst]

    def do_samples_GnmAssembly(self, routine_obj, reference_genome,
                               adapter_file, pbs_flpath, num_threads=8,
                               min_len=75, depth=5, nodes=1, queue=True,
                               local=False):
        '''
        [TO DO] add description
        '''
        assert(queue != local), 'either local or queue must be True'
        # submit all sequences to queue
        for s_i in self.samples_obj_lst:
            if queue is True:
                routine_obj.submit_to_queue(s_i, reference_genome, adapter_file,
                                    pbs_flpath, num_threads=num_threads,
                                    min_len=min_len, depth=depth, nodes=1)
            if local is True:
                routine_obj.run(self, reference_genome, adapter_file,
                                num_threads, min_len, depth, self.source_dir)
        pass


#test
#rtn_path = "/HDD/Projects/git_stuff/RGFbackend/test_dir/routines/iam_sarscov2.rtn"
#rtn_dct = load_rtn_data(rtn_path)

# TODO : create routine class
#        this class will provide methods to:
#       1 - generate submition files
#       2 - submit to job queue
#       3 - run locally
