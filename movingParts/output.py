import os

# set source dir containing runs data
source_dir = "/storage/rgf_data/raw_data/users/IAM/"
# set file name to match
match_str = "mutations.csv"
# set output data file name
out_flnm = "mutations_set.csv"


def compileFiles(source_dir, match_str, out_flnm):
    """
    Compile the content of a files inside subdirs into a single file
    Parameters
    ----------
    source_dir:<str>
        path of the dir containing individual sequence batch files
    match_str:<str>
        name of individual files to be compiled on a single one
    out_flnm:<str>
        name of the output file containing the compiled content
    """
    # to store files in a list
    out_fl = open(source_dir + out_flnm, "w")

    # dirs=directories
    for (root, dirs, files) in os.walk(source_dir):
        for f in files:
            if f == match_str:
                first_line = True
                print(f"  > processing {root+'/'}{f}")
                in_fl = open(root + "/" + f, "r")
                for line in in_fl:
                    if first_line is True:
                        first_line = False
                        continue
                    out_fl.write(line)
