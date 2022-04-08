#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Bio import SeqIO
from pyBedGraph import BedGraph
from pybedtools import BedTool
from files.File_type import Filetype


class FileInput:
    """Decorator for file checking

    :param file_name: str
    :param file_path: str current path
    :param file_type: file_type all listed filetypes
    :param server_path: str server location, where the igv component has access to the files
    """

    def __init__(self, file_name, file_path, file_type, server_path):
        # zip_type could be removed, also zipped and header_present
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.server_path = server_path

    def get_dict_for_annotation(self):
        """
        Method returns a dictionary for annotation files

        :return: dict"""
        if self.file_type == Filetype.FASTA:
            return [{'value': rec.id, 'label': rec.name} for rec in SeqIO.parse(self.file_path, "fasta")]
        if self.file_type == Filetype.BEDGRAPH:  # This is a static test
            bed_graph = BedGraph('samples/example.sizes', self.file_path, ignore_missing_bp=False)
            return bed_graph.load_chrom_data('Chr1')
        if self.file_type in [Filetype.BED, Filetype.GTF, Filetype.GFF]:
            return [{'label': str(entry.name), 'value': str(entry.start) + ':' + str(entry.stop)}
                    for entry in BedTool(self.file_path)]
        if self.file_type == Filetype.GTF:
            return [{'label': str(entry.name), 'value': str(entry.start) + ':' + str(entry.stop)}
                    for entry in BedTool(self.file_path)]
        if self.file_type == Filetype.GFF:
            return [{'label': str(entry.name), 'value': str(entry.start) + ':' + str(entry.stop)}
                    for entry in BedTool(self.file_path)]

    def get_general_dict(self, colour):
        """
        Creates a dict entry for the igv component.

        :return: dict
        """
        if not colour:
            colour = 'rgb(191, 188, 6)'
        return dict(name="Read " + str(self.file_type),
                    url=self.server_path,
                    nameField='gene',
                    # indexed='false',
                    color=colour)

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
