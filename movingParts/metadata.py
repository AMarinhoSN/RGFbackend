import datetime
# --- FUNCTIONS ---------------------------------------------------------------


def load_gprm_format(file_path):
    '''
    load the gse parameters standard formating
    [TODO] add gprm parameters
    '''
    f = open(file_path, 'r')
    mtdt_def = {}
    for ln in f:
        l_preprc = ln.replace(' ', '').replace('\n', '')
        # skip comment
        if ln.startswith('#'):
            continue
        # store new dictionary ('>')
        if ln.startswith('>'):
            key_nm = l_preprc.replace('>', '')
            mtdt_def[key_nm] = {}
            continue
        # if lists ('++')
        if ln.startswith('++'):
            l_data = l_preprc.split(':')
            subK_nm = l_data[0].replace('++', '').replace(' ', '')
            subV_nm = l_data[1].split(',')
            mtdt_def[key_nm][subK_nm] = subV_nm
            continue
        # if value ('==')
        if ln.startswith('=='):
            l_data = l_preprc.split(':')
            subK_nm = l_data[0].replace('==', '')
            subV_nm = l_data[1].split(',')[0]
            mtdt_def[key_nm][subK_nm] = subV_nm
            continue
    return mtdt_def


def check_basic_cols_def(mtdt_def):
    '''
    assert the presence of standard definitions for metadata.
    If some is missing, returns a error mesage which can be written on a log
    file. If everything is Okay, returns True.

    Parameters
    ==========

    mtdt_def: <dct>
        a dictionary containing dictionaries
    '''
    # test for complaiance
    # check if essential, recommended and date_time_standard are provided
    try:
        assert('recommended' in mtdt_def.keys())
    except(AssertionError):
        return "category 'recomended' was not provided"
    try:
        assert('essential' in mtdt_def.keys())
    except(AssertionError):
        return "category 'essential' was not provided"

    try:
        assert('date_time_standard' in mtdt_def.keys())
    except(AssertionError):
        return "category 'date_time_standard' was not provided"

    # check if names and types were correctly provided
    try:
        assert('names' in mtdt_def['essential'].keys())
    except(AssertionError):
        return "names not provided for esssential columns"

    try:
        assert('types' in mtdt_def['essential'].keys())
    except(AssertionError):
        return "Types not provided for esssential columns"

    return True


def check_columns_compliance(colsNames_lst, typeNames_lst):
    '''
    Check if only valid types were
    '''
    VALID_TYPES = ['str', 'int', 'date', 'bool']
    try:
        assert(len(colsNames_lst) == len(typeNames_lst))
    except(AssertionError):
        nms_str = 'names (size = '+str(len(colsNames_lst)) + ')'
        type_str = ' and types (size = ' + str(len(typeNames_lst))+')'
        return nms_str + type_str+' provided are not same size'

    # check if only valid types were provided
    for item in typeNames_lst:
        if item not in VALID_TYPES:
            return item+' is not a valid type'
    return True


def check_date_frmt(string_dt):
    accptd_date_frmt = ['d', 'm', 'Y', 'H', 'M', 'S']
    print(string_dt)
    for i, char in enumerate(string_dt):
        if char == '%':
            if string_dt[i+1] not in accptd_date_frmt:
                msg = '%'+string_dt[i+1]+' is an invalid symbol for datetime'
                return msg
            continue
    return True


def check_mtdata_def_compliance(mtd_flpath):
    '''
    Check if a given sample metadata definition file obey the format
    conventions

    PARAMETERS
    ---------
    mtd_flpath: <path>
        a valid path for a .mtd file
    Returns
        True, if is everything accordingly
        str, error message if compliance test failed
    '''
    mtdt_def = load_gprm_format(mtd_flpath)
    # check if basic definitions are present
    msg_1 = check_basic_cols_def(mtdt_def)
    if msg_1 is not True:
        return msg_1

    # check if names and types were defined properly
    msg_2 = check_columns_compliance(mtdt_def['essential']['names'],
                                     mtdt_def['essential']['types'])
    if msg_2 is not True:
        return msg_2

    msg_3 = check_columns_compliance(mtdt_def['recommended']['names'],
                                     mtdt_def['recommended']['types'])
    if msg_3 is not True:
        return msg_3
    # check date and time compliance
    string_dt = mtdt_def['date_time_standard']['format']
    print(mtdt_def)
    msg_4 = check_date_frmt(string_dt)
    if msg_4 is not True:
        return msg_4
    # everuthing is okay
    return True


if __name__ == '__main__':
    # --- check metadata basic definitions ------------------------------------
    mtd_flpath = './examples/metadata.mtd'
    msg = check_mtdata_def_compliance(mtd_flpath)
    try:
        assert(msg is True)
        print("Everything is OK ;P")
    except(AssertionError):
        raise Exception(msg)
    # [TO DO] check date time string

    # ------ [TODO] check supplied 'csv' file complaince to definitions -------
