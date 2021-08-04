'''
FUNCTIONS TO ENSURE MINIMAL DOCUMENT STRUCTURES ARE DEFINED HERE.
'''

# ======== GLOBAL VARIABLES ====================================================
GEN_PRVDR_KEYS = {'code':'str','full_name':'str','address':'str','city':'str',
                  'state':'str','country':'str','zip_code':'str',
                  'main_contact_name':'str','main_contact_email':'str'}

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
    print(reference_keys)
    for key in reference_keys:
        print(key)
        if checkKey(dct, key) == False:
            missing_keys.append(key)
    return missing_keys

def listIncorrectValTypes(dct, reference_kvtypes):
    ''' Check value types compliance and return a list of missing values'''
    failed_types_lst = []
    for key in dct.keys():
        if type(dct[key]) == type(reference_kvtypes[key]):
            continue
        if type(dct[key]) != type(reference_kvtypes[key]):
            failed_types_lst.append({key:dct[key]})
    return failed_types_lst

# ---------- DOCUMENT SPECIFIC FUNCTIONS ---------------------------------------
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

if __name__=='__main__':
    # TODO TEST -----------------------------------------------------------
    # If running the file, unit tests will be done [PROVISIONAL]
    # proper testing routines should be written in the future
    print('@ testing Genome Provider Compliance functions')

    correct_provider = {'code':'IAM',
                    'full_name': 'Instituto de Pesquisa Aggeu Magalhães',
                    'address':'rua numero', 'city':'Recife', 'state':'PE',
                    'country':'Brazil', 'zip_code':'5555-555',
                    'main_contact_name':'Fulana da Silva',
                    'main_contact_email':'f.dasilva@fiocruz.br'}
    try:
        assert(assertGenPrvdrKeysCompliance(correct_provider) == True)
        print(' > Assertion keys compliance : PASS')
    except(AssertionError):
        print(' > Assertion keys compliance : FAILED!')

    try:
        assert(assertGenPrvdrTypeCompliance(correct_provider) == True)
        print(' > Assertion types compliance test: PASS')
    except(AssertionError):
        print(' > Assertion types compliance : FAILED!')

    # TODO [add] False result tests
