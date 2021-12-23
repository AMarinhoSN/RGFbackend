import analyses.mutations as mutations
import gff3_parser
from sys import exit


def parse_fasta(fasta_path):
    """
    load fasta file
    """
    # download from NCBI remember to download with GI information

    fst_fl = open(fasta_path, "r")
    dct_lst = []
    curr_seq = None
    curr_dct = {}
    # get number of lines
    # n_lines = sum([1 for l in fst_fl])
    # parse fasta file
    n = 0
    for l in fst_fl:
        n += 1
        # new sequence
        if l.startswith(">"):
            # store curr seq if not empty
            if curr_seq != None:
                curr_dct["seq"] = curr_seq
                curr_dct["seq_len"] = len(curr_seq)
                dct_lst.append(curr_dct)

            # reset for new sequence
            curr_seq = ""

            # process GI data
            l_dt = l.split("|")
            gi = l_dt[1]
            product_nm = l_dt[-1].split("[")[0][1:-1]
            protein_id = l_dt[3]

            # start new dct
            curr_dct = {"gi": gi, "product": product_nm, "protein_id": protein_id}
            continue
        else:
            curr_seq += l.replace("\n", "")

    # do not lost the last sequence
    curr_dct["seq"] = curr_seq
    curr_dct["seq_len"] = len(curr_seq)
    dct_lst.append(curr_dct)

    return dct_lst


def loadSOIGff(gff_flpath, load_CDStranslated=False, ref_seq=None):
    """
    load System Of Interest GFF data.
    """
    # --- LOCAL FUNCTIONS -----------------------------------------------------
    def __intify(row):
        return int(row)

    # get translated sequences for every CDS
    def getTranslated(row, ref_seq):
        if "CDS" in row["Type"]:
            gnm_slice = ref_seq[row["Start"] - 1 : row["End"]]
            return mutations.translate(gnm_slice)
        else:
            return None

    soi_gff = gff3_parser.parse_gff3(gff_flpath, verbose=True, parse_attributes=True)

    soi_gff["Start"] = soi_gff["Start"].apply(__intify)
    soi_gff["End"] = soi_gff["End"].apply(__intify)

    if load_CDStranslated is True:
        try:
            assert ref_seq != None
        except (AssertionError):
            m = "ERROR: no genome reference sequence fasta file was provided"
            print(m)
            exit(1)
        # get protein sequences
        soi_gff["translated"] = soi_gff.apply(getTranslated, ref_seq=ref_seq, axis=1)

    return soi_gff


def binarySearch(lst, v):
    """
    Find the index of a given number on a list of numbers, using the binary search
    algorithm
    """
    pointer_max = len(lst)
    pointer_min = 0
    pointer_mid = 0

    while pointer_min <= pointer_max:
        # get mid point between min and max
        pointer_mid = (pointer_max + pointer_min) // 2

        # if value bigger than mid, increase low to be bigger than current mid
        if lst[pointer_mid] < v:
            pointer_min = pointer_mid + 1

        # if values is lesser than mid, decrease max to be smaller than current mid
        if lst[pointer_mid] > v:
            pointer_max = pointer_mid - 1

        # if equal, than is done
        if lst[pointer_mid] == v:
            return pointer_mid
    return -1
