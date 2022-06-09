from enum import Enum, auto


class Filetype(Enum):
    """Enum which shows the File-Type"""
    FASTA = auto()
    FASTAINDEX = auto()
    GTF = auto()
    BED = auto()
    BEDGRAPH = auto()
    GFF = auto()
    BAM = auto()
    WIG = auto()
    bigWIG = auto()
    TSV = auto()
    CSV = auto()
    SF = auto()
    NONE = auto()
