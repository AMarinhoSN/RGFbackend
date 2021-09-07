#!/bin/bash

# Redirect output stream to this file.
#PBS -o pbs_out.dat

# Redirect error stream to this file.
#PBS -e pbs_err.dat

# Send status information to this email address.
#PBS -M antonio.marinho@fiocruz.br

# Send an e-mail when the job is done.
#PBS -m e

### Number of nodes and number of processors per node
#PBS -l nodes=1:ppn=20#shared

# Change to current working directory (directory where qsub was executed)
# within PBS job (workaround for SGE option "-cwd")
cd $PBS_O_WORKDIR

#
#assure that script.sh has execution rights (chmod +x script.sh)
#>add_bash_here<
