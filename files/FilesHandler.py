from os import listdir
from os.path import isfile, join
from collections import deque

from files import File_type
from files.File import FileInput
from files.FileHandlerInterface import FileHandlerInterface
from pybedtools import BedTool

import re


class FileHandler(FileHandlerInterface):
    """
    File handler takes a path and creates an individual File for each Track for later identification.

    :param path: takes a directory/File
    """

    def __init__(self, path):
        self.all_files = deque()
        self.path_of_files = path
        self.SERVER_FOLDER = 'tracks/'
        self.load_all_files(path)

    def get_files_as_dict(self):
        """
        Return a set of files of the same type as dict for the dropdown menu.

        :return: dict with {value: filename, label: filename}"""
        return [file.get_filename() for file in self.all_files]

    def get_genome(self, filename):
        """
        Return a set of files, which could be used as a reference genome.

        :param filename: str from existing files
        :return: The genome list.
        :rtype: list[FileInput]
        """
        if not filename:
            return [genome for genome in self.all_files
                    if genome.get_filetype() == File_type.Filetype.FASTA]
        genome = []
        for name in filename:
            for file in self.all_files:
                if file.get_filename() == name:
                    genome.append(file)
        return genome

    def get_specific_files_as_dict(self, filename, color):
        """
        Return a list of dictionaries for the igv-component track.

        :param filename: list[str] of the existing files
        :param color: str (optional) colors the track. E.G. rgb(191,188,6)
        :return: dict a readable dict for the igv-component
        """
        specific_files = []
        if not filename:
            # This option is only if the user starts the app without specifying, which file to display
            # TODO: need to add BED6
            return [sequence_file.get_general_dict(color) for sequence_file in self.all_files if
                    sequence_file.get_filetype() in [File_type.Filetype.BAM,
                                                     File_type.Filetype.BEDGRAPH,
                                                     File_type.Filetype.WIG,
                                                     File_type.Filetype.bigWIG]]
        for name in filename:
            for specif_file in self.all_files:
                if specif_file.get_filename() == name:
                    specific_files.append(specif_file.get_general_dict(color))
        if len(specific_files) == 0:
            return FileNotFoundError
        return specific_files

    def get_specific_file(self, file):
        """
        Return a specific file.

        :param file: str of an existing filename
        :return: FileInput a specific file from all given files as file"""
        if file is not None:
            for entry in self.all_files:
                if isinstance(file, list):
                    for name in file:
                        if entry.get_filename() == name:
                            return entry
                elif entry.get_filename() == file:
                    return entry
            return FileNotFoundError
        return NameError('The field file is empty.')

    def get_gene_dict(self, annotation_files):
        """
        Return a dict.

        :param  annotation_files: FileInput with datatype(BED6/12,GFF,GTF) as parameter
        :return: a dict to annotate the genes
        """
        if annotation_files != "":
            return annotation_files.get_dict_for_annotation()
        # This is used if the user did not chose any annotation file
        return self.get_annotations()[0].get_dict_for_annotation()

    def get_annotations(self):
        """
        Returns a list of possible annotation files.

        :return: list[FileInput] files like GTF, GFF, BED12 as a list
        """
        return [file for file in self.all_files if
                file.get_filetype() in [File_type.Filetype.GFF,
                                        File_type.Filetype.GTF,
                                        File_type.Filetype.BED]]

    def get_sequencing_files(self):
        """
        :return: list[FileInput] Files like BAM, BED4(BedGraph), BED6, WIG, bigWIG"""
        # TODO: Implement BED6-File as sequence-File
        return [sequence_file.get_filename() for sequence_file in self.all_files if
                sequence_file.get_filetype() in [File_type.Filetype.BAM,
                                                 File_type.Filetype.BEDGRAPH,
                                                 File_type.Filetype.WIG,
                                                 File_type.Filetype.bigWIG]]

    def get_genome_files(self):
        """
        Return a list of type FASTA.

        :return: list[FileInput] Files like FA, FAS"""
        return [genome.get_filename() for genome in self.all_files if
                genome.get_filetype() is File_type.Filetype.FASTA]

    @staticmethod
    def get_locus(genome_file, gen):
        """
        Return the specific location of a genome.

        :param genome_file: FileInput file need the current genome-file
        :param gen: str need the annotated gen
        :return: a dict readable for the igv-component
        """
        return genome_file.get_locus(gen)

    def load_all_files(self, path):
        """
        Load all Files into the FilesHandler.

        :param path: need a path to the directory/File
        :raises PermissionError: If the directory is not accessible
        """
        only_files = [f for f in listdir(path) if isfile(join(path, f))]
        for file in only_files:
            zip_type = ""
            header_present = False
            try:
                file_type = self.__get_filetype(file)
                if file_type != File_type.Filetype.NONE and file.find('.gz') == -1:  # ignore zipped files
                    the_file = FileInput(file.__str__(), self.path_of_files / file.__str__(),
                                         file_type,
                                         False, zip_type, header_present, self.SERVER_FOLDER + file.__str__())
                    self.all_files.append(the_file)
            except PermissionError:
                raise OSError

            # TODO: handle :ZONEIdentifier, zip, tbi, fas, tsv and other file types.

    def __get_filetype(self, file):
        file_type = File_type.Filetype.NONE
        if file.find('.fa') != -1:
            file_type = File_type.Filetype.FASTA
        if re.search(r"\b.bed\b", file):  # explicit search for .bed. Maybe should be used also on other files
            # Be aware of files with index like .bed.gz.tbi
            file_type = self.__check_bed(file)
        if file.find('.bedgraph') != -1:
            file_type = File_type.Filetype.BEDGRAPH
        if file.find('.gtf') != -1:
            file_type = File_type.Filetype.GTF
        if file.find('.gff') != -1:
            file_type = File_type.Filetype.GFF
        if file.find('bam') != -1:
            file_type = File_type.Filetype.BAM
        if file.find('wig') != -1:
            file_type = File_type.Filetype.WIG
        if file.find('bw') != -1:
            file_type = File_type.Filetype.bigWIG
        # TODO: Add TSV and CSV files
        return file_type

    def __check_bed(self, file):
        # May not needed for an extra check
        BedTool(str(self.path_of_files) + '/' + file)
        return File_type.Filetype.BED
