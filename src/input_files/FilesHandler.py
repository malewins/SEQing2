import csv
from os import listdir
from os.path import isfile, join
from collections import deque
from pprint import pprint

from plotly import graph_objects as go

import pandas
import logging
from pybedtools import BedTool

from src.input_files.File_type import Filetype
from src.input_files.File import FileInput
from src.input_files.FileHandlerInterface import FileHandlerInterface

import re

# Const values
GENE_ID = 'gene_id'
CHROM = 'Chrom'
START = 'Start'
STOP = 'Stop'
TRANSCRIPT_ID = 'transcript_id'
SAMPLE = 'Sample'
SAMPLE2 = 'Sample2'
TPM = 'TPM'


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
        self.transcript_to_gene = pandas.DataFrame()
        self.gene_with_start_stop = pandas.DataFrame()
        self.expression_table = pandas.DataFrame()
        self.load_all_files(args.get_directory())
        self.logger = logging.getLogger(__name__)

    def get_files_as_dict(self):
        """
        Return a set of input_files of the same type as dict for the dropdown menu.

        :return: dict with {value: filename, label: filename}"""
        return [file.get_filename() for file in self.all_files]

    def get_genome(self, filename):
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

    def get_specific_files_as_dict(self, filename, color):
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
            return FileNotFoundError
        return specific_files

    def get_specific_file(self, file):
        """
        Return a specific file.

        :param file: str of an existing filename
        :return: FileInput a specific file from all given input_files as file"""
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
            return None
            # return self.get_annotations()[0].get_dict_for_annotation("")
        return None

    def get_annotations(self):
        """
        Returns a list of possible annotation input_files.

        :return: Files like GTF, GFF, BED12 as a list
        :rtype: list[FileInput]
        """
        return [file for file in self.all_files if
                file.get_filetype() in [Filetype.GFF,
                                        Filetype.GTF,
                                        Filetype.BED]]

    def get_sequencing_files(self):
        """
        Return a list of all possible sequencing input_files.

        :return: Files like BAM, BED4(BedGraph), BED6, WIG, bigWIG
        :rtype: list[FileInput]
        """
        # TODO: Implement BED6-File as sequence-File
        return [sequence_file.get_filename() for sequence_file in self.all_files if
                sequence_file.get_filetype() in [Filetype.BAM,
                                                 Filetype.BEDGRAPH,
                                                 # File_type.Filetype.WIG, future release
                                                 Filetype.bigWIG]]

    def get_genome_files(self):
        """
        Return a list of type FASTA.

        :return: Files like FA, FAS
        :rtype: list[FileInput]
        """
        return [genome.get_filename() for genome in self.all_files if
                genome.get_filetype() is Filetype.FASTA]

    def get_expressions(self):
        """
        Return a list of type CSV-input_files, which relegate to a folder of sf-input_files.

        :return: CSV-input_files
        :rtype: list[FileInput]
        """
        return [expression.get_filename() for expression in self.all_files if
                expression.get_filetype() is Filetype.SF]

    def get_descriptions(self):
        """
        Return a list of type CSV-input_files.

        :return: CSV-input_files
        :rtype: list[FileInput]
        """
        return [expression.get_filename() for expression in self.all_files if
                expression.get_filetype() is Filetype.CSV]

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
        # TODO: return description as string for given gene
        pass

    def __get_gen_name(self, gene):
        df = self.gene_with_start_stop
        for gen, chrom, start, stop in zip(df.gene_id, df.Chrom, df.Start, df.Stop):
            if gene == str(chrom) + ':' + str(start) + '-' + str(stop):
                return gen

    @staticmethod
    def __get_transcript_plot(transcript_table):
        fig = go.Figure()
        for name, group_sample in transcript_table.groupby(by=[GENE_ID, SAMPLE]):
            sample = name[1]
            for some_name, group_transcript in group_sample.groupby(by=[TRANSCRIPT_ID]):
                x_axis = []
                table_for_calculation = group_transcript.groupby(by=[SAMPLE2])
                y_axis = list(table_for_calculation[TPM].mean())
                standard_deviation = list(table_for_calculation[TPM].std())
                for sample2, grp in table_for_calculation:
                    key = sample + '_' + sample2
                    x_axis.append(key)
                fig.add_trace(go.Scatter(x=x_axis, y=y_axis,
                                         error_y=dict(type='data',
                                                      symmetric=True,
                                                      array=standard_deviation,
                                                      arrayminus=standard_deviation)))
        return fig

    def get_expression_figure(self, file, gene):
        """
        Return an expression linegraph with error bars.

        :return: graph
        :rtype: go.Figure
        """

        if self.expression_table.empty:
            self.expression_table = file.get_tpm_table(self.transcript_to_gene)
        gene = self.__get_gen_name(gene)
        table_for_figure = self.expression_table[self.expression_table[GENE_ID].isin([gene])]
        table_for_figure = table_for_figure.reset_index()
        table_for_figure = table_for_figure.drop(columns=table_for_figure.columns[0], axis=1)
        table_for_figure[TPM] = table_for_figure[TPM].astype(float)
        return self.__get_transcript_plot(table_for_figure)

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

                # Check if Filetype was found and ignores zipped input_files
                if file_type != Filetype.NONE and file.find('.gz') == -1:
                    the_file = FileInput(file_name, file_path, file_type,
                                         self.SERVER_FOLDER + file_name)
                    self.all_files.append(the_file)
            except PermissionError:
                raise OSError

            # TODO: handle  zip, tbi, tsv and other file types.

    def __get_filetype(self, file):
        file_type = Filetype.NONE
        if file.find('.fa') != -1:
            file_type = Filetype.FASTA
        if re.search(r"\b.bed\b", file):  # explicit search for .bed. Maybe should be used also on other input_files
            # Be aware of input_files with index like .bed.gz.tbi
            file_type = self.__check_bed()
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
    def __check_csv(file):
        # TODO: check if args has option exp and return this file(s)
        # if self.args.has_option('exp'):
        try:
            with open(file, 'r') as f:
                header = csv.Sniffer().has_header(f.read(1024))
                if header:
                    gene_description = pandas.read_csv(file, on_bad_lines='skip')
                    # TODO: Check if salmon-reference input_files are present. Instead to check column sample
                    if 'sample' in gene_description.columns:
                        return Filetype.SF
            return Filetype.CSV
        except OSError:
            pprint('Something went wrong while reading the file.')
        except IndexError:
            pprint('File has no Description.')
        except ValueError:
            pprint('Something is wrong with the file.')

    @staticmethod
    def __check_bed():
        """
        THis should check if it is a BED6 annotation-File or BED6 sequencing file.
        """
        # May not needed for an extra check
        #        BedTool(str(self.path_of_files) + '/' + file)
        return Filetype.BED

    @staticmethod
    def __remove_zone_identifier(file):
        return file.replace(':Zone.Identifier', '')

    def __create_dict_for_annotation(self, anno_desc_files):
        desc_file = anno_desc_files[0]
        anno_file = anno_desc_files[1]
        # 'ensembl_gene_id', 'description', 'external_gene_name'=name and usecols=[0,1,2]
        # TODO: Check for header, Check description and or gene_id, check length of amount of colls
        # Load CSV file
        try:
            # Be careful the file itself has to have the name index
            if str(desc_file.get_filename()).find('index'):
                load_csv = pandas.read_csv(desc_file.get_filepath(), compression='infer',
                                           names=[GENE_ID, TRANSCRIPT_ID], sep='\t',
                                           usecols=[0, 1])
                # TODO: only works with Bed and GTF files currently
                if anno_file.get_filetype() == Filetype.BED:
                    load_anno = pandas.read_csv(anno_file.get_filepath(), compression='infer',
                                                names=[CHROM, START, STOP, TRANSCRIPT_ID], sep='\t',
                                                usecols=[0, 1, 2, 3])
                    df = load_csv.join(load_anno.set_index(TRANSCRIPT_ID), on=TRANSCRIPT_ID)
                    self.transcript_to_gene = df
                if anno_file.get_filetype() == Filetype.GTF:
                    self.transcript_to_gene = self.__get_gtf_as_table(BedTool(anno_file.get_filepath()))
                return self.__get_dict_for_dropdown()
                # return anno_file.get_dict_for_annotation("")

        except pandas.errors.InvalidIndexError:
            self.logger.error('Column does not match with the names or the amount.')
            raise
            # gene_names = list_gene_desc.union([gene.name for gene in anno_file_tool])
            # self.gene_description = list_gene_desc.union([gene.name for gene in anno_file_tool])

    @staticmethod
    def __get_gtf_as_table(gtf):
        chromosom = []
        gen_id = []
        transcript_id = []
        start = []
        stop = []
        for entry in gtf:
            chromosom.append(entry.chrom)
            gen_id.append(entry.name)
            transcript_id.append(entry[TRANSCRIPT_ID])
            start.append(entry.start)
            stop.append(entry.stop)
        return pandas.DataFrame(list(zip(gen_id, transcript_id, chromosom, start, stop)),
                                columns=[GENE_ID, TRANSCRIPT_ID, CHROM, START, STOP])

    def __get_dict_for_dropdown(self):
        df = self.transcript_to_gene
        gen = []
        start = []
        stop = []
        chromosome = []
        dictionary_for_dropdown = []
        for name, group in df.groupby(by=[GENE_ID]):
            gen.append(name)
            min_start = group[START].min()
            start.append(min_start)
            max_stop = group[STOP].max()
            stop.append(max_stop)
            chrom = str(group[CHROM]).replace('Chr', '')
            chromosome.append(chrom[0])
            dictionary_for_dropdown.append({'label': name,
                                            'value': chrom[0] + ':' + str(min_start) + '-' + str(max_stop)})
        self.gene_with_start_stop = pandas.DataFrame(list(zip(gen, chromosome, start, stop)),
                                                     columns=[GENE_ID, CHROM, START, STOP])
        return dictionary_for_dropdown
