import analyses.toolbox as toolbox
import pandas as pd


class soi:
    """
    Class to handle System Of Insterest general information

    Usage
    -----
    my_soi = soi(name, gff_path, refseq_fasta)

    Parameters
    ----------
    name:<str>
        name of the system of interest
    gff_path:<path>
        GFF file path containing genome sections information
    refseq_fasta:<path>
        reference sequence fasta file path
    """

    def __init__(self, name, gff_path, refseq_fasta):
        self.name = name
        self.gff_path = gff_path
        self.ref_fasta = refseq_fasta

        # load reference sequence data
        ref_gnm_dct = toolbox.parse_fasta(refseq_fasta)
        self.ref_seq = ref_gnm_dct[0]["seq"]
        self.gnm_len = ref_gnm_dct[0]["seq_len"]
        # load gff data
        self.gff_df = toolbox.loadSOIGff(
            gff_path, load_CDStranslated=True, ref_seq=self.ref_seq
        )


class variants:
    """ """

    def __init__(self, name, mutsig_csv):
        """ """
        self.name = name
        self.mutsig_csv = mutsig_csv
        # load variants signature
        self.mutsig_df = pd.read_csv(mutsig_csv, sep="\t")
