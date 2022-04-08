#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Component:

    def __init__(self, files_handler):
        self.handler = files_handler
        self.current_genome_file = ""
        self.genome = []
        self.sequence_files = []
        self.annotation_files = ""
        self.expression_files = []
        self.set_genome("")

    def set_genome(self, filename):
        """
        Set s specific genome.

        :param filename: str filename of existing files.
        """
        self.genome = self.handler.get_genome(filename)
        if filename != "" and filename is not None:
            self.current_genome_file = self.handler.get_specific_file(filename)
        else:
            self.current_genome_file = self.genome[0]

    def set_sequence_file(self, filename):
        color = 'rgb(0, 143, 255)'
        self.sequence_files = self.handler.get_specific_files_as_dict(filename, color)

    def set_annotation_file(self, filename):
        if filename != "" and filename is not None:
            self.annotation_files = self.handler.get_specific_file(filename)
        else:
            self.annotation_files = self.handler.get_annotations()[0]

    def set_expression_file(self, filename):
        color = 'rgb(22, 22, 24)'
        self.expression_files = self.handler.get_specific_files_as_dict(filename, color)

    def get_current_gene_dict(self):
        if self.annotation_files != "":
            return self.handler.get_gene_dict(self.annotation_files)
        return self.handler.get_gene_dict("")

    def get_locus(self, genome):
        if self.annotation_files != "":
            return self.handler.get_locus(self.annotation_files, genome)

    def get_file_options(self):
        return self.handler.get_files_as_dict()

    def get_annotations(self):
        return [file.get_filename() for file in self.handler.get_annotations()]

    def get_sequencing_files(self):
        return self.handler.get_sequencing_files()

    def get_selected_files(self):
        if len(self.sequence_files) > 0:
            return self.sequence_files
        return self.handler.get_specific_files_as_dict("", color='238,77,46')

    def get_genome(self):
        return self.genome

    def get_current_genome_file(self):
        if self.current_genome_file != "":
            return self.current_genome_file
        return NameError("File is empty")
