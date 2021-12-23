from setuptools import setup

setup(
    name="RGFbackend",
    version="0.0.5",
    description="""
    A python package designed to handle backend routine of Rede Genomica Fiocruz
    """,
    url="http://github.com/AMarinhoSN/RGFbackend",
    author="Antonio Marinho da Silva Neto",
    author_email="antonio.marinho@fiocruz.br",
    packages=["dbInterface", "watchers", "movingParts"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    scripts=[
        "scripts/RGFManageGnmPrvdr",
        "scripts/RGF_logger",
        "scripts/RGF_sbmtWatcher",
        "scripts/RGF_output",
    ],
    install_requires=["pymongo", "watchdog", "gff3_parser", "numpy", "pandas"],
    zip_safe=False,
)
