# RGFbackend

Here you will find the backend routines currently in use at Rede Genômica Fiocruz (RGF).
RGF is the COVID-19 national genomic surveillance of Fundação Oswaldo Cruz (FIOCRUZ), currently in development.

:warning: Our top priority now is to solve the specific problems of RGF.
However, our long term goal is to develop an open platform for general genomics surveillance infrastructure implementation.
Hopefully, other research and public health organization worldwide could use and/or adapt to build their solutions.

---

# How to install (quick and dirty)

```{bash}
>$ git clone https://github.com/AMarinhoSN/RGFbackend
>$ cd ./RGFbackend/
>$ pip install -e ./
```

---
# Getting started (quick and dirty)

The current implementation relies on monitoring a single directory where all data files will be submitted and on a [MongoDB server instance](https://www.mongodb.com/). This directory must have the following structure:

```
.
+-- source_dir
|   +-- users
|     +-- <user_A>
|       +-- INPUT
|         +-- <run_0X_code>
|           + --- <file1>.fastq.gz
|           + --- <file2>.fastq.gz
|     +-- <user_B>
|       + INPUT
|         +-- <run_0Y_code>
|           + --- <file1>.fastq.gz
|           + --- <file2>.fastq.gz
```
The initial metadata submitted to the database is extracted directly from directory and files names, so be carefull.

Currently there are three routines that can be activated via command line interface (CLI).
The logger routine, which will register any change on a source directory

:warning: **Temporary implementation**: in the future we plan to develop a frontend for submission of sequencing batchs processing from other genome provider institutions.
So this directory centered structure will change in the future, but for now this will get the job done.

There are three routines implemented now, **1) the logger**, **2)the submission watcher** and **3) the genome provider management**

## Start Logger
This routine monitors all changes that occurs on a given directory (dir_path) and writes it on a text file (log_flpth).
Given the centrality of the directory on our current implementation, we must keep a register of everything that is happen on the dir.
This can be handy for debugging, security issues and/or simply audit what and when something happen.

```{bash}
>$ RGF_logger <dir_path> <log_flpth>
```

## Start Submission Watcher
The Submission Watcher is our main routine, it will create documents to register and feed the database.
Currently, the routine of submit new sequencing batchs to be processed is triggered by the **creation of a 'submit.txt' file**
```{bash}
>$ RGF_sbnmWatcher <dir_path> <cred_flpath> <db_name>
```
## Genome provider management

---

## Features for Module 1 v0.1

- [ ] submit jobs to cluster queue routine
- [x] automatically register new runs on MongoDB
- [x] apps to start logger routine via CLI
- [x] apps to manage genome provider collection via CLI
- [x] apps to start submission watcher routine via CLI
- [ ] automatically register new samples on MongoDB
- [x] method to register new genome providers on MongoDB
