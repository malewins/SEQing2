from os import listdir, access, R_OK, getcwd
from os.path import isdir
import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint


class Args:
    """Create Object class ARGS"""

    def __init__(self):
        self.parser = ArgumentParser(description='Interactive, web based visualization for iCLIP and rna-seq data.')
        self.__set_argument()

    @staticmethod
    def __dir_path(string):
        if isdir(string):
            return string
        else:
            raise NotADirectoryError(string)

    def __set_argument(self):
        # File bed12 or gtf
        self.parser.add_argument('-gen', dest='genAnnotation',
                                 help='''Files containing gene annotations in bed12, gtf or gff format,
                                  at least one such file is required for execution. 
                                  These input_files should not include a header.''',  # Maybe can include header
                                 nargs='+', type=Path)
        # File bedgraph
        self.parser.add_argument('-bsraw', dest='bsraw', help='''Files containing iCLIP data, 
                                in .bedgraph, wig and bigWig format.  
                                These input_files should not include a header.''',
                                 nargs='+', type=Path)

        # File csv
        self.parser.add_argument('-desc', dest='desc', help='''File containing gene descriptions,
                                tab seperated csv or tsv with 3 columns. 
                                This file should not include include a header line, but the column order has to match:
                                    gene_id description gene_name''',
                                 type=Path, nargs='+')
        self.parser.add_argument('-exp', dest='exp', help='''File contains a list with sample, replica and the location
                                of the file with filetype Salmon(.sf). E.g. WT_18, 1, Quant_WT_1.sf.''',
                                 type=Path, nargs='+')
        # File fa
        self.parser.add_argument('-seqs', dest='fa', help='''Fa or fas input files containing genomic sequences''',
                                 type=Path, nargs='+')

        self.parser.add_argument('-dir', dest='dir', help='''Takes one folder, which should containing Files like:
                                fasta-, annotation-, bedGraph-, wig-, bigWig-, gff-, gtf-, csv- and tsv-input_files''',
                                 type=Path)

        # add Port as Parameter
        self.parser.add_argument('-port', dest='port', help='''Choose a port on which the app should run. 
                                For example -port 8050.''', type=int, default=8050)
        self.parser.parse_args()

    def has_option(self, option):
        """
        Checks for option. If option does not exist it throws an Exception.

        :param option: to check, if the option is available
        :return: true if the option appears otherwise false
        :rtype: bool
        """
        args = self.parser.parse_args()

        if option == 'genAnnotation':
            return args.genAnnotation
        if option == 'bsraw':
            return args.bsraw
        if option == 'desc':
            return args.desc
        if option == 'exp':
            return args.exp
        if option == 'fa':
            return args.fa
        if option == 'dir':
            return args.dir
        if option == 'port':
            return args.port
        return TypeError

    def get_absolut_path(self):
        parser = self.parser.parse_args()
        if parser.dir:
            return Path(parser.dir).resolve()
        if parser.fa:
            for fa in parser.fa:
                return Path(fa).resolve()

    def get_directory(self):
        """
        Return Directory. If it is not selected it return current directory.

        :return: directory path
        :rtype: str
        """
        # should throw exception if to many arguments are present

        args = self.parser.parse_args()

        if args.dir:
            directory = self.__validate_directory(args.dir)
            if len(listdir(directory)) > 0:
                return directory
            else:
                sys.exit('Directory is empty')
        return getcwd()

    def get_files(self):
        """
        Return a list of input input_files, given by the user.

        :return: file list
        :rtype: list[path]
        """
        args = self.parser.parse_args()
        files = []
        if args.fa:
            return [str(f) for f in args.fa if self.__validate_files(f)]
        return files

    @staticmethod
    def __validate_directory(path):
        """
        Should be a private method, which checks the directory.

        :param path: take a (absolute) path
        :return: the path of the directory
        :rtype: str
        """
        if not Path.exists(path):
            pprint("Path does not exist.")
            raise ValueError
        if not path.is_dir():
            pprint("Not a directory")
            raise NotADirectoryError
        if not access(path, R_OK):
            pprint("Not accessible")
            raise PermissionError
        return path

    @staticmethod
    def __validate_files(path):
        # TODO: Must be corrected
        # print(Path(path).resolve())
        # if not Path(aPath).exists():
        #   pprint("Path does not exist.")
        #  raise ValueError
        # if not Path.is_file(path):
        #   pprint("File not Found.")
        #  raise FileNotFoundError
        # if not access(path, R_OK):
        #    pprint("Not accessible")
        #   raise PermissionError
        return path

    def get_port(self):
        """
        Return the port.

        :return: port
        :rtype: int
        """
        return self.parser.parse_args().port
