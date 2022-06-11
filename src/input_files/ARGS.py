from os import listdir, access, R_OK, getcwd
from os.path import isdir
import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint


class Args:
    """Create Object class ARGS that handles arguments from the commandline."""

    def __init__(self):
        self.parser = ArgumentParser(description='Interactive, web based visualization for iCLIP and rna-seq data.')
        self.__set_argument()

    @staticmethod
    def __dir_path(string: str) -> str:
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
        # Add general dictionary with all files
        self.parser.add_argument('-dir', dest='dir', help='''Takes one folder, which should containing Files like:
                                fasta-, annotation-, bedGraph-, wig-, bigWig-, gff-, gtf-, csv- and tsv-input_files''',
                                 type=Path)
        self.parser.add_argument('-anno', dest='anno', help='''Directory that containing at least a gtf-file.
                                For further information, please add a description.csv file. 
                                For Bed12-File it is necessary to add an index.csv file. 
                                It is important that description and index appear in the filename.''',
                                 type=Path)
        # add Port as Parameter
        self.parser.add_argument('-port', dest='port', help='''Choose a port on which the app should run. 
                                For example -port 8050.''', type=int, default=8050)
        self.parser.add_argument('-dark', help='''Experimental Mode to display the data in a dark mode.''',
                                 action='store_true', default=False)
        self.parser.parse_args()

    def has_option(self, option: str) -> bool:
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
        if option == 'anno':
            return args.anno
        if option == 'dark':
            return args.dark
        raise TypeError

    def get_absolut_path(self, arg: str) -> Path or None:
        """
        Get absolut path for the folder given in dir or anno

        :return: Absolut path
        :rtype: Path or None
        """
        parser = self.parser.parse_args()
        if arg == 'dir':
            return Path(parser.dir).resolve()
        if arg == 'anno':
            return Path(parser.anno).resolve()
        return None

    def get_directory(self) -> str:
        """
        Return Directory. If it is not selected it return current directory.

        :return: directory path
        :rtype: str
        """
        args = self.parser.parse_args()
        if args.dir:
            directory = self.__validate_directory(args.dir)
            if len(listdir(directory)) > 0:
                return directory
            else:
                sys.exit('Directory is empty')
        return getcwd()

    def get_annotation_directory(self) -> str:
        """
        Return Directory. If it is not selected it raises NameError, because an annotation file is needed.

        :return: directory path
        :rtype: str
        :raise: NameError
        """
        args = self.parser.parse_args()
        if args.anno:
            directory = self.__validate_directory(args.anno)
            if len(listdir(directory)) > 0:
                return directory
            else:
                sys.exit('Directory is empty')
        raise NameError('Missing annotation directory! Please add a Folder with annotation files!')

    def get_files(self) -> list[str]:
        """
        Return a list of input input_files, given by the user.

        :return: file list
        :rtype: list[str]
        """
        args = self.parser.parse_args()
        files = []
        if args.fa:
            return [str(f) for f in args.fa if f]
        return files

    @staticmethod
    def __validate_directory(path) -> str:
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

    def get_port(self) -> int:
        """
        Return the port.

        :return: port
        :rtype: int
        """
        return self.parser.parse_args().port

    def get_mode(self) -> bool:
        """
        Return the mode in which the app is displayed.

        :return: True if dark mode is active otherwise false
        ;rtype: bool
        """
        return self.parser.parse_args().dark
