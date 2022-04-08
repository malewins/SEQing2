#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        """
        Set a given sequence file.

        :param filename: str filename of existing files.
        """
        color = 'rgb(0, 143, 255)'
        self.sequence_files = self.handler.get_specific_files_as_dict(filename, color)

    def set_annotation_file(self, filename):
        """
        Set a given annotation file.

        :param filename: str filename of existing files.
        """
        if filename != "" and filename is not None:
            self.annotation_files = self.handler.get_specific_file(filename)
        else:
            self.annotation_files = self.handler.get_annotations()[0]

    def set_expression_file(self, filename):
        """
        Set a given expression file.

        :param filename: str filename of existing files.
        """
        color = 'rgb(22, 22, 24)'
        self.expression_files = self.handler.get_specific_files_as_dict(filename, color)

    def get_current_gene_dict(self):
        """
        Return gene annotation for the dropdown menu.

        :return: Return a dict as json object for the dropdown menu.
        :rtype: json-object as dict
        """
        if self.annotation_files != "":
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
        Return all sequencing files type (BAM, BED4/6, WIG, bigWIG)

        :doc: files.FilesHandler.FileHandler.get_sequencing_files
        """
        return self.handler.get_sequencing_files()

    def get_selected_files(self):
        """
        Return the selected files. If none is selected it returns the all file.

        :return: Returns a list of selected sequencing files as json-object for the igv-component.
        :rtype: list[json-object]
        """
        if len(self.sequence_files) > 0:
            return self.sequence_files
        return self.handler.get_specific_files_as_dict("", color='238,77,46')

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
