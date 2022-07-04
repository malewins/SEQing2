from os import listdir
from os.path import isfile, join
from collections import deque

from plotly import graph_objects as go

from src.input_files.File_type import Filetype
from src.input_files.File import FileInput
from src.input_files.FileHandlerInterface import FileHandlerInterface
from src.input_files.AnnotationFile import Annotation
from src.input_files.ExpressionFile import Expression
from src.input_files.ARGS import Args
import re


class FileHandler(FileHandlerInterface):
    """
    File handler takes a path and creates an individual File for each Track for later identification.

    :param args: ARGS.Args takes the object Args
    """

    def __init__(self, args: Args):
        self.SERVER_FOLDER = 'tracks/'
        self.all_files = deque()
        self.args = args
        self.anno_file = Annotation()
        self.expression_file = Expression()
        self.path_of_files = args.get_absolut_path('dir')
        self.load_all_files(args.get_directory())

    def get_genome(self, filename: str) -> list[FileInput]:
        """
        Return a set of input_files, which could be used as a reference genome.

        :param filename: str from existing input_files
        :return: The genome list.
        :rtype: list[FileInput]
        """
        if not filename:
            return [genome for genome in self.all_files
                    if genome.get_filetype() == Filetype.FASTA]
        genome = []
        for name in filename:
            for file in self.all_files:
                if file.get_filename() == name:
                    genome.append(file)
        return genome

    def get_specific_files_as_dict(self, filename: list[str], color: str) -> list[dict]:
        """
        Return a list of dictionaries for the igv-component track.

        :param filename: list[str] of the existing input_files
        :param color: str (optional) colors the track. E.G. rgb(191,188,6)
        :return: dict a readable dict for the igv-component
        """
        specific_files = []
        if not filename:
            # This option is only if the user starts the app without specifying, which file to display
            return [sequence_file.get_general_dict(color) for sequence_file in self.all_files if
                    sequence_file.get_filetype() in [Filetype.BAM,
                                                     Filetype.BEDGRAPH,
                                                     # File_type.Filetype.WIG, future release
                                                     Filetype.bigWIG]]
        for name in filename:
            for specif_file in self.all_files:
                if specif_file.get_filename() == name:
                    specific_files.append(specif_file.get_general_dict(color))
        if len(specific_files) == 0:
            raise FileNotFoundError
        return specific_files

    def get_specific_file(self, file: str) -> FileInput:
        """
        Return a specific file.

        :param file: str of an existing filename
        :return: FileInput a specific file from all given input_files as file
        :rtype: FileInput
        """
        if file is not None:
            for entry in self.all_files:
                if isinstance(file, list):
                    for name in file:
                        if entry.get_filename() == name:
                            return entry
                elif entry.get_filename() == file:
                    return entry
            raise FileNotFoundError
        raise NameError('The field file is empty.')

    def get_gene_dict(self, annotation_files: list[FileInput]) -> dict or None:
        """
        Return a dict.

        :param  annotation_files: FileInput with datatype(BED6/12,GFF,GTF,CSV,TSV) as parameter
        :return: a dict to annotate the genes
        :rtype: dict or None
        """
        if self.anno_file.is_empty():
            if len(annotation_files) >= 2:
                self.anno_file.create_dict_for_annotation(annotation_files)
                return self.anno_file.get_dropdown_menu()
            # This is used if the user did not choose any annotation file
            if len(self.get_annotations()) != 0:
                return None
            return None
        return self.anno_file.get_dropdown_menu()

    def get_annotations(self) -> list[str]:
        """
        Returns a list of possible annotation input_files.

        :return: Files like GTF, BED12 as a list
        :rtype: list[str]
        """
        return sorted([file.get_filename() for file in self.all_files if
                       file.get_filetype() in [Filetype.GTF,
                                               Filetype.BED]])

    def get_coverage_files(self) -> list[str]:
        """
        Return a list of all possible coverage input_files.

        :return: Files like BAM, BED4(BedGraph), BED6, WIG, bigWIG
        :rtype: list[str]
        """
        return sorted([sequence_file.get_filename() for sequence_file in self.all_files if
                       sequence_file.get_filetype() in [Filetype.BAM,
                                                        Filetype.BEDGRAPH,
                                                        # File_type.Filetype.WIG, future release
                                                        Filetype.bigWIG]])

    def get_genome_files(self) -> list[str]:
        """
        Return a list of type FASTA.

        :return: Files like FA, FAS
        :rtype: list[str]
        """
        return sorted([genome.get_filename() for genome in self.all_files if
                       genome.get_filetype() is Filetype.FASTA])

    def get_expressions(self) -> list[str]:
        """
        Return a list of type CSV-input_files, which relegate to a folder of sf-input_files.

        :return: CSV-input_files
        :rtype: list[str]
        """
        return sorted([expression.get_filename() for expression in self.all_files if
                       expression.get_filetype() is Filetype.SF])

    def get_descriptions(self) -> list[str]:
        """
        Return a list of type CSV-input_files.

        :return: CSV-input_files
        :rtype: list[str]
        """
        return sorted([expression.get_filename() for expression in self.all_files if
                       expression.get_filetype() is Filetype.CSV])

    def get_expression_figure(self, file: FileInput, gene: str) -> go.Figure:
        """
        Return an expression linegraph with error bars.

        :param file: take a FileInput with Filetype.SF
        :param gene: takes the range of a gene on the chromosome
        :return: graph
        :rtype: go.Figure
        :raise: NameError if there exist no annotation file
        """
        if self.expression_file.is_empty():
            if not self.anno_file.is_empty():
                self.expression_file.create_expression_file(file, self.anno_file.get_transcript_to_gene(),
                                                            self.anno_file.get_genes_with_start_and_stops())
            else:
                raise NameError('Annotation file is missing!')
        return self.expression_file.get_expression_figure(gene)

    def is_dict_set(self) -> bool:
        """
        Return True if dictionary is set, otherwise False.

        :return: True or False
        :rtype: bool
        """
        return self.anno_file.is_empty()

    def load_all_files(self, path: str):
        """
        Load all Files into the FilesHandler.

        :param path: need a path to the directory/File
        :raises PermissionError: If the directory is not accessible
        """
        if self.args.has_option('dir'):
            only_files = [f for f in listdir(path) if isfile(join(path, f))]
        else:
            only_files = self.args.get_files()
        if self.args.has_option('anno'):
            anno_dict_path = self.args.get_annotation_directory()
            file_path = str(self.args.get_absolut_path('anno')) + '/'
            anno_files = [FileInput(f, file_path + f, self.__get_filetype(f)) for f in listdir(anno_dict_path) if
                          isfile(join(anno_dict_path, f))]
            if len(anno_files) < 4:
                self.anno_file.create_dict_for_annotation(anno_files)
            else:
                anno_files = [f for f in listdir(anno_dict_path) if isfile(join(anno_dict_path, f))]
                only_files = only_files + anno_files
        for file in only_files:
            file_name = self.__remove_zone_identifier(file.__str__())
            file_path = str(self.path_of_files) + '/' + file_name
            file_type = self.__get_filetype(file_path)

            # Check if Filetype was found and ignores zipped files
            if file_type != Filetype.NONE and file.find('.gz') == -1:
                the_file = FileInput(file_name, file_path, file_type,
                                     self.SERVER_FOLDER + file_name)
                self.all_files.append(the_file)

    def __get_filetype(self, file: str) -> Filetype:
        file_type = Filetype.NONE
        if re.search(r'\b.fa\b', file) or re.search(r'\b.fas\b', file):
            file_type = Filetype.FASTA
        if re.search(r'\b.fai\b', file):
            file_type = Filetype.FASTAINDEX
        if re.search(r"\b.bed\b", file):  # explicit search for .bed.
            # Be aware of input_files with index like .bed.gz.tbi
            file_type = Filetype.BED
        if file.find('.bedgraph') != -1:
            file_type = Filetype.BEDGRAPH
        if file.find('.gtf') != -1:
            file_type = Filetype.GTF
        if file.find('.gff') != -1:
            file_type = Filetype.GFF
        if file.find('bam') != -1:
            file_type = Filetype.BAM
        if file.find('wig') != -1:
            file_type = Filetype.WIG
        if file.find('bw') != -1:
            file_type = Filetype.bigWIG
        if file.find('csv') != -1:
            file_type = self.__check_csv(file)
        if file.find('tsv') != -1:
            file_type = Filetype.TSV
        return file_type

    @staticmethod
    def __check_csv(file: str) -> Filetype:
        if file.find('index') != -1:
            return Filetype.CSV
        if file.find('description') != -1:
            return Filetype.CSV
        if file.find('experiment') != -1:
            return Filetype.SF
        return Filetype.NONE

    @staticmethod
    def __remove_zone_identifier(file: str) -> str:
        return file.replace(':Zone.Identifier', '')
