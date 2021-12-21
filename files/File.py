#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Bio import SeqIO
from pyBedGraph import BedGraph
from pybedtools import BedTool
from files.File_type import Filetype


class FileInput:
    """Decorator for file checking
    @:param file Path
    @:param file Type (gtf,bed,fa,bedgraph)
    @:param file is zipped or not(True or False)
    @:param type of zip if zipped(gz)
    @:param header is present (True or False)"""

    def __init__(self, file_name, file_path, file_type, zipped, zip_type, header_present, server_path):
        # zip_type could be removed, also zipped and header_present
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.zipped = zipped
        self.zip_type = zip_type
        self.header_present = header_present
        self.server_path = server_path

    def get_dict(self):
        """Method returns a dictionary of the file
        @:return dict"""
        if self.file_type == Filetype.FASTA:
            return [{'value': rec.id, 'label': rec.name} for rec in SeqIO.parse(self.file_path, "fasta")]
        if self.file_type == Filetype.BEDGRAPH:
            bed_graph = BedGraph('samples/example.sizes', self.file_path, ignore_missing_bp=False)
            return bed_graph.load_chrom_data('Chr1')
        if self.file_type == Filetype.BED:  # BED6
            return [{'value': rec[3], 'label': rec[0] + " : " + rec[3]} for rec in BedTool(self.file_path)]
        if self.file_type == Filetype.GTF:
            return [{'value': rec[8], 'label': rec[0] + ":" + rec[8]} for rec in BedTool(self.file_path)]
        # TODO: Return a dictionary of GTF, BED12, BEDGRAPH, GFF

    def get_general_dict(self):
        return dict(name="Read " + str(self.file_type),
                    url=self.server_path,
                    nameField='gene',
                    # indexed='false',
                    color='rgb(191, 188, 6)')

    def get_locus(self, genome):
        if self.file_type == Filetype.BED:  # BED6
            for rec in BedTool(self.file_path):
                if rec[3] == genome:
                    return [rec[0] + ":" + rec[1] + "-" + rec[2]]
        if self.file_type == Filetype.GTF:  # Check how long the entry is over the rows
            for rec in BedTool(self.file_path):
                if rec[8] == genome:
                    return [rec[0] + ":" + rec[3] + "-" + rec[4]]
        # TODO: ADD Locus dictionary of GFF, GTF, BED12,

    def get_filename(self):
        return self.file_name

    def get_filetype(self):
        return self.file_type

    """def check_input_file(file_path):
        #A function to test an input file and classifies it by content
        # try to guess file type by analysing the head
        guessed_type = ft.guess(file_path)
        file_zipped = False

        if guessed_type is None:
            # read uncompressed head
            file_head = pd.read_csv(file_path, sep='\t', header=None, nrows=5, error_bad_lines=False)
            zip_type = None
        elif guessed_type.mime in ['application/gzip', 'application/x-bzip2', 'application/zip']:
            zip_type = guessed_type.mime.split('/')[1]
            # read compressed head
            file_head = pd.read_csv(file_path, compression='infer', sep='\t', header=None, nrows=5,
                                    error_bad_lines=False, warn_bad_lines=False)
            file_zipped = True
        else:
            # return unsupported file type
            return FileInput(file_path, 'unsupported', False, False)
            # zip_type == None
        head_dtypes = np.array(file_head.dtypes)
        # check for header (no numbers in first row)
        header_present = not any(cell == np.int for cell in head_dtypes)
        header = pd.Series()
        if header_present:
            header = file_head.iloc[0]
            if file_zipped:
                file_head = pd.read_csv(file_path, compression='infer', sep='\t', header=None, nrows=5, skiprows=1,
                                        comment='#')
            else:
                file_head = pd.read_csv(file_path, sep='\t', header=None, nrows=5, skiprows=1, comment='#')

        # assign file type by shape of table
        head_dim = file_head.shape
        # check for BED4
        if head_dim[1] == 4:
            return FileInput(file_path, 'BED4', file_zipped, zip_type, header_present)
        # check for BED6
        elif head_dim[1] == 6:
            return FileInput(file_path, 'BED4', file_zipped, zip_type, header_present)
        # check for GFF or GTF
        elif head_dim[1] == 9:
            if not header.empty:
                for col in header:
                    if 'gff-version 3' in col:
                        return FileInput(file_path, 'GFF3', file_zipped, zip_type, header_present)
                    else:
                        return FileInput(file_path, 'GTF', file_zipped, zip_type, header_present)
            else:
                if '"' in file_head.iloc[0, 8]:
                    return FileInput(file_path, 'GTF', file_zipped, zip_type, header_present)
        elif head_dim[1] == 12:
            return FileInput(file_path, 'BED12', file_zipped, zip_type, header_present)
        else:
            # unsupported format
            return FileInput(file_path, 'unsupported', False, zip_type, header_present)

    # There might be some Packages that allow access to the file. This has not be
    # written by myself
    def getGTFFIle(self):
        gff3_dir = self.file_path()
        GFF3 = pd.read_csv(
            filepath_or_buffer=gff3_dir + "/samples/Araport11_protein_coding.201606.gtf",
            sep='\t',
            header=None,
            names=['chrom', 'chromStart', 'chromEnd', 'geneID', 'transID', 'score', 'strand', 'thickStart',
                   'thickEnd', 'itemRGB', 'blockCount', 'blockSizes', 'blockStarts'],
            skiprows=[i for i in xrange(25)]
        )
        GFF3 = GFF3[GFF3['source'].notnull()]
        return GFF3"""
