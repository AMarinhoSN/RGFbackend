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

rtn_path = "/HDD/Projects/git_stuff/RGFbackend/test_dir/routines/iam_sarscov2.rtn"
rtn_dct = load_rtn_data(rtn_path)

# TODO : create routine class
#        this class will provide methods to:
#       1 - generate submition files
#       2 - submit to job queue
#       3 - run locally
