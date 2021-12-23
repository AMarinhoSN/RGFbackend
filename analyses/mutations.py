import pandas as pd
import numpy as np
from pandarallel import pandarallel


# Codons table
TABLE = {
    "ATA": "I",
    "ATC": "I",
    "ATT": "I",
    "ATG": "M",
    "ACA": "T",
    "ACC": "T",
    "ACG": "T",
    "ACT": "T",
    "AAC": "N",
    "AAT": "N",
    "AAA": "K",
    "AAG": "K",
    "AGC": "S",
    "AGT": "S",
    "AGA": "R",
    "AGG": "R",
    "CTA": "L",
    "CTC": "L",
    "CTG": "L",
    "CTT": "L",
    "CCA": "P",
    "CCC": "P",
    "CCG": "P",
    "CCT": "P",
    "CAC": "H",
    "CAT": "H",
    "CAA": "Q",
    "CAG": "Q",
    "CGA": "R",
    "CGC": "R",
    "CGG": "R",
    "CGT": "R",
    "GTA": "V",
    "GTC": "V",
    "GTG": "V",
    "GTT": "V",
    "GCA": "A",
    "GCC": "A",
    "GCG": "A",
    "GCT": "A",
    "GAC": "D",
    "GAT": "D",
    "GAA": "E",
    "GAG": "E",
    "GGA": "G",
    "GGC": "G",
    "GGG": "G",
    "GGT": "G",
    "TCA": "S",
    "TCC": "S",
    "TCG": "S",
    "TCT": "S",
    "TTC": "F",
    "TTT": "F",
    "TTA": "L",
    "TTG": "L",
    "TAC": "Y",
    "TAT": "Y",
    "TAA": "_",
    "TAG": "_",
    "TGC": "C",
    "TGT": "C",
    "TGA": "_",
    "TGG": "W",
}

# --- SOI GFF HANDLING --------------------------------------------------------


def translate(seq):
    """
    Translate protein sequence from a DNA coding sequence.
    """
    protein = ""
    if len(seq) % 3 == 0:
        for i in range(0, len(seq), 3):
            codon = seq[i : i + 3]
            protein += TABLE[codon]
    return protein


# -----------------------------------------------------------------------------
# --- MUTATION DATA HANDLING --------------------------------------------------


def loadUnqMuts(mut_csvpath):
    # --- LOCAL FUNCTIONS -----------------------------------------------------
    def __procMutStr(mut_str):
        """
        process mutations string data
        """
        # get first number
        for c in range(0, len(mut_str)):
            try:
                int(mut_str[c])
                s = c
                break
            except (ValueError):
                continue
        # get last number
        mut_rev = mut_str[::-1]
        for c in range(0, len(mut_str)):
            try:
                int(mut_rev[c])
                f = c * -1
                break
            except (ValueError):
                continue
        pos = int(mut_str[s:f])
        orig = mut_str[0:s]
        mut = mut_str[f : len(mut_str)]
        return orig, pos, mut

    # load mutation csv * mutations data using viralflow standard
    samples_mut_df = pd.read_csv(mut_csvpath)
    # get unique mutations observed
    unique_muts = samples_mut_df["mut"].value_counts()

    # remove strange mutations labels
    dct_lst = []
    for m in unique_muts.index:
        # get number position
        orig, pos, mut = __procMutStr(m)
        freq = unique_muts[m]
        if len(mut) > 1:
            print(f"skipped {mut} | {m}")
            continue
        dct = {"orig": orig, "pos": pos, "mut": mut, "freq": freq}
        dct_lst.append(dct)

    # load unique mutations dataframe
    unq_muts_df = pd.DataFrame(dct_lst)

    # get samples mutations signatures
    unq_lbls = samples_mut_df["cod"].unique()
    dct_lst = []
    for lbl in unq_lbls:
        lbl_slice = samples_mut_df.loc[samples_mut_df["cod"] == lbl]
        mut_set = lbl_slice["mut"].values
        # get arrays of origs, positions and mutations
        origs_lst = []
        pos_lst = []
        mut_lst = []
        for m in mut_set:
            orig, pos, mut = __procMutStr(m)
            origs_lst.append(orig)
            pos_lst.append(pos)
            mut_lst.append(mut)
        dct = {
            "cod": lbl,
            "pos_x": pos_lst,
            "mut_y": mut_lst,
            "orig_z": origs_lst,
            "mut_set": mut_set,
        }
        dct_lst.append(dct)

    # mount sample mutation signatures dataframes
    samples_mutsgn_df = pd.DataFrame(dct_lst)

    return unq_muts_df, unique_muts, samples_mutsgn_df


