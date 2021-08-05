#!/bin/bash
#Written by: Filipe Dezordi (https://dezordi.github.io/)
#At FioCruz/IAM - 12 Mai. 2021

file_list="$1"
while read files;do
	reference=$(echo $files | awk -F":" '{print $1}')
	fastq1=$(echo $files | awk -F":" '{print $2}')
	fastq2=$(echo $files | awk -F":" '{print $3}')
	prefix=$(echo $files | awk -F":" '{print $4}')
	threads=$(echo $files | awk -F":" '{print $5}')
	depth=$(echo $files | awk -F":" '{print $6}')
	min_len=$(echo $files | awk -F":" '{print $7}')
        adapters=$(echo $files | awk -F":" '{print $8}')
	image=$(echo $files | awk -F":" '{print $9}')
	singularity run --env REFERENCE=$reference --env FASTQ1=$fastq1 --env FASTQ2=$fastq2 --env PREFIXOUT=$prefix --env THREADS=$threads --env DEPTH=$depth --env MIN_LEN=$min_len --env ADAPTERS=$adapters --writable $image
done < $file_list
