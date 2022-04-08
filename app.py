# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash.dependencies import Input, Output
from dash import dcc
from dash import html
# Static Default style
from flask import send_from_directory
from components import DisplayData, SetSettingsByUser
from AppInterface import app, server

colors = {
    'background': '#f2f5f4',
    'text': '#008fff'
}


class AppHandler:
    """
    App handler, which handles the app
    @:param absolut_dir_path: takes an absolut path to a directory
    @:param iclip: need the iclip handler to interact with
    """

    def __init__(self, absolut_dir_path, component_handler, port):
        self.dir = absolut_dir_path
        self.current_gene_options = component_handler.get_current_gene_dict()
        self.annotations = component_handler.get_annotations()
        self.sequencing = component_handler.get_sequencing_files()
        self.port = port
        self.settings = SetSettingsByUser.Settings(component_handler,
                                                   self.annotations,
                                                   self.sequencing)
        self.display = DisplayData.Display(component_handler)

        @server.route('/tracks/<path:path>')
        def data(path):
            """Evoke that the files are available via a server"""
            return send_from_directory(absolut_dir_path, path)

        @app.callback(Output('page-content', 'children'),
                      Input('url', 'pathname'))
        def display_page(pathname):
            if pathname == '/page1':
                return self.display.layout()
            else:
                return self.settings.get_layout_for_settings()

        self.runapp()  # start the app

    def runapp(self):
        """This runs the app on the given Port"""
        app.layout = self.get_layout()
        # This is needed, because callbacks are also called in other files.
        app.config.suppress_callback_exceptions = True
        app.run_server(debug=True, port=self.port)

    @staticmethod
    def pages():
        """This method provides the pages"""
        return html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')])

    def get_layout(self):
        return html.Div(style={'backgroundColor': colors['background']}, children=[self.pages()])
