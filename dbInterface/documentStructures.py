'''
FUNCTIONS TO ENSURE MINIMAL DOCUMENT STRUCTURES ARE DEFINED HERE.
'''

# ======== GLOBAL VARIABLES ====================================================
# Here the required keys for all the documents are defined.
# PS: Currently, an example of the type expected is included as a dictionary,
# just to allow to use the built in function type(). Probably there is a better
# way to do that and this routine should be updated.

# Genome provders doc keys
GEN_PRVDR_KEYS = {'code':'str','full_name':'str','address':'str','city':'str',
                  'state':'str','country':'str','zip_code':'str',
                  'main_contact_name':'str','main_contact_email':'str'}
# sequencing run batch
SEQ_BATCH_KEYS = {'run_code': 'str', 'gprvdr_code': 'str','full_path': 'str',
                'routine':'str', 'reads_lenght':1, 'submition_date':'str',
                'files_at_dir':['a','b','c']}

# genome data

# ======== FUNCTIONS ===========================================================
# ---------- GENERAL FUNCTIONS ---------------------------------------
def listMissingKeys(dct, reference_keys):
    '''
    check if dictionary keys expected for genome providers documentes are
    present and return a list of missing keys
    '''
    def checkKey(dct, key):
        '''check if keys are present on a given dictionary'''
        if key in dct.keys():
            return True
        else:
            return False

    # compile list of missing keys and return it
    missing_keys = []
    for key in reference_keys:
        if checkKey(dct, key) == False:
            missing_keys.append(key)
    return missing_keys

def listIncorrectValTypes(dct, reference_kvtypes):
    ''' Check value types compliance and return a list of missing values'''
    failed_types_lst = []
    for key in reference_kvtypes.keys():
        if type(dct[key]) == type(reference_kvtypes[key]):
            continue
        if type(dct[key]) != type(reference_kvtypes[key]):
            failed_types_lst.append({key:dct[key]})
    return failed_types_lst

# ---------- DOCUMENT SPECIFIC FUNCTIONS ---------------------------------------
# --- Genome Providers
def assertGenPrvdrKeysCompliance(dct):
    ''' Assert genome providers document compliance to key structure'''
    # check for missing keys
    missing_keys = listMissingKeys(dct, GEN_PRVDR_KEYS)
    if len(missing_keys) == 0:
        return True
    if len(missing_keys) > 0:
        return False, missing_keys

def assertGenPrvdrTypeCompliance(dct):
    ''' Assert genome provider document key value types compliance'''
    failed_types_lst = listIncorrectValTypes(dct, GEN_PRVDR_KEYS)
    if len(failed_types_lst) == 0:
        return True
    if len(failed_types_lst) > 0:
        return False, failed_types_lst

# --- Sequencing Run Batchs
def assertSeqBatchKeysCompliance(seq_dct):
    ''' Assert genome providers document compliance to key structure'''
    # check for missing keys
    missing_keys = listMissingKeys(seq_dct, SEQ_BATCH_KEYS)
    if len(missing_keys) == 0:
        return True
    if len(missing_keys) > 0:
        return False, missing_keys

def assertSeqBatchTypeCompliance(seq_dct):
    '''
    Assert genome provider document key value types compliance

    Parameters
    ----------
    seq_dct : dct
        dictionary providing sequencing batch document content

    Returns
    -------
    bool
    '''
    failed_types_lst = listIncorrectValTypes(seq_dct, SEQ_BATCH_KEYS)
    if len(failed_types_lst) == 0:
        return True
    if len(failed_types_lst) > 0:
        return False, failed_types_lst


if __name__=='__main__':
    # TODO TEST -----------------------------------------------------------
    # If running the file, unit tests will be done [PROVISIONAL]
    # proper testing routines should be written in the future
    def test_compliance(comp_key_func, comp_type_func, dct_in):
        try:
            assert(comp_key_func(dct_in) == True)
            print(' > Assertion keys compliance : PASS')
        except(AssertionError):
            print(' > Assertion keys compliance : FAILED!')

        try:
            assert(comp_type_func(dct_in) == True)
            print(' > Assertion types compliance test: PASS')
        except(AssertionError):
            print(' > Assertion types compliance : FAILED!')



    print('@ testing Genome Provider Compliance functions')

    correct_provider = {'code':'IAM',
                    'full_name': 'Instituto de Pesquisa Aggeu Magalhães',
                    'address':'rua numero', 'city':'Recife', 'state':'PE',
                    'country':'Brazil', 'zip_code':'5555-555',
                    'main_contact_name':'Fulana da Silva',
                    'main_contact_email':'f.dasilva@fiocruz.br'}

    test_compliance(assertGenPrvdrKeysCompliance,
                    assertGenPrvdrTypeCompliance,
                    correct_provider)

    print('@ testing Sequence Batch Compliance functions')
    # sequencing run batch

    correct_seqbatch  = {'run_code':'IAM201', 'gprvdr_code':'IAM',
                        'full_path':'/source/dir/IAM/INPUT/IAM201',
                        'routine':'standard', 'reads_lenght':150,
                        'submition_date':'05/08/2021 12:51:56'}

    test_compliance(assertSeqBatchKeysCompliance,
                    assertSeqBatchTypeCompliance,
                    correct_seqbatch)

    # TODO [add] False result tests
