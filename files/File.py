#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas
from Bio import SeqIO
from pyBedGraph import BedGraph
from pybedtools import BedTool
from files.File_type import Filetype
import plotly.graph_objects as go
from logging import getLogger


class FileInput:
    """Decorator for file checking

    :param file_name: str
    :param file_path: str current path
    :param file_type: file_type all listed filetypes
    :param server_path: str server location, where the igv component has access to the files
    """

    def __init__(self, file_name, file_path, file_type, server_path):
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.server_path = server_path
        self.logger = getLogger(__name__)

    def get_dict_for_annotation(self, gen_list):
        """
        Method returns a dictionary for annotation files

        :return: dict"""
        if self.file_type == Filetype.FASTA:
            return [{'value': rec.id, 'label': rec.name} for rec in SeqIO.parse(self.file_path, "fasta")]
        if self.file_type == Filetype.BEDGRAPH:  # This is a static test
            bed_graph = BedGraph('samples/example.sizes', self.file_path, ignore_missing_bp=False)
            return bed_graph.load_chrom_data('Chr1')
        if gen_list != "" or gen_list is not None:
            if self.file_type in [Filetype.BED, Filetype.GTF, Filetype.GFF, Filetype.GFF, Filetype.GFF]:
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
        Creates a dict entry for the igv component. Only works with Data-files

        :return: dict
        """
        # if self.file_type == Filetype.WIG:
        # transfomrer = pybedtools.contrib.bigwig.wig_to_bigwig(self.file_path,"", "test")
        # self.server_path = "tracks/" + transfomrer
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

    def get_graph(self):
        """
        Return an expression linegraph with error bars.

        :return: graph
        :rtype: go.Figure
        """
        expression_graph = go.Figure()
        if self.file_type == Filetype.SF:
            try:
                load_file = pandas.read_csv(self.file_path, compression='infer',
                                            names=['sample', 'sample2', 'replicate', 'quant_file'], sep=',',
                                            usecols=[0, 1, 2, 3])
                # samples = load_file['sample'].tolist()
                # samples2 = load_file['sample2'].tolist()
                # replicate = load_file['replicate'].tolist()
                quant_files = load_file['quant_file'].tolist()
                quant_files.remove('quant_file')  # Head has to be removed
                for file in quant_files:
                    absolut_file_path = str(self.file_path).replace(self.file_name, '') + file
                    salmon_data = pandas.read_csv(absolut_file_path, compression='infer', sep='\t',
                                                  names=['Name', 'Length', 'EffectiveLength', 'TMP', 'NumReads'],
                                                  usecols=[0, 1, 2, 3, 4])
                    expression_graph.add_trace(self.__create_graph(salmon_data))
                return expression_graph
            except pandas.errors.InvalidIndexError:
                self.logger.error('Column does not match with the names or the amount.')
                raise
        return expression_graph

    # Just for Testing
    @staticmethod
    def __create_graph(salmon):
        return go.Scatter(
            x=[1, 2, 3, 4],
            y=[2, 1, 3, 4],
            error_y=dict(
                type='data',
                symmetric=False,
                array=[0.1, 0.2, 0.1, 0.1],
                arrayminus=[0.2, 0.4, 1, 0.2])
        )
