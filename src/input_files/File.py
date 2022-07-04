#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pybedtools import BedTool
from src.input_files.File_type import Filetype
from src.input_files.Colors import Color
from logging import getLogger


class FileInput:
    """Decorator for file checking

    :param file_name: str
    :param file_path: str current path
    :param file_type: file_type all listed filetypes
    :param server_path: str server location, where the igv component has access to the input_files
    """

    def __init__(self, file_name, file_path, file_type, server_path=''):
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.server_path = server_path
        self.logger = getLogger(__name__)

    def get_general_dict(self, colour) -> dict:
        """
        Creates a dict entry for the igv component. Only works with Data-input_files

        :return: dict
        """
        if not colour:
            colour = Color.YELLOW_RGB.value
        return dict(name=self.file_name,
                    url=self.server_path,
                    nameField='gene',
                    color=colour)

    def get_genes_for_annotation(self) -> list[str]:
        if self.file_type in [Filetype.BED, Filetype.GTF, Filetype.GFF, Filetype.GFF, Filetype.GFF]:
            print([str(entry.name) for entry in BedTool(self.file_path)])
            return [str(entry.name) for entry in BedTool(self.file_path)]
        return None

    def get_locus(self, gen) -> list[str]:
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
            raise ValueError
        return gen

    def get_filename(self) -> str:
        """
        Return the name of the file.

        :return: filename
        :rtype: str
        """
        return self.file_name

    def get_filetype(self) -> Filetype:
        """
        Return the type of the file.

        :return: filetype
        :rtype: Filetype
        """
        return self.file_type

    def get_serverpath(self) -> str:
        """
        Return the path of the file on the server.

        :return: server path
        :rtype: str
        """
        return self.server_path

    def get_filepath(self) -> str:
        """
        Return the path of the file on the local drive.

        :return: file path
        :rtype: str
        """
        return self.file_path

    def is_empty(self) -> bool:
        """

        """
        if self.file_name == "":
            return True
        return False
