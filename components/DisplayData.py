from dash import dcc, html, Input, Output
import dash_bio

from AppInterface import app


class Display:

    def __init__(self, component):
        self.iclip = component
        self.gen = ""

        @app.callback(
            Output('igv', 'children'),
            Input('Gen-select', 'value'))
        def return_igv(value):
            """Return the IGV component with the selected genome."""
            self.gen = value
            return html.Div([
                dash_bio.Igv(
                    id='locus-igv',
                    locus=component.get_locus(value),
                    reference=dict(
                        id="A.thaliana (TAIR 10)",
                        name="A. thaliana (TAIR 10)",
                        # fastaURL="tracks/TAIR10_chr_all_noYWMKSRD.fa",
                        fastaURL=self.iclip.get_current_genome_file().get_serverpath(),
                        indexURL="https://s3.amazonaws.com/igv.org.genomes/tair10/TAIR10_chr_all.fas.fai",
                        aliasURL="https://s3.amazonaws.com/igv.org.genomes/tair10/TAIR10_alias.tab",
                        tracks=component.get_selected_files()
                    )
                )])

        @app.callback(
            Output('information-output', 'children'),
            Input('information', 'value'))
        def update_output(value):
            # TODO: Fill information of the gene
            return '# The information is: \n{}'.format(str(self.gen), value)

    def clustergram(self):
        """This method provides the Gene-Selection."""
        return html.Div([
            dcc.Dropdown(
                id='Gen-select',
                options=self.iclip.get_current_gene_dict(),
                placeholder='Select a gene...'
            ),
            dcc.Loading(id='igv'),
            html.Div(id='select-gen')
        ])

    def gene_annotation_area(self):
        """
        This method provides a section, where a gen description takes place
        """
        return html.Div(children=[
            dcc.Textarea(value='''# The information about the gen: \n''' + str(self.gen),
                         id='information'),
            html.Div(id='information-output')
        ])

    def layout(self):
        return html.Div(children=[
            self.gene_annotation_area(),
            self.clustergram()
        ])
