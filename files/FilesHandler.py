import csv
from os import listdir
from os.path import isfile, join
from collections import deque
from pprint import pprint

import pandas
import logging
from pybedtools import BedTool

from files import File_type
from files.File import FileInput
from files.FileHandlerInterface import FileHandlerInterface

import re


class FileHandler(FileHandlerInterface):

    """
    File handler takes a path and creates an individual File for each Track for later identification.

    :param args: ARGS.Args takes the object Args
    """

    def __init__(self, args):
        self.SERVER_FOLDER = 'tracks/'
        self.all_files = deque()
        self.args = args
        self.path_of_files = args.get_absolut_path()
        self.gene_description = []
        self.load_all_files(args.get_directory())
        self.logger = logging.getLogger(__name__)

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
            return [sequence_file.get_general_dict(color) for sequence_file in self.all_files if
                    sequence_file.get_filetype() in [File_type.Filetype.BAM,
                                                     File_type.Filetype.BEDGRAPH,
                                                     # File_type.Filetype.WIG,
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

        :param  annotation_files: FileInput with datatype(BED6/12,GFF,GTF,CSV,TSV) as parameter
        :return: a dict to annotate the genes
        """
        # First is always a CSV or TSV file
        if len(annotation_files) == 2:
            return self.__create_dict_for_annotation(annotation_files)

        # This is used if the user did not choose any annotation file
        if len(self.get_annotations()) != 0:
            return self.get_annotations()[0].get_dict_for_annotation("")
        return None

    def get_annotations(self):
        """
        Returns a list of possible annotation files.

        :return: Files like GTF, GFF, BED12 as a list
        :rtype: list[FileInput]
        """
        return [file for file in self.all_files if
                file.get_filetype() in [File_type.Filetype.GFF,
                                        File_type.Filetype.GTF,
                                        File_type.Filetype.BED]]

    def get_sequencing_files(self):
        """
        Return a list of all possible sequencing files.

        :return: Files like BAM, BED4(BedGraph), BED6, WIG, bigWIG
        :rtype: list[FileInput]
        """
        # TODO: Implement BED6-File as sequence-File
        return [sequence_file.get_filename() for sequence_file in self.all_files if
                sequence_file.get_filetype() in [File_type.Filetype.BAM,
                                                 File_type.Filetype.BEDGRAPH,
                                                 # File_type.Filetype.WIG,
                                                 File_type.Filetype.bigWIG]]

    def get_genome_files(self):
        """
        Return a list of type FASTA.

        :return: Files like FA, FAS
        :rtype: list[FileInput]
        """
        return [genome.get_filename() for genome in self.all_files if
                genome.get_filetype() is File_type.Filetype.FASTA]

    def get_expressions(self):
        """
        Return a list of type CSV-files, which relegate to a folder of sf-files.

        :return: CSV-files
        :rtype: list[FileInput]
        """
        return [expression.get_filename() for expression in self.all_files if
                expression.get_filetype() is File_type.Filetype.SF]

    def get_descriptions(self):
        """
        Return a list of type CSV-files.

        :return: CSV-files
        :rtype: list[FileInput]
        """
        return [expression.get_filename() for expression in self.all_files if
                expression.get_filetype() is File_type.Filetype.CSV]

    @staticmethod
    def get_locus(genome_file, gen):
        """
        Return the specific location of a genome.

        :param genome_file: FileInput file need the current genome-file
        :param gen: str need the annotated gen
        :return: a dict readable for the igv-component
        """
        return genome_file.get_locus(gen)

    def get_gene_description(self, value):
        pass

    @staticmethod
    def get_expression_figure(file):
        """
        Return an expression linegraph with error bars.

        :return: graph
        :rtype: go.Figure
        """
        return file.get_graph()

    def load_all_files(self, path):
        """
        Load all Files into the FilesHandler.

        :param path: need a path to the directory/File
        :raises PermissionError: If the directory is not accessible
        """
        if self.args.has_option('dir'):
            only_files = [f for f in listdir(path) if isfile(join(path, f))]
        else:
            only_files = self.args.get_files()
        for file in only_files:
            try:
                file_name = self.__remove_zone_identifier(file.__str__())
                file_path = str(self.path_of_files) + '/' + file_name
                file_type = self.__get_filetype(file_path)

                # Check if Filetype was found and ignores zipped files
                if file_type != File_type.Filetype.NONE and file.find('.gz') == -1:
                    the_file = FileInput(file_name, file_path, file_type,
                                         self.SERVER_FOLDER + file_name)
                    self.all_files.append(the_file)
            except PermissionError:
                raise OSError

            # TODO: handle  zip, tbi, tsv and other file types.

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
        if file.find('csv') != -1:
            file_type = self.__check_csv(file)
        if file.find('tsv') != -1:
            file_type = File_type.Filetype.TSV
        return file_type

    @staticmethod
    def __check_csv(file):
        # TODO: check if args has option exp and return this file(s)
        # if self.args.has_option('exp'):
        try:
            with open(file, 'r') as f:
                header = csv.Sniffer().has_header(f.read(1024))
                if header:
                    gene_description = pandas.read_csv(file, on_bad_lines='skip')
                    # TODO: Check if salmon-reference files are present. Instead to check column sample
                    if 'sample' in gene_description.columns:
                        return File_type.Filetype.SF
            return File_type.Filetype.CSV
        except OSError:
            pprint('Something went wrong while reading the file.')
        except IndexError:
            pprint('File has no Description.')
        except ValueError:
            pprint('Something is wrong with the file.')

    @staticmethod
    def __check_bed(file):
        """
        THis should check if it is a BED6 annotation-File or BED6 sequencing file.
        """
        # May not needed for an extra check
        #        BedTool(str(self.path_of_files) + '/' + file)
        return File_type.Filetype.BED

    @staticmethod
    def __remove_zone_identifier(file):
        return file.replace(':Zone.Identifier', '')

    def __create_dict_for_annotation(self, anno_desc_files):
        desc_file = anno_desc_files[0]
        anno_file = anno_desc_files[1]
        # 'ensembl_gene_id', 'description', 'external_gene_name'=names and usecols=[0,1,2]
        # TODO: Check for header, Check description and or gene_id, check length of amount of colls
        # Load CSV file
        try:
            load_csv = pandas.read_csv(desc_file.get_filepath(), compression='infer',
                                       names=['ensembl_gene_id', 'description'], sep='\t',
                                       usecols=[0, 1])
            # Load Annotation-file
            anno_file_tool = BedTool(anno_file.get_filepath())
            # Maybe need to add larger range of genes due to gene_index.csv
            # list_gene_names = set(load_csv['ensembl_gene_id'].tolist())
            list_gene_desc = set(load_csv['description'].tolist())
            gene_names = list_gene_desc.union([gene.name for gene in anno_file_tool])
            self.gene_description = list_gene_desc.union([gene.name for gene in anno_file_tool])
            return anno_file.get_dict_for_annotation(gene_names)

        except pandas.errors.InvalidIndexError:
            self.logger.error('Column does not match with the names or the amount.')
            raise
