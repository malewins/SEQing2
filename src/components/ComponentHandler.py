#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pprint import pprint
import plotly.graph_objects as go


class Component:
    """
    The Component handler handel between the FilesHandler and the app.

    :param files_handler: FileHandler takes an Object of FileHandler
    """

    def __init__(self, files_handler):
        self.handler = files_handler
        self.current_genome_file = ""
        self.genome = []
        self.sequence_files = []
        self.annotation_files = ""
        self.expression_files = []
        self.description_files = []
        self.gen = ""
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
        if len(self.genome) != 0:
            self.current_genome_file = self.genome[0]

    def set_sequence_file(self, filename):
        """
        Set a given sequence file.

        :param filename: str filename of existing input_files.
        """
        color = 'rgb(0, 143, 255)'
        self.sequence_files = self.handler.get_specific_files_as_dict(filename, color)

    def set_annotation_file(self, filename):
        """
        Set a given annotation file.

        :param filename: str filename of existing input_files.
        """
        if filename != "" and filename is not None:
            self.annotation_files = self.handler.get_specific_file(filename)
        if len(self.handler.get_annotations()) != 0:
            self.annotation_files = self.handler.get_annotations()[0]
        else:
            pprint('There exist no annotation File.')

    def set_expression_file(self, filename):
        """
        Set a given expression file.

        :param filename: str filename of existing input_files.
        """
        if filename != "" and filename is not None:
            self.expression_files = [self.handler.get_specific_file(filename)]

    def set_description_files(self, filename):
        """
        Set a given description file.

        :param filename: str filename of existing input_files.
        """
        if filename != "" and filename is not None:
            self.description_files = []
            for file in filename:
                self.description_files.append(self.handler.get_specific_file(file))
        if len(self.handler.get_descriptions()) != 0 and filename == "":
            self.description_files = self.handler.get_descriptions()

    def set_gen_value(self, gen):
        self.gen = gen

    def get_current_gene_dict(self):
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

    def get_locus(self, gen):
        """
        Return the specific region on a genome.

        :param gen: str need the gen name
        :return: list[str]
        """
        if self.annotation_files != "":
            return self.handler.get_locus(self.annotation_files, gen)

    def get_annotations(self):
        """
        Return all annotation filenames type(GTF, GFF, BED12)

        :return: list[str]
        """
        return [file.get_filename() for file in self.handler.get_annotations()]

    def get_sequencing_files(self):
        """
        Return all sequencing input_files type (BAM, BED4/6, WIG, bigWIG)

        :doc: input_files.FilesHandler.FileHandler.get_sequencing_files
        """
        return self.handler.get_sequencing_files()

    def get_selected_files(self):
        """
        Return the selected input_files. If none is selected it returns the all file.

        :return: Returns a list of selected sequencing input_files as json-object for the igv-component.
        :rtype: list[json-object]
        """
        if len(self.sequence_files) > 0 and self.annotation_files != "":
            return self.sequence_files + [self.annotation_files.get_general_dict('rgb(238,77,46)')]
        return self.handler.get_specific_files_as_dict("", color='rgb(238,77,46)')

    def get_genome(self):
        """
        Return all possible genomes.

        :return: list[FileInput]
        """
        return self.genome

    def get_current_genome_file(self):
        """
        Return the chosen genome file. If there was only one, then this will be returned.

        :return: current genome File
        :rtype: FileInput
        """
        if self.current_genome_file != "":
            return self.current_genome_file
        return NameError("File is empty")

    def get_expression_files(self):
        """
        Return the chosen experiment file. If there was only one, then this will be returned.

        :return: current experiment file
        :rtype: FileInput
        """
        # if not self.expression_files:
        #   return None
        return self.handler.get_expressions()

    def get_description_files(self):
        """
        Return the chosen description file. If there was only one, then this will be returned.

        :return: current experiment file
        :rtype: FileInput
        """
        return self.handler.get_descriptions()

    def get_figure(self, gen_region):
        """
        Return an expression linegraph with error bars.

        :return: graph
        :rtype: go.Figure
        """
        # TODO: Not only get first expression_files!
        if self.expression_files:
            return self.handler.get_expression_figure(self.expression_files[0], gen_region)
        return go.Figure()

    def dict_is_not_set(self) -> bool:
        return self.handler.is_dict_set()
