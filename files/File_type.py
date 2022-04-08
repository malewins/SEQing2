from enum import Enum, auto


class Filetype(Enum):
    """Enum which shows the possible File-Type"""
    FASTA = auto()
    GTF = auto()
    BED = auto()
    BEDGRAPH = auto()
    GFF = auto()
    BAM = auto()
    WIG = auto()
    bigWIG = auto()
    TSV = auto()
    CSV = auto()
    NONE = auto()