# --- Unique mutations


def computeUnqGeneMutDF(soi_gff, unique_muts, skip_lbl):
    """
    Get unique mutations affecting genes only.
    """

    def isOnAGene(row, genes_df, skip_lbl=[]):
        """check if is inside a CDS region"""
        for gene_i in genes_df[["Start", "End", "gene"]].values:
            if (row["pos"] >= gene_i[0]) and (row["pos"] <= gene_i[1]):
                if gene_i[2] in skip_lbl:
                    continue
                else:
                    return gene_i[2]

    genes_df = soi_gff.loc[
        soi_gff["gene_biotype"] == "protein_coding"
    ]  # [['Start', 'End','product','gene', 'protein_id', 'translated']]
    unique_muts["gene"] = unique_muts.apply(
        isOnAGene, genes_df=genes_df, skip_lbl=skip_lbl, axis=1
    )
    unqGeneMut = unique_muts.loc[unique_muts["gene"].dropna().index]
    return unqGeneMut


# --- filter sample mutations df ----------------------------------------------
# get bases changes information
def filterGeneMutsPos(row, unq_muts_df):
    """
    filter positions to get only gene mutations
    """
    return [i for i in row["pos_x"] if i in unq_muts_df["pos"].values]


def getBaseCols(row, col_nm):
    """
    get base information from a gene position only
    """
    # sanity assurance (let's be sure we have a sorted list of number)
    gmutpos_lst = np.sort(row["gene_pos"])
    # get limits to check
    min_gmutpos = gmutpos_lst[0]
    max_gmutpos = gmutpos_lst[-1]
    # get position indexes
    sel_idx = []
    for i, pos_i in enumerate(row["pos_x"]):
        # skip off values
        if (pos_i < min_gmutpos) or (pos_i > max_gmutpos):
            continue
        # get index of selected position and recover base information
        if pos_i in gmutpos_lst:
            sel_idx.append(i)

    return [row[col_nm][i] for i in sel_idx]


# Get codons, translate for mutations and store on a list
def getMutGeneNames(row, soi_gff, skip_genes):
    """
    get gene names for a given set of positions based on gff definitions
    """
    # load reference genes array
    genes_gff = soi_gff.loc[soi_gff["product"].dropna().index]
    genes_arr = genes_gff[["Start", "End", "product"]].values

    # catalog gene names
    mut_genes = []
    for i in row["gene_pos"]:
        curr_gene = None
        for g in genes_arr:
            if g[2] in skip_genes:
                continue
            if (i >= g[0]) and (i <= g[1]):
                curr_gene = g[2]
                break
        mut_genes.append(curr_gene)
    return mut_genes


def getGeneMutInfo(samples_mutsgn_df, soi_gff, unq_muts_df, skip_lbl=["ORF1ab"]):
    """ """
    # get unique gene mutations observed
    gene_unq_muts_df = computeUnqGeneMutDF(soi_gff, unq_muts_df, skip_lbl=skip_lbl)

    # add gene mutations to samples mutation dataframe
    samples_mutsgn_df["gene_pos"] = samples_mutsgn_df.apply(
        filterGeneMutsPos, unq_muts_df=gene_unq_muts_df, axis=1
    )
    samples_mutsgn_df["gene_orig"] = samples_mutsgn_df.apply(
        getBaseCols, col_nm="orig_z", axis=1
    )
    samples_mutsgn_df["gene_mut"] = samples_mutsgn_df.apply(
        getBaseCols, col_nm="mut_y", axis=1
    )
    samples_mutsgn_df["gene_mut_set"] = samples_mutsgn_df.apply(
        getBaseCols, col_nm="mut_set", axis=1
    )
    samples_mutsgn_df["gene_names"] = samples_mutsgn_df.apply(
        getMutGeneNames, soi_gff=soi_gff, skip_genes=skip_lbl, axis=1
    )

    return samples_mutsgn_df


# --- AA handling -------------------------------------------------------------
def get_codon_pos(pos, s_gene):
    """
    Compute codon position for a given nucleotide number, given the start position
    of a given gene.
    """
    # sanity check
    # get aa position number and codong
    interval = pos - s_gene
    codon_number = interval / 3

    if interval % 3 == 0:
        return codon_number + 1, pos

    else:
        # check if which codon starts before pos
        for i in [1, 2]:
            # print(f'checking {pos-i}')
            n_pos = pos - i
            interval = n_pos - s_gene
            codon_number = interval / 3
            if interval % 3 == 0:
                return codon_number + 1, n_pos


