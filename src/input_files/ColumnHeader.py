from enum import Enum


class Header(Enum):
    """Enum for Column Header in files"""
    GENE_ID = 'gene_id'
    CHROM = 'Chrom'
    START = 'Start'
    STOP = 'Stop'
    TRANSCRIPT_ID = 'transcript_id'
    SAMPLE = 'Sample'
    SAMPLE2 = 'Sample2'
    TPM = 'TPM'
    REPLICATE = 'replicate'
    QUANT_FILE = 'quant_file'
    NUM_READS = 'NumReads'
    NAME = 'Name'
    LENGTH = 'Length'
    EFFECTIVE_LENGTH = 'EffectiveLength'
    ENSEMBL_GENE_ID = 'ensembl_gene_id'
    DESCRIPTION = 'description'
    EXTERNAL_GENE_NAME = 'external_gene_name'
    GENE_BIOTYPE = 'gene_biotype'
    INDEX = 'index'
    NONE = None
