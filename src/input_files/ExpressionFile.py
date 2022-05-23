from pandas import DataFrame, read_csv, concat, errors
from logging import getLogger
from plotly import graph_objects as go
from src.input_files.File_type import Filetype
from src.input_files.ColumnHeader import Header


class Expression:

    def __init__(self):
        self.transcript_to_gene = DataFrame()
        self.gene_with_start_stop = DataFrame()
        self.expression_table = DataFrame()
        self.logger = getLogger(__name__)

    def is_empty(self):
        return self.expression_table.empty

    def get_expression_figure(self, gene):
        """
        Return an expression linegraph with error bars.

        :return: graph
        :rtype: go.Figure
        """
        gene = self.__get_gen_name(gene)
        table_for_figure = self.expression_table[self.expression_table[Header.GENE_ID.value].isin([gene])]
        table_for_figure = table_for_figure.reset_index()
        table_for_figure = table_for_figure.drop(columns=table_for_figure.columns[0], axis=1)
        table_for_figure[Header.TPM.value] = table_for_figure[Header.TPM.value].astype(float)
        return self.__get_transcript_plot(table_for_figure)

    def create_expression_file(self, file, gene_list_with_transcripts: DataFrame, start_and_stop: DataFrame):
        """
        Return an expression linegraph with error bars.

        :return: graph
        :rtype: go.Figure
        """
        self.gene_with_start_stop = start_and_stop
        gene_table = DataFrame()
        if file.get_filetype() == Filetype.SF:
            try:
                load_file = read_csv(file.get_filepath(), compression='infer',
                                     names=[Header.SAMPLE.value, Header.SAMPLE2.value, Header.REPLICATE.value,
                                            Header.QUANT_FILE.value], sep=',',
                                     usecols=[0, 1, 2, 3])
                length = len(load_file)
                pos = 1  # skips header
                absolut_file_path = str(file.get_filepath()).replace(file.get_filename(), '') + \
                                    load_file[Header.QUANT_FILE.value].iloc[
                                        pos]
                salmon_data = read_csv(absolut_file_path, compression='infer', sep='\t',
                                       names=[Header.NAME.value, Header.LENGTH.value,
                                              Header.EFFECTIVE_LENGTH.value, Header.TPM.value,
                                              Header.NUM_READS.value],
                                       usecols=[0, 1, 2, 3, 4])

                gene_list_with_transcripts = gene_list_with_transcripts.merge(
                    salmon_data[[Header.TPM.value, Header.NAME.value]],
                    how='left', left_on=Header.TRANSCRIPT_ID.value,
                    right_on=Header.NAME.value).drop(
                    columns=[Header.NAME.value, Header.CHROM.value, Header.START.value,
                             Header.STOP.value])  # These columns are in no further interests
                gene_list_with_transcripts = gene_list_with_transcripts.dropna(subset=Header.TPM.value)
                gene_list_with_transcripts.loc[:, Header.SAMPLE.value] = load_file[Header.SAMPLE.value].iloc[pos]
                gene_list_with_transcripts.loc[:, Header.SAMPLE2.value] = load_file[Header.SAMPLE2.value].iloc[pos]
                pos = 2
                gene_id_list = gene_list_with_transcripts[Header.GENE_ID.value].tolist()
                transcript_id_list = gene_list_with_transcripts[Header.TRANSCRIPT_ID.value].tolist()
                while pos < length:
                    # Can be reduced by zip see gtf_test
                    tmp_table = DataFrame()
                    absolut_file_path = str(file.get_filepath()).replace(file.get_filename(), '') + \
                                        load_file[Header.QUANT_FILE.value].iloc[
                                            pos]
                    salmon_data = read_csv(absolut_file_path, compression='infer', sep='\t',
                                           names=[Header.NAME.value, Header.LENGTH.value,
                                                  Header.EFFECTIVE_LENGTH.value, Header.TPM.value,
                                                  Header.NUM_READS.value],
                                           usecols=[0, 1, 2, 3, 4])
                    tmp_table.loc[:, Header.GENE_ID.value] = gene_id_list
                    tmp_table.loc[:, Header.TRANSCRIPT_ID.value] = transcript_id_list
                    salmon_data = tmp_table.join(salmon_data.set_index([Header.NAME.value]),
                                                 on=Header.TRANSCRIPT_ID.value)
                    salmon_data = salmon_data.dropna(subset=[Header.TPM.value])
                    tmp_table.loc[:, Header.TPM.value] = salmon_data[Header.TPM.value]
                    tmp_table.loc[:, Header.SAMPLE.value] = load_file[Header.SAMPLE.value].iloc[pos]
                    tmp_table.loc[:, Header.SAMPLE2.value] = load_file[Header.SAMPLE2.value].iloc[pos]
                    gene_list_with_transcripts = concat([gene_list_with_transcripts, tmp_table])
                    pos += 1
                self.expression_table = gene_list_with_transcripts
            except errors.InvalidIndexError:
                self.logger.error('Column does not match with the names or the amount.')
                raise
        else:
            raise FileNotFoundError

    @staticmethod
    def __get_transcript_plot(transcript_table):
        fig = go.Figure()
        for name, group_sample in transcript_table.groupby(by=[Header.GENE_ID.value, Header.SAMPLE.value]):
            sample = name[1]
            for transcript_name, group_transcript in group_sample.groupby(by=[Header.TRANSCRIPT_ID.value]):
                x_axis = []
                table_for_calculation = group_transcript.groupby(by=[Header.SAMPLE2.value])
                y_axis = list(table_for_calculation[Header.TPM.value].mean())
                standard_deviation = list(table_for_calculation[Header.TPM.value].std())
                for sample2, grp in table_for_calculation:
                    key = sample + '_' + sample2
                    x_axis.append(key)
                fig.add_trace(go.Scatter(x=x_axis, y=y_axis, name=transcript_name,
                                         error_y=dict(type='data',
                                                      symmetric=True,
                                                      array=standard_deviation,
                                                      arrayminus=standard_deviation)))
        return fig

    def __get_gen_name(self, gene):
        df = self.gene_with_start_stop
        for gen, chrom, start, stop in zip(df.gene_id, df.Chrom, df.Start, df.Stop):
            if gene == str(chrom) + ':' + str(start) + '-' + str(stop):
                return gen
