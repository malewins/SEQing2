from pandas import DataFrame, read_csv, errors
from src.input_files.File_type import Filetype
from src.input_files.ColumnHeader import Header
from src.input_files.File import FileInput
from pybedtools import BedTool
from logging import getLogger
import re


class Annotation:

    def __init__(self):
        self.transcript_to_gene = DataFrame()
        self.gene_with_start_stop = DataFrame()
        self.dropdown_menu = dict()
        self.expression_table = DataFrame
        self.logger = getLogger(__name__)

    def create_dict_for_annotation(self, anno_desc_files: list):
        """
        Create a dict for the igv-component and create a look-up table for the mapped transcript to gene.
        :param anno_desc_files: Takes a list of files that have at least a GFT- and a DESCRIPTION.CSV File
        """
        if len(anno_desc_files) > 3:
            raise NameError('To many arguments.')
        index_file = self.__get_file(Header.INDEX.value, anno_desc_files)
        if index_file is not None:
            anno_desc_files.remove(index_file)
        # Be careful the file itself has to have the name description
        desc_file = self.__get_file(Header.DESCRIPTION.value, anno_desc_files)
        if desc_file is not None:
            anno_desc_files.remove(desc_file)
        file_anno = anno_desc_files[0]  # Last element of the list
        anno_file = file_anno.get_filepath()
        anno_type = file_anno.get_filetype()
        if anno_type == Filetype.BED:
            csv = self.__load_file(index_file, Header.INDEX)
            anno = self.__load_file(index_file, Header.NONE)
            self.transcript_to_gene = csv.join(anno.set_index(Header.TRANSCRIPT_ID.value),
                                               on=Header.TRANSCRIPT_ID.value)
        if anno_type == Filetype.GTF:
            self.transcript_to_gene = self.__get_gtf_as_table(BedTool(anno_file))
        else:
            raise TypeError
        # Add Description to the Genes
        if desc_file is not None:
            desc = self.__load_file(desc_file, Header.DESCRIPTION)
            self.transcript_to_gene = self.transcript_to_gene.merge(
                                        desc[[Header.ENSEMBL_GENE_ID.value, Header.DESCRIPTION.value]],
                                        how='left', left_on=Header.GENE_ID.value,
                                        right_on=Header.ENSEMBL_GENE_ID.value)
        self.__get_dict_for_dropdown()

    def is_empty(self) -> bool:
        """
        Checks if Annotation was set.
        :return: True if is set, otherwise False
        :rtype: bool
        """
        return self.gene_with_start_stop.empty

    def get_dropdown_menu(self) -> dict:
        """
        Return a specific dict for dcc Dropdown.
        :return: Gen-Dict
        :rtype: dict {"label":GEN_ID - DESCRIPTION, "value": CHROMOSOME + GENE.START + GENE.STOP}
        """
        return self.dropdown_menu

    def get_transcript_to_gene(self) -> DataFrame:
        """
        Return a joined table, where transcript are mapped to its corresponding gene.
        :return: Long Table of Gene with transcripts
        :rtype: pandas.Dataframe()
        """
        return self.transcript_to_gene

    def get_genes_with_start_and_stops(self) -> DataFrame:
        """
        Return a table with length of the genes.
        :return: Gene Table with explicit start and stops
        :rtype: pandas.Dataframe()
        """
        return self.gene_with_start_stop

    @staticmethod
    def __get_gtf_as_table(gtf: BedTool) -> DataFrame:
        chromosome = []
        gen_id = []
        transcript_id = []
        start = []
        stop = []
        for entry in gtf:
            chromosome.append(entry.chrom)
            gen_id.append(entry.name)
            transcript_id.append(entry[Header.TRANSCRIPT_ID.value])
            start.append(entry.start)
            stop.append(entry.stop)
        return DataFrame(list(zip(gen_id, transcript_id, chromosome, start, stop)),
                         columns=[Header.GENE_ID.value, Header.TRANSCRIPT_ID.value, Header.CHROM.value,
                                  Header.START.value, Header.STOP.value])

    def __get_dict_for_dropdown(self):
        df = self.transcript_to_gene
        gen = []
        start = []
        stop = []
        chromosome = []
        dictionary_for_dropdown = []
        for name, group in df.groupby(by=[Header.GENE_ID.value]):
            gen.append(name)
            min_start = group[Header.START.value].min()
            start.append(min_start)
            max_stop = group[Header.STOP.value].max()
            stop.append(max_stop)
            chrom = str(group[Header.CHROM.value].iloc[0]).replace('Chr', '')
            chromosome.append(chrom)
            desc = self.__get_description_if_present(group)
            dictionary_for_dropdown.append({'label': str(name) + desc,
                                            'value': chrom + ':' + str(min_start) + '-' + str(max_stop)})
        self.gene_with_start_stop = DataFrame(list(zip(gen, chromosome, start, stop)),
                                              columns=[Header.GENE_ID.value, Header.CHROM.value,
                                                       Header.START.value, Header.STOP.value])
        self.dropdown_menu = dictionary_for_dropdown

    @staticmethod
    def __get_description_if_present(df) -> str:
        if Header.DESCRIPTION.value in df.columns:
            return ' - ' + str(df[Header.DESCRIPTION.value].values[0])
        return ''

    @staticmethod
    def __get_file(kind: str, all_files: list) -> FileInput or None:
        for file in all_files:
            if kind in file.get_filename().lower():
                return file
        return None

    @staticmethod
    def __filetype(anno_file) -> Filetype:
        if re.search(r"\b.bed\b", anno_file):
            return Filetype.BED
        if anno_file.find('.gtf') != -1:
            return Filetype.GTF
        return Filetype.NONE

    def __load_file(self, file, header: Header):
        try:
            if type(file) == FileInput:
                file = file.get_filepath()
            if header == Header.INDEX:
                return read_csv(file, compression='infer',
                                names=[Header.GENE_ID.value, Header.TRANSCRIPT_ID.value], sep='\t',
                                usecols=[0, 1])
            if header == Header.DESCRIPTION:
                return read_csv(file, compression='infer',
                                names=[Header.ENSEMBL_GENE_ID.value, Header.DESCRIPTION.value,
                                       Header.EXTERNAL_GENE_NAME.value, Header.GENE_BIOTYPE.value],
                                sep='\t',
                                usecols=[0, 1])
            else:
                return read_csv(file, compression='infer',
                                names=[Header.CHROM.value, Header.START.value, Header.STOP.value,
                                       Header.TRANSCRIPT_ID.value], sep='\t',
                                usecols=[0, 1, 2, 3])
        except errors.InvalidIndexError:
            self.logger.error('Column does not match with the names or the amount.')
            raise
