#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class IClipHandler:

    def __init__(self, files_handler):
        self.handler = files_handler
        self.current_file = ""
        # self.current_file = files_handler.get_beds()[0]

    def set_reference(self):
        return self.handler.get_general_reference_dict()

    def set_selected_file(self, file):
        self.current_file = self.handler.get_specific_file(file)

    def get_current_gene_dict(self):
        return self.handler.get_gene_dict()

    def get_locus(self, genome):
        # locus at the moment only for bed-files
        return self.handler.get_locus(genome)

    def get_file_options(self):
        return self.handler.get_files_as_dict()
