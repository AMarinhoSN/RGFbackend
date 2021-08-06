from setuptools import setup

setup(name='RGFbackend',
    version='0.0.1',
    description='''
    A python package designed to handle backend routine of Rede Genomica Fiocruz
    ''',
    url='http://github.com/AMarinhoSN/RGFbackend',
    author='Antonio Marinho da Silva Neto',
    author_email='antonio.marinho@fiocruz.br',
    packages=['dbInterface', 'watchers'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ],
    scripts=['bin/RGFManageGnmPrvdr', 'bin/RGF_logger'],
    install_requires=['pymongo', 'watchdog'],
    zip_safe=False)
