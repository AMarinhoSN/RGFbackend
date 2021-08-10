from pymongo import MongoClient, errors

#
import dbInterface.documentStructures as docstr

# ==== FUNCTIONS ===============================================================


def read_keyval_file(cred_flpath):
    '''
    Read key values text file
    '''
    f = open(cred_flpath, 'r')
    dct = {}
    for line in f:
        data = line.split('=')
        if len(data) == 2:
            key = data[0].replace(' ', '')
            value = data[1].replace(' ', '').replace('\n', '')
            dct[key] = value
        # if line cannot be splited into two substrings using '=', ignore it
        if len(data) == 1:
            continue
        if len(data) > 2:
            raise Exception("More than one '=' symbol at keyvalue line")
    return dct

# ------------------------------------------------------------------------------

#cred_flpath='/HDD/Projects/module_2_dev/tutorials/mongo_sing/mongo_credentials'


class DataBase:
    '''
    class designed to handle routine of mongo database operations
    '''

    def __init__(self, cred_flpath, database_name, timeout_upto=2000):
        '''
        create a mondoDB class object.

        A text file with mongodb access credentials is needed to access the
        running mongod. This is just a wrapper for the MongoClient of Pymongo,
        all lines will be converted to keyword arguments and be used as input
        for MongoClient.

        Parameters
        ----------
        cred_flpath : path
            Path for credentials file
        database_name : str
            Name of the database to be used/created.
        timeout_upto: int
            Max time to wait for server connection in ms (default = 2000)

        Returns
        -------
        mongoDB class object

        '''
        # TODO add sanity test for mongo db instance existence
        self.database_name = database_name
        self.cred_flpath = cred_flpath
        # load credentials file
        kwargs = read_keyval_file(cred_flpath)
        try:
            self.client = MongoClient(**kwargs,
                                    serverSelectionTimeoutMS = timeout_upto)
            # check if server is valid
            self.client.server_info()
        except(errors.ServerSelectionTimeoutError):
            print("ERROR: Connection timeout (waited for ",timeout_upto, ' ms)')
            print("       Either your server is not up or you have a slow ")
            print("       connection (if so, try to increase max timeout).")
            raise Exception(" Connection timeout error.")

        #try:
        #except:
        #    print("ERROR: invalid database server. Check if the server is up")
        #    print("       and/or the credentials are valid")
        #    exit()
        # create database
        self.DB = self.client[self.database_name]
        # create collections for genome providers
        self.gnmPrvdrsCol = self.DB['genomeProviders']
        # create collections genome samples data
        self.gnmDataCol = self.DB['genomeData']
        # create collections sequencing run batchs
        self.seqBatchsCol = self.DB['seqBatchs']
        # WARNING: collections and databases are created only after adding an
        # actual document

    # ===| INSERT DOCUMENT METHODS |============================================

    def insert_new_gnmProvider(self, new_provider_flpth):
        '''insert a genome provider new document on a given collection'''

        # --- | load text file | -----------------------------------------------
        new_provider_dct = read_keyval_file(new_provider_flpth)
        #  --- | assert document structure compliance | ------------------------
        # check keys
        try:
            assert(docstr.assertGenPrvdrKeysCompliance(new_provider_dct))
        except(AssertionError):
            missing_keys = docstr.assertGenPrvdrKeysCompliance(
                new_provider_dct)
            print('ERROR: The following keys are missing...')
            for k in missing_keys:
                print('       ', k)
            raise Exception('Missing keys for Genome Provider doc')

        # check values types
        try:
            assert(docstr.assertGenPrvdrTypeCompliance(new_provider_dct))
        except(AssertionError):
            failed_types = docstr.assertGenPrvdrTypeCompliance(
                new_provider_dct)
            print('ERROR: The following values have the wrong type...')
            for k in failed_types:
                print('       ', k)
            raise Exception('Wrong value format for Genome Provider doc')

        # --- | add new document | ---------------------------------------------
        # add document to genome provider
        self.gnmPrvdrsCol.insert_one(new_provider_dct)

    # TODO

    def insert_new_seqBatch(self, new_seq_batch_dct):
        #  --- | assert document structure compliance | ------------------------
        # check keys
        try:
            assert(docstr.assertSeqBatchKeysCompliance(new_seq_batch_dct))
        except(AssertionError):
            missing_keys = docstr.assertSeqBatchKeysCompliance(
                new_seq_batch_dct)
            print('ERROR: The following keys are missing...')
            for k in missing_keys:
                print('       ', k)
            raise Exception('Missing keys for Genome Provider doc')

        # check values types
        try:
            assert(docstr.assertSeqBatchTypeCompliance(new_seq_batch_dct))
        except(AssertionError):
            failed_types = docstr.assertGenPrvdrTypeCompliance(
                new_seq_batch_dct)
            print('ERROR: The following values have the wrong type...')
            for k in failed_types:
                print('       ', k)
            raise Exception('Wrong value format for Genome Provider doc')

        # --- | add new document | ---------------------------------------------
        # add document to sequencing Batchs collection
        self.seqBatchsCol.insert_one(new_seq_batch_dct)

    # TODO
    def insert_new_gnmSample(self):
        pass

    # ===| QUERY DOCUMENT METHODS |============================================
