# parser for rtn files
REQUIRED_DCTS = ['metadata', 'paths', 'input_names', 'default_params',
                'dependencies']

# --- FUNCTIONS ----------------------------------------------------------------
#
# RTN FILES
def catalog_missing_keys(rtn_flpth):
    '''
    check if required keys are present at an rtn_flpth
    '''
    rtn_f = open(rtn_flpth, 'r')
    keys_at_file = []
    # get keys defined on file
    for line in rtn_f:
        if line.startswith('>'):
            field_name = line.split('>')[1].replace(' ','').replace('\n','')
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
    missing_keys= catalog_missing_keys(rtn_path)
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
            curr_field_name = line.split('>')[1].replace(' ','').replace('\n','')
            dct[curr_field_name] = {}
            continue

        # handle 'key = value' format
        if curr_field_name in equal_fmt_fields:
            ln_data = line.split('=')
            key = ln_data[0].replace(' ','')
            value = ln_data[1].replace(' ','').replace('\n','')
            dct[curr_field_name][key] = value
            continue

        # handle input names format (key :: value)
        if curr_field_name in  ['input_names']:
            # handle args order line
            if line.startswith('<'):
                args_lst = []
                ln_data = line.split('<')
                for arg_prvd in ln_data:
                    if arg_prvd == '':
                        continue
                    arg_nm = arg_prvd.replace('>','').replace(' ','').replace('\n','')
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
            key = ln_data[0].replace(' ','')
            value = ln_data[1].replace(' ','').replace('\n','')
            dct[curr_field_name][key] = value
            continue

    return dct

def get_args_command_line(routine, sample, reference_genome, num_threads,
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
        if key in ['R1_read','R2_read']:
            if key.startswith('R1'):
                value = sample.R1_read
            if key.startswith('R2'):
                value = sample.R2_read
        # get remaining settings [TODO get default values from routine]
        if key == 'reference_genome':
            value = reference_genome
        if key == 'sample_code':
            value = sample_a.code
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

    def submit_to_queue(self, routine_obj, engine='pbs'):
        '''
        submit
        '''
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



    def submit_to_queue(self, sample_dct, engine='pbs'):
        '''
        '''
        # for each fastq, do:
            # create output directory
            # create submition file
            # get bash line and add to submition file

        pass

    def run(self, sample_obj, reference_genome, adapters_file, num_threads,
            min_len, depth, source_dir, local=True):
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
            mkdir_cmd = "mkdir "+ source_dir+'/params/'
            process = subprocess.run(mkdir_cmd, shell=True,check=True)
            # copy reference genome file
            copy_ref_cmd = "cp "+ reference_genome +' '+ source_dir+'/params/'
            process = subprocess.run(copy_ref_cmd, shell=True,check=True)
            # copy adapaters file
            copy_adp_cmd = "cp "+ adapters_file +' '+ source_dir+'/params/'
            process = subprocess.run(copy_adp_cmd, shell=True,check=True)

            return None

        # copy parameters files to source dir
        __prep_directory()
        # get bash line
        # get only file names
        ref_gnm = reference_genome.split('/')[-1]
        adpt_fln = adapters_file.split('/')[-1]

        cmd_lst = get_args_command_line(self, sample_a, ref_gnm,
                                    num_threads, min_len, adpt_fln)
        # run locally
        if local == True:
            # run bash command
            process = subprocess.run(' '.join(cmd_lst), shell=True,check=True)
            # [TO DO] check output files
            # [TO DO] move output files

        #if queue == True:
        # PBS
        # get template for PBS
        # monitor output files generation and create a log/report
        # Slurm


# test
rtn_path = "/HDD/Projects/git_stuff/RGFbackend/test_dir/routines/iam_sarscov2.rtn"
rtn_dct = load_rtn_data(rtn_path)

# TODO : create routine class
#        this class will provide methods to:
#       1 - generate submition files
#       2 - submit to job queue
#       3 - run locally
