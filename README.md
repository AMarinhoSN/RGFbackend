# RGFbackend

Here you will find the backend routines currently in use for Rede Genômica Fiocruz (RGF).
RGF is the COVID-19 national genomic surveillance of Fundação Oswaldo Cruz (FIOCRUZ), currently in development.

---

Our top priority now is to solve the specific problems of RGF. However, our long term goal is to develop an open platform for general genomic surveillance infrastructure implementation.
Hopefully, other research and public health organization worldwide could use and/or adapt to build their solutions.
# How to install (quick and dirty)

```{bash}
>$ git clone https://github.com/AMarinhoSN/RGFbackend
>$ cd ./RGFbackend/
>$ pip install -e ./
```


## Features for Module 1 v0.1

- [ ] submit jobs to cluster queue routine
- [x] automatically register new runs on MongoDB
- [ ] automatically register new samples on MongoDB
- [x] method to register new genome providers on MongoDB
