#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from src.input_files.File import FileInput
from src.input_files.Colors import Color
import plotly.graph_objects as go


class Component:
    """
    The Component handler handel between the FilesHandler and the app.

    :param files_handler: FileHandler takes an Object of FileHandler
    """

    def __init__(self, files_handler):
        self.handler = files_handler
        self.current_genome_file: FileInput = FileInput('', '', '')
        self.current_index_file: FileInput = FileInput('', '', '')
        self.genome: list = []
        self.sequence_files: list = []
        self.annotation_files: list = []
        self.expression_files: list = []
        self.description_files: list = []
        self.gen: str = ""
        self.set_genome("")

    def set_genome(self, filename):
        """
        Set s specific genome. This has to be loaded first,
         to return a genome for the igv-component.

        :param filename: str filename of existing input_files.
        """
        self.genome = self.handler.get_genome(filename)

        if filename != "" and filename is not None:
            self.current_genome_file = self.handler.get_specific_file(filename)
            # index file has to be in the same directory and must be a fasta index file!
            self.current_index_file = self.handler.get_specific_file(filename + '.fai')
        elif len(self.genome) != 0:
            self.current_genome_file = self.genome[0]
            self.current_index_file = self.handler.get_genome(filename + '.fai')

    def set_sequence_file(self, filename):
        """
        Set a given sequence file.

        :param filename: str filename of existing input_files.
        """
        self.sequence_files = self.handler.get_specific_files_as_dict(filename, Color.ORANGE_RGB.value)

    def set_annotation_file(self, filename):
        """
        Set a given annotation file.

        :param filename: str filename of existing input_files.
        """
        if filename is not None:
            self.annotation_files = self.handler.get_specific_files_as_dict(filename, Color.GREEN_RGB.value)

    def set_expression_file(self, filename):
        """
        Set a given expression file.

        :param filename: str filename of existing input_files.
        """
        if filename != "" and filename is not None:
            self.expression_files = [self.handler.get_specific_file(filename)]

    def set_gen_value(self, gen):
        self.gen = gen

    def get_current_gene_dict(self) -> dict:
        """
        Return gene annotation for the dropdown menu.

        :return: Return a dict as json object for the dropdown menu.
        :rtype: json-object as dict
        """
        if self.description_files:
            return self.handler.get_gene_dict(self.description_files)
        if self.annotation_files != "" and self.description_files:
            return self.handler.get_gene_dict(self.annotation_files)
        return self.handler.get_gene_dict("")

    def get_annotations(self) -> list[str]:
        """
        Return all annotation filenames type(GTF, GFF, BED12)

        :return: A list of filenames
        :rtype: list[str]
        """
        return [file.get_filename() for file in self.handler.get_annotations()]

    def get_sequencing_files(self):
        """
        Return all sequencing input_files type (BAM, BED4/6, WIG, bigWIG)

        :doc: input_files.FilesHandler.FileHandler.get_sequencing_files
        """
        return self.handler.get_sequencing_files()

    def get_selected_files(self) -> list[dict]:
        """
        Return the selected input_files. If none is selected it returns the all file.

        :return: Returns a list of selected sequencing input_files as json-object for the igv-component.
        :rtype: list[json-object]
        """
        if len(self.sequence_files) > 0 and self.annotation_files:
            return self.sequence_files + self.annotation_files
        return self.handler.get_specific_files_as_dict("", color=Color.ORANGE_RGB.value)

    def get_genome(self) -> list[FileInput]:
        """
        Return all possible genomes.

        :return: List of all Input File_type FASTA
        :rtype: list[FileInput]
        """
        return self.genome

    def get_current_genome_file(self) -> str:
        """
        Return the chosen genome file. If there is no file, it will raise NameError

        :return: current server path of the genome file
        :rtype: str
        """
        if not self.current_genome_file.is_empty():
            return self.current_genome_file.get_serverpath()
        raise NameError("File is empty!")

    def get_current_index_file(self) -> str:
        """
        Return the corresponding index file. If there is no file, it will raise NameError.

        :return: current server path of the index file
        :rtype: str
        """
        if not self.current_index_file.is_empty():
            return self.current_index_file.get_serverpath()
        raise NameError("No existing index File!")

    def get_expression_files(self) -> list[str]:
        """
        Return the chosen experiment file. If there was only one, then this will be returned.

        :return: current experiment file
        :rtype: list[str]
        """
        return self.handler.get_expressions()

    def get_description_files(self) -> list[str]:
        """
        Return the chosen description file. If there was only one, then this will be returned.

        :return: current experiment file
        :rtype: list[str]
        """
        return self.handler.get_descriptions()

    def get_figure(self, gen_region: str) -> go.Figure:
        """
        Return an expression linegraph with error bars.

        :param gen_region: Needs the gene region to create a specific Graph for the gene.
        :return: graph
        :rtype: go.Figure
        """
        # TODO: Not only get first expression_files!
        if self.expression_files:
            return self.handler.get_expression_figure(self.expression_files[0], gen_region)
        return go.Figure()

    def dict_is_not_set(self) -> bool:
        return self.handler.is_dict_set()
