from os import listdir
from os.path import isfile, join
from collections import deque

from files import File_type
from files.File import FileInput
from files.FileHandlerInterface import FileHandlerInterface

import re


class FileHandler(FileHandlerInterface):

    def __init__(self, path):
        # Could be stored in one Datastructure
        self.all_files = deque()
        self.path_of_files = path
        self.SERVER_FOLDER = 'tracks/'
        self.load_all_files(path)

    def get_files_as_dict(self):
        """Return a set of files of the same type as dict for the dropdown menue
        @:return a dict with {value: filename, label: filename}"""
        return [{'value': file.get_filename(), 'label': file.get_filename()} for file in self.all_files]

    def get_general_reference_dict(self):
        return [track.get_general_dict() for track in self.all_files if track.get_filetype() != File_type.Filetype.FASTA]

    def get_specific_file(self, file):
        # at the moment just for bed
        for entry in self.all_files:
            if entry.get_filename() == file:
                return entry
        return FileNotFoundError

    def get_beds(self):
        beds = []
        for file in self.all_files:
            if file.get_filetype() == File_type.Filetype.BED:
                beds.append(file)
        return beds
        # return [bed for bed in self.all_files if bed.get_filetype() == File_type.Filetype.BED]

    def get_gene_dict(self):
        return self.get_beds()[0].get_dict()

    # TODO: Works only with bed at the moment

    def get_locus(self, genome):
        return self.get_beds()[0].get_locus(genome)

    # TODO: Wokrs only with bed files

    def load_all_files(self, path):
        """Load all Files into the files handler"""
        only_files = [f for f in listdir(path) if isfile(join(path, f))]
        for file in only_files:
            zip_type = ""
            header_presend = False
            file_type = File_type.Filetype.NONE
            try:
                if file.find('.fa') != -1:
                    file_type = File_type.Filetype.FASTA
                if re.search(r"\b.bed\b", file):  # explicit search for .bed. Maybe should be used also on other files
                    # Be aware of files with index like .bed.gz.tbi
                    file_type = File_type.Filetype.BED
                if file.find('.bedgraph') != -1:
                    file_type = File_type.Filetype.BEDGRAPH
                if file.find('.gtf') != -1:
                    file_type = File_type.Filetype.GTF
                if file.find('.gff') != -1:
                    file_type = File_type.Filetype.GFF
                if file_type != File_type.Filetype.NONE and file.find('.gz') == -1:  # ignore zipped files
                    the_file = FileInput(file.__str__(), self.path_of_files / file.__str__(),
                                         file_type,
                                         False, zip_type, header_presend, self.SERVER_FOLDER + file.__str__())
                    self.all_files.append(the_file)
            except PermissionError:
                raise OSError

            # TODO: handle :ZONEIdentifier, zip, bam, tbi, fa, fas and other file types.