def getProteinMutations(row, ref_seq, gene_only_df, skip_genes):
    """
    get aminoacid changes from nucleotide mutations
    """
    # set list to store results
    aa_orig_lst = []
    aa_pos_lst = []
    aa_mut_lst = []
    # for each mutation on the given row
    for i, pos_i in enumerate(row["gene_pos"]):
        orig_i = row["gene_orig"][i]
        mut_i = row["gene_mut"][i]

        # check to which gene the mutation belongs
        for j, g_j in enumerate(gene_only_df[["Start", "End", "gene"]].values):
            # skip selected gene labels
            if g_j[2] in skip_genes:
                continue
            # if on a given gene interval
            if (pos_i >= g_j[0]) and (pos_i <= g_j[1]):
                # get residue number, base of codon start
                aa_pos, codon_start = get_codon_pos(pos_i, g_j[0])

                # compute position of the base on the condon
                mut_idx = pos_i - codon_start

                # get codon of reference sequence
                ref_codon = ref_seq[codon_start - 1 : codon_start + 2]

                # sanity check -----------------------------------------
                # Be sure that the identified base is the one expected
                assert orig_i == ref_seq[pos_i - 1]
                # ------------------------------------------------------

                # get mutated codon
                str_lst = list(ref_codon)
                str_lst[mut_idx] = mut_i
                mut_codon = "".join(str_lst)

                # get aminoacids
                orig_aa = TABLE[ref_codon]
                new_aa = TABLE[mut_codon]

                # store aa information
                # print(f"  > {orig_aa}{int(aa_pos)}{new_aa}")
                aa_orig_lst.append(orig_aa)
                aa_pos_lst.append(int(aa_pos))
                aa_mut_lst.append(new_aa)
                break
    return aa_orig_lst, aa_pos_lst, aa_mut_lst


def getAAMutInfo(samples_mutsgn_df, ref_seq, skip_genes, soi_gff):
    """
    add aminoacid mutations information on dataframes
    """

    def getAAMutStrings(row):
        mut_set = []
        for i, pos_i in enumerate(row["aa_pos"]):
            mut_set.append(
                f"{row['aa_orig'][i]}{int(row['aa_pos'][i])}{row['aa_mut'][i]}"
            )
        return mut_set

    # get gene reference datafrane
    gene_only_df = soi_gff.loc[soi_gff["product"].dropna().index]
    # get codon/aa number positions
    t = samples_mutsgn_df.apply(
        getProteinMutations,
        ref_seq=ref_seq,
        gene_only_df=gene_only_df,
        skip_genes=skip_genes,
        axis=1,
    )
    o_col = []
    p_col = []
    m_col = []

    for i in t:
        o_col.append(i[0])
        p_col.append(i[1])
        m_col.append(i[2])

    samples_mutsgn_df["aa_orig"] = o_col
    samples_mutsgn_df["aa_pos"] = p_col
    samples_mutsgn_df["aa_mut"] = m_col
    # add aa mutations labels
    samples_mutsgn_df["aa_mut_labels"] = samples_mutsgn_df.apply(
        getAAMutStrings, axis=1
    )

    return samples_mutsgn_df


# --- gene codes dictionary ---------------------------------------------------
# get gene labels code
def getGeneCodes(samples_mutsgn_df, csv_out_path):
    # get number os samples
    N_samples = len(samples_mutsgn_df[["gene_names"]])  # .values[0]

    # store all values on a single list and get unique values
    gene_names_lst = []
    for i in range(0, N_samples):
        for j in samples_mutsgn_df[["gene_names"]].values[i]:
            for z in j:
                gene_names_lst.append(z)
    unq_genes_observed = np.unique(gene_names_lst)

    # write csv and return a dictionary
    out_csv = open(csv_out_path, "w")
    out_csv.write("code, gene_name\n")
    dct = {}
    for i, v_i in enumerate(unq_genes_observed):
        dct[v_i] = i
        out_csv.write(f"{i},{v_i}\n")

    return dct


def getCodedLabels(row, gene_codes_dct):
    assert len(row["aa_mut_labels"]) == len(row["gene_names"])
    N_muts = len(row["gene_names"])
    new_labels = []
    for i in range(0, N_muts):
        cod_i = row["gene_names"][i]
        mut_i = row["aa_mut_labels"][i]
        new_mutlbl = str(gene_codes_dct[cod_i]) + ":" + mut_i
        new_labels.append(new_mutlbl)
    return new_labels


