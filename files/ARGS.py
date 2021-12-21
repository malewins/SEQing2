import os.path
import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint


class Args:
    """Create Object class ARGS"""

    def __init__(self):
        self.parser = ArgumentParser(description='Interactive, web based visualization for iCLIP and rna-seq data.')
        self.__set_argument(self)

    @staticmethod
    def __dir_path(string):
        if os.path.isdir(string):
            return string
        else:
            raise NotADirectoryError(string)

    @staticmethod
    def __set_argument(self):
        # File bed12 or gtf
        self.parser.add_argument('-gen', dest='geneAnnotion',
                                 help='''files containing gene annotations in bed12 or gtf format,
                                  at least one such file is required for execution. 
                                  These files should not include a header.''',
                                 nargs='+', type=Path)
        # File bedgraph
        self.parser.add_argument('-bsraw', dest='bsraw', help='''files containing iCLIP data, 
                                in .bedgraph format. Everything before the first underscore _ 
                                in the file name will be treated as prefix and used to match 
                                iCLIP files to files containing binding sites. 
                                These files should not include a header.''',
                                 nargs='+', type=Path, default=[])
        # File csv
        self.parser.add_argument('-desc', dest='desc', help='''file containing gene descriptions,
                                tab seperated csv with 3 columns. This file should not include include a header line,
                                but the column order has to match:
                                    gene_id description gene_name''',
                                 type=Path)

        # File fa
        self.parser.add_argument('-seqs', dest='fa', help='''Fa files containing genomic sequences''',
                                 type=Path, nargs='+')

        self.parser.add_argument('-dir', dest='dir', help='''Takes a folder, which should containing Files like:
                            fasta-File, Annoation-File, bedgraph-File.''',
                                 type=Path)
        self.parser.add_argument('-web', dest='web-application',
                                 help='''If you want to start the application as a web-application.''')

        self.parser.parse_args()

    def has_option(self, option):
        """Checks for option. If option does not exist it throws an Exception
            @:param option: to check, if the option is available
            @:return true if the option appears otherwise false"""
        if len(option) > 0:
            if hasattr(self.parser.parse_args(), option):
                return True
            else:
                return False

    def get_directory(self):
        """Return Directory. If it is not selected it return current directory
        @:return directory path"""

        # should throw exception if to many arguments are
        # If directory is empty this should be checked

        args = self.parser.parse_args()

        if args.dir:
            directory = self.__validate_directory(args.dir)
            if len(os.listdir(directory)) > 0:
                return directory
            else:
                sys.exit('Directory is empty')
        return os.getcwd()

    @staticmethod
    def __validate_directory(path):
        """Should be a private method, which checks the directory
        @:param path: take a (absolute) path
        @:return the path of the directory"""
        if not path.is_dir():
            pprint("Not a directory")
            raise NotADirectoryError
        if not os.access(path, os.R_OK):
            pprint("Not accessible")
            raise PermissionError
        return path


'''def load_iclip_data(binding_site_raw_path):
    if len(binding_site_raw_path) > 0:
        print('Loading iCLIP data.')
        for i in binding_site_raw_path:
            try:
                dtypes = {'chrom': 'category', 'chromStart': 'uint64', 'chromEnd': 'uint64', 'count': 'uint32'}
                df = pandas.read_csv(i, compression='infer', sep='\t',
                                     names=['chrom', 'chromStart', 'chromEnd', 'count'], dtype=dtypes)
                # validation = validateBedGraph(df)
                if True:
                    if i.stem.split('_')[0] not in data_set_names:
                        data_set_names.append(i.stem.split('_')[0])
                        bs_raw_dfs.update({str(data_set_names[-1]): df})
                    else:
                        print('Warning, you are using the same prefix for multiple iCLIP files, file ' + str(
                            i) + ' will be ignored')
                else:
                    print('Error in file ' + str(i) + ':')
                    print(validation[1])
            except FileNotFoundError:
                print('File ' + str(i) + ' was not found')
            except ValueError as e:
                print('File ' + str(i.stem) + ' had errornous data types or missing values: ' + str(e))
        print('Done.')


def load_basic_descriptions(gene_id_path):
    gene_names = list(set().union([k for k in [i['gene_id'].tolist() for i in gene_annotations]]))
    geneDescriptions = pandas.read_csv(gene_id_path, compression='infer',
                                       names=['ensembl_gene_id', 'description', 'external_gene_name'], sep='\t',
                                       usecols=[0, 1, 2])
    # Filter for genes that are actually in the dataset
    geneDescriptions = geneDescriptions[geneDescriptions['ensembl_gene_id'].isin(gene_names)]
    geneDescriptions.fillna(':', inplace=True)
'''
