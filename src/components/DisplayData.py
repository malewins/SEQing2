from dash import dcc, html, Input, Output
import dash_bio

from dash.exceptions import PreventUpdate

from src.app.AppInterface import app
from src.input_files.Colors import Color

"""This File provides settings to display the specific data and not all data at once. This has a performance reason."""
Line = {'textAlign': 'left', 'height': '1px', 'width': '1500px', 'backgroundColor': Color.BLACK_HTML.value}
center = {'textAlign': 'center'}


class Display:
    """ Displays the data on the webpage.

    :param component: ComponentHandler.Component takes the object Component
    """

    def __init__(self, component):
        self.iclip = component
        self.gen = ""
        self.selected_files = component.get_selected_files()
        self.location = ""
        self.fig = component.get_figure("")

        @app.callback(
            Output('igv', 'children'),
            Input('Gen-select', 'value'))
        def return_igv(value):
            """Return the IGV component with the selected genome."""
            self.gen = value
            component.set_gen_value(value)
            return html.Div([
                dash_bio.Igv(
                    id='locus-igv',
                    locus=value,
                    reference=self.get_references()
                )])

        @app.callback(
            Output('information-output', 'children'),
            Input('Gen-select', 'value'))
        def update_output(value):
            if not value:
                raise PreventUpdate
            self.gen = value
            return 'The coordinate of the Gene is : \n{}'.format(value)

        @app.callback(
            Output('graph', 'children'),
            Input('Gen-select', 'value'))
        def update_graph(value):
            if not value:
                raise PreventUpdate
            return html.Div(dcc.Graph(figure=self.iclip.get_figure(value)), id='plot')

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

    def get_references(self):
        """
        Return a dict as references for the igv-component.

        :return: reference dict
        :rtype: dict
        """

        return dict(id="A.thaliana (TAIR 10)",
                    name="A. thaliana (TAIR 10)",
                    fastaURL=self.iclip.get_current_genome_file(),
                    indexURL=self.iclip.get_current_index_file(),
                    #indexURL='tracks/Arabidopsis_thaliana.TAIR10.dna.toplevel.fa.fai',
                    #indexURL="https://s3.amazonaws.com/igv.org.genomes/tair10/TAIR10_chr_all.fas.fai",
                    #aliasURL="https://s3.amazonaws.com/igv.org.genomes/tair10/TAIR10_alias.tab",
                    tracks=self.iclip.get_selected_files()
                    )

    def gene_annotation_area(self):
        """
        This method provides a section, where a gen description takes place.
        """
        return html.Div(children=[
            html.Div(id='information-output')
        ])

    @staticmethod
    def set_expression_graph():
        """
        This method provides a section, where the expression graph takes place.
        """
        return html.Div(children=[
            html.Hr(style=Line),
            html.H2('Expression-Graph', style=center),
            dcc.Loading(id='graph')
        ])

    def layout(self):
        """
        Returns the layout of /page1.

        :return: html layout.
        :rtype: html
        """
        return html.Div(children=[
            self.gene_annotation_area(),
            self.clustergram(),
            self.set_expression_graph()
        ])
