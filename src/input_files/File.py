#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math

import pandas
from Bio import SeqIO
from pyBedGraph import BedGraph
from pybedtools import BedTool
from src.input_files.File_type import Filetype
from plotly import graph_objects as go
from logging import getLogger

# Const values
NAME = 'Name'
LENGTH = 'Length'
EFFECTIVE_LENGTH = 'EffectiveLength'
TPM = 'TPM'
NUM_READS = 'NumReads'
GENE_ID = 'gene_id'
TRANSCRIPT_ID = 'transcript_id'
SAMPLE = 'Sample'
SAMPLE2 = 'Sample2'
REPLICATE = 'replicate'
QUANT_FILE = 'quant_file'
CHROM = 'Chrom'
START = 'Start'
STOP = 'Stop'


class FileInput:
    """Decorator for file checking

    :param file_name: str
    :param file_path: str current path
    :param file_type: file_type all listed filetypes
    :param server_path: str server location, where the igv component has access to the input_files
    """

    def __init__(self, file_name, file_path, file_type, server_path):
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.server_path = server_path
        self.logger = getLogger(__name__)

    def get_dict_for_annotation(self, gen_list):
        """
        Method returns a dictionary for annotation input_files

        :return: dict"""
        if self.file_type == Filetype.FASTA:
            return [{'value': rec.id, 'label': rec.name} for rec in SeqIO.parse(self.file_path, "fasta")]
        if self.file_type == Filetype.BEDGRAPH:  # This is a static test
            bed_graph = BedGraph('samples/example.sizes', self.file_path, ignore_missing_bp=False)
            return bed_graph.load_chrom_data('Chr1')
        if self.file_type in [Filetype.BED, Filetype.GTF, Filetype.GFF, Filetype.GFF, Filetype.GFF]:
            bed_tool_file = BedTool(self.file_path)
            print(bed_tool_file[0].name)
            if gen_list != "" and gen_list is not None:
                return [{'label': str(entry.name),
                         'value': str(entry.chrom).replace('Chr', '') + ':' + str(entry.start) + '-' + str(entry.stop)}
                        for entry in BedTool(self.file_path)
                        if entry.name in gen_list]
            else:
                return [{'label': str(entry.name),
                         'value': str(entry.chrom).replace('Chr', '') + ':' + str(entry.start) + '-' + str(entry.stop)}
                        for entry in BedTool(self.file_path)]

    # TODO: If dict has instead of 2 -> chr2 than it is not necessary to replace Chr.
    #  It could have total different names

    def get_general_dict(self, colour):
        """
        Creates a dict entry for the igv component. Only works with Data-input_files

        :return: dict
        """
        # if self.file_type == Filetype.WIG:
        # transfomrer = pybedtools.contrib.bigwig.wig_to_bigwig(self.file_path,"", "test")
        if not colour:
            colour = 'rgb(191, 188, 6)'
        return dict(name=self.file_name,
                    url=self.server_path,
                    nameField='gene',
                    # indexed='false',
                    color=colour)

    def get_genes_for_annotation(self):
        if self.file_type in [Filetype.BED, Filetype.GTF, Filetype.GFF, Filetype.GFF, Filetype.GFF]:
            print([str(entry.name) for entry in BedTool(self.file_path)])
            return [str(entry.name) for entry in BedTool(self.file_path)]
        return None

    def get_locus(self, gen):
        """
        Return the position of the gen on the genome as json-Object for the igv-component.

        :param gen: str the actual unique gen-name
        :return: Location of the gen
        :rtype: list[str]
        """
        if gen is not None:
            locus = [str(entry.chrom) + ':' + str(entry.start) + '-' + str(entry.stop) for entry in
                     BedTool(self.file_path)
                     if (str(entry.start) + ':' + str(entry.stop)) == gen]
            if locus is not None:
                return locus
            return ValueError
        return gen

    def get_filename(self):
        """
        Return the name of the file.

        :return: filename
        :rtype: str
        """
        return self.file_name

    def get_filetype(self):
        """
        Return the type of the file.

        :return: filetype
        :rtype: file_type
        """
        return self.file_type

    def get_serverpath(self):
        """
        Return the path of the file on the server.

        :return: server path
        :rtype: str
        """
        return self.server_path

    def get_filepath(self):
        """
        Return the path of the file on the local drive.

        :return: file path
        :rtype: str
        """
        return self.file_path

    def get_tpm_table(self, gene_list_with_transcripts):
        """
        Return an expression linegraph with error bars.

        :return: graph
        :rtype: go.Figure
        """
        gene_table = pandas
        if self.file_type == Filetype.SF:
            try:
                load_file = pandas.read_csv(self.file_path, compression='infer',
                                            names=[SAMPLE, SAMPLE2, REPLICATE, QUANT_FILE], sep=',',
                                            usecols=[0, 1, 2, 3])
                length = len(load_file)
                pos = 1  # skips header
                absolut_file_path = str(self.file_path).replace(self.file_name, '') + load_file[QUANT_FILE].iloc[
                    pos]
                salmon_data = pandas.read_csv(absolut_file_path, compression='infer', sep='\t',
                                              names=[NAME, LENGTH, EFFECTIVE_LENGTH, TPM, NUM_READS],
                                              usecols=[0, 1, 2, 3, 4])

                gene_list_with_transcripts = gene_list_with_transcripts.merge(salmon_data[[TPM, NAME]],
                                                                              how='left', left_on=TRANSCRIPT_ID,
                                                                              right_on=NAME).drop(
                    columns=[NAME, CHROM, START, STOP])  # These columns are in no further interests
                gene_list_with_transcripts = gene_list_with_transcripts.dropna(subset=TPM)
                gene_list_with_transcripts.loc[:, SAMPLE] = load_file[SAMPLE].iloc[pos]
                gene_list_with_transcripts.loc[:, SAMPLE2] = load_file[SAMPLE2].iloc[pos]
                pos = 2
                gene_id_list = gene_list_with_transcripts[GENE_ID].tolist()
                transcript_id_list = gene_list_with_transcripts[TRANSCRIPT_ID].tolist()
                while pos < length:
                    # Can be reduced by zip see gtf_test
                    tmp_table = pandas.DataFrame()
                    absolut_file_path = str(self.file_path).replace(self.file_name, '') + load_file[QUANT_FILE].iloc[
                        pos]
                    salmon_data = pandas.read_csv(absolut_file_path, compression='infer', sep='\t',
                                                  names=[NAME, LENGTH, EFFECTIVE_LENGTH, TPM, NUM_READS],
                                                  usecols=[0, 1, 2, 3, 4])
                    tmp_table.loc[:, GENE_ID] = gene_id_list
                    tmp_table.loc[:, TRANSCRIPT_ID] = transcript_id_list
                    salmon_data = tmp_table.join(salmon_data.set_index([NAME]), on=TRANSCRIPT_ID)
                    salmon_data = salmon_data.dropna(subset=[TPM])
                    tmp_table.loc[:, TPM] = salmon_data[TPM]
                    tmp_table.loc[:, SAMPLE] = load_file[SAMPLE].iloc[pos]
                    tmp_table.loc[:, SAMPLE2] = load_file[SAMPLE2].iloc[pos]
                    gene_list_with_transcripts = pandas.concat([gene_list_with_transcripts, tmp_table])
                    pos += 1
                return gene_list_with_transcripts
            except pandas.errors.InvalidIndexError:
                self.logger.error('Column does not match with the names or the amount.')
                raise
        return gene_table

    @staticmethod
    def __get_standard_deviation(for_square_sum, mean, n_times):
        square_sum = 0
        for elm in for_square_sum:
            square_sum = square_sum + (elm - mean) * (elm - mean)  # sum^(i=0)^(n) (i-mean)^2
        return math.sqrt(square_sum / n_times)  # root of the variance