# get unique mutations observed and frequencies
def getUnqMutsObserved(samples_mutsgn_df, csv_out_path):
    # get number of samples
    N_samples = len(samples_mutsgn_df[["coded_mut_labels"]])

    # store all values on a single list and get unique values
    mut_names_lst = []
    for i in range(0, N_samples):
        for j in samples_mutsgn_df[["coded_mut_labels"]].values[i]:
            for z in j:
                mut_names_lst.append(z)
    total_muts = len(mut_names_lst)
    # get unique mutations and frequencies, write data on a csv
    unq_muts, unq_muts_freqs = np.unique(mut_names_lst, return_counts=True)
    out_csv = open(csv_out_path, "w")
    out_csv.write("coded_mut,freq,prob\n")
    mut_freq_dct = {}
    for i, v_i in enumerate(unq_muts):
        n_i = unq_muts_freqs[i]
        p_i = n_i / total_muts
        mut_freq_dct[v_i] = [n_i, p_i]
        out_csv.write(f"{v_i},{n_i},{p_i}\n")

    return mut_freq_dct


def getVectors(row, unq_mut_dct):
    vec = []
    for k in unq_mut_dct.keys():
        if k in row["coded_mut_labels"]:
            vec.append(1)

        if k not in row["coded_mut_labels"]:
            vec.append(0)
    return vec


# --- CLASS -------------------------------------------------------------------


class MutationSet:
    """
    Class to handle a given set of mutations
    """

    def __init__(self, set_name, samples_mut_csv):
        """ """
        self.name = set_name
        self.sample_mut_path = samples_mut_csv

    def loadUniqueMutations(self):
        unq_muts_df, unq_muts_counts, samples_mutsgn_df = loadUnqMuts(
            self.sample_mut_path
        )
        # unique mutations dataframe
        self.unq_muts_df = unq_muts_df
        self.unq_muts_counts = unq_muts_counts
        self.samples_mutsgn_df = samples_mutsgn_df

    def getOnlyGeneMut(self, soi_gff, skip_lbl=[], ncpus=1):
        """
        load rows to samples_mut_df containing only mutations affecting genes
        """
        pandarallel.initialize(nb_workers=ncpus, progress_bar=True)

        # load only mutaions affecting genes
        self.unq_gene_mut_df = computeUnqGeneMutDF(
            soi_gff, self.unique_muts_counts, skip_lbl=skip_lbl
        )

        # add gene mutations to samples mutation dataframe
        self.samples_mutsgn_df["gene_pos"] = self.samples_mutsgn_df.parallel_apply(
            filterGeneMutsPos, unq_muts_df=self.unq_gene_muts_df, axis=1
        )
        self.samples_mutsgn_df["gene_orig"] = self.samples_mutsgn_df.parallel_apply(
            getBaseCols, col_nm="orig_z", axis=1
        )
        self.samples_mutsgn_df["gene_mut"] = self.samples_mutsgn_df.parallel_apply(
            getBaseCols, col_nm="mut_y", axis=1
        )
        self.samples_mutsgn_df["gene_mut_set"] = self.samples_mutsgn_df.parallel_apply(
            getBaseCols, col_nm="mut_set", axis=1
        )
        self.samples_mutsgn_df["gene_names"] = self.samples_mutsgn_df.parallel_apply(
            getMutGeneNames, soi_gff=soi_gff, skip_genes=skip_lbl, axis=1
        )

    def getAAMut(self, ref_seq, soi_gff, skip_genes=[]):
        """
        Load aminoacid mutation data
        """
        self.samples_mutsgn_df = getAAMutInfo(
            self.samples_mutsgn_df, ref_seq, skip_genes, soi_gff
        )

    def generateGeneCodes(self, csv_out_path):
        """ """
        gene_codes_dct = getGeneCodes(self.samples_mutsgn_df, csv_out_path)
        self.gene_codes_df = pd.DataFrame(gene_codes_dct)
        # add coded mutation labels
        self.samples_mutsgn_df["coded_mut_labels"] = self.samples_mutsgn_df.apply(
            getCodedLabels, gene_codes_dct=gene_codes_dct, axis=1
        )

    def loadUniqueAAMut(self, csv_out_path):
        self.AAmut_freq_dct = getUnqMutsObserved(self.samples_mutsgn_df, csv_out_path)

    def loadMutationsVectors(self):
        self.samples_mutsgn_df["mut_vec"] = self.samples_mutsgn_df.apply(
            getVectors, unq_mut_dct=self.AAmut_freq_dct, axis=1
        )

    # TODO : Variant naming
    def compareSamples2Var(self):
        """ """
        pass
