# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_bio
from dash.dependencies import Input, Output
from dash import dcc
from dash import html

# Static Default style
from flask import send_from_directory, Flask

from files import File_type


class AppHandler:
    """
    App handler, which handels the app
    @:param absolut_dir_path: takes an absolut path to a directory
    @:param iclip: need the iclip handler to interact with
    """

    def __init__(self, absolut_dir_path, iclip):
        self.server = Flask(__name__)
        self.app = dash.Dash(server=self.server)
        self.dir = absolut_dir_path
        self.file_option = iclip.get_file_options()
        self.current_gene_options = iclip.get_current_gene_dict()
        self.iclip = iclip

        @self.server.route('/tracks/<path:path>')
        def data(path):
            """Evoke that the files are available via a server"""
            return send_from_directory(absolut_dir_path, path)

        # Return the IGV component with the selected genome.
        @self.app.callback(
            Output('default-igv-container', 'children'),
            Input('Gen-select', 'value')
        )
        def return_igv(genome):
            return html.Div([
                dash_bio.Igv(
                    id='locus-igv',
                    locus=iclip.get_locus(genome),
                    reference=dict(
                        id="A.thaliana (TAIR 10)",
                        name="A. thaliana (TAIR 10)",
                        fastaURL="tracks/TAIR10_chr_all_noYWMKSRD.fa",
                        indexURL="https://s3.amazonaws.com/igv.org.genomes/tair10/TAIR10_chr_all.fas.fai",
                        aliasURL="https://s3.amazonaws.com/igv.org.genomes/tair10/TAIR10_alias.tab",
                        tracks=iclip.set_reference()
                    )
                )])

        """@self.app.callback(
            Output('Gen-select', 'options'),
            Input('File-Select', 'value')
        )
        def return_gene_selection(gene):
            iclip.set_selected_file(gene)
            newopt = self.iclip.get_current_gene_dict()
            return newopt"""

        @self.app.callback(
            Output('descDiv', 'children'),
            Input('example-dropdown', 'value')
        )
        def get_gene_annotation(name):
            return 'You have selected "{}"'.format(name)

        self.runapp()  # start the app

    def runapp(self):
        self.app.layout = self.get_layout()
        # this is needed, if callbacks are also called in other files
        self.app.config.suppress_callback_exceptions = True
        self.app.run_server(debug=True, port=8888)

    def clustergram(self):
        """return html.Div([html.Div([
            dcc.Dropdown(
                id="File-Select",
                options=self.file_option,
                value=self.file_option[0]['value']
            ),
            html.Div(id='igv-container')
        ]),"""
        return html.Div([
            # dcc.Loading(id='igv-container'),
            dcc.Dropdown(
                id='Gen-select',
                options=self.current_gene_options,
                placeholder='Select a gene...'
            ),
            dcc.Loading(id='default-igv-container'),
            html.Div(id='select-gen'),
            html.Hr(),
        ])

    @staticmethod
    def dropdown():
        """This method provides the options for SEQing2"""
        item = [{'label': 'IClip', 'value': 'NULL'},
                {'label': 'RNA-Seq', 'value': 'NULL'},
                {'label': 'Settings', 'value': 'NULL'}]
        return html.Div([
            dcc.Dropdown(
                id='example-dropdown',
                options=item,
                value='IClip'
            ),
            html.Div(id='descDiv')
        ])

    def get_layout(self):
        return html.Div(children=[self.clustergram()])
