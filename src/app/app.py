# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser, if not set the port to a different location.

from dash.dependencies import Input, Output
from dash import dcc
from dash import html
# Static Default style
from flask import send_from_directory
from src.components import DisplayData, SetSettingsByUser
from src.app.AppInterface import app, server
from src.input_files.Colors import Color
from dash_auth import BasicAuth


class AppHandler:
    """
    App handler, which handles the app.

    :param absolut_dir_path: takes an absolut path to a directory.
    :param component_handler: need the component handler to interact with the filehandler.
    :param port: takes a port as int.
    """

    def __init__(self, absolut_dir_path, component_handler, port, mode, pwd):
        self.current_gene_options = component_handler.get_current_gene_dict()
        self.port = port
        self.settings = SetSettingsByUser.Settings(component_handler)
        self.display = DisplayData.Display(component_handler)
        VALID_USERNAME_PASSWORD_PAIRS = {'user': pwd}
        auth = BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

        @server.route('/tracks/<path:path>')
        def data(path) -> server:
            """Evoke that the input_files are available via a server"""
            return send_from_directory(absolut_dir_path, path)

        @app.callback(Output('page-content', 'children'),
                      Input('url', 'pathname'))
        def display_page(pathname) -> html:
            """Handles the different pages to display."""
            if pathname == '/page1':
                return self.display.get_layout_for_display()
            else:
                return self.settings.get_layout_for_settings()

        self.runapp(mode)  # start the app

    def runapp(self, mode: bool):
        """This runs the app on the given Port"""
        app.layout = self.__get_layout(mode)
        # This is needed, because callbacks are also called in other input_files.
        app.config.suppress_callback_exceptions = True
        app.run_server(debug=False, port=self.port)

    @staticmethod
    def __pages() -> html.Div:
        """This method provides the pages"""
        return html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')])

    def __get_layout(self, mode: bool) -> html.Div:
        """
        Return the general layout for the webpage.

        :return: the different webpages
        :rtype; html
        """
        if mode:
            black_or_white = {'backgroundColor': Color.BLACK_HTML.value, 'color': Color.WHITE_HTML.value}
        else:
            black_or_white = {'backgroundColor': Color.WHITE_HTML.value, 'color': Color.BLACK_HTML.value}

        return html.Div(style=black_or_white,
                        children=[dcc.Loading(self.__pages(), type='circle')])
