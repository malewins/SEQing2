from dash import dcc, html, Input, Output
import dash_bio

from dash.exceptions import PreventUpdate
from plotly import io as pio

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
        self.component_controller = component
        self.selected_files = component.get_selected_files()

        @app.callback(
            Output('igv', 'children'),
            Input('Gen-select', 'value'))
        def return_igv(value: str) -> html.Div:
            """Return the IGV component with the selected genome."""
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
        def update_output(value: str) -> str:
            if not value:
                raise PreventUpdate
            return 'The coordinate of the Gene is : \n{}'.format(value)

        @app.callback(
            Output('graph', 'children'),
            Input('Gen-select', 'value'))
        def update_graph(value: str) -> html.Div:
            if not value:
                raise PreventUpdate
            return html.Div(dcc.Graph(figure=self.component_controller.get_figure(value)), id='plot')

    def __get_dropdown_and_igv(self) -> html.Div:
        """
        This method provides the Gene-Selection.

        :return: the dropdown menu to choose a specific gene
        :rtype: html.Div
        """
        return html.Div([
            dcc.Dropdown(
                id='Gen-select',
                options=self.component_controller.get_current_gene_dict(),
                placeholder='Select a gene...',
                style={'color': Color.BLACK_RGB.value}
            ),
            dcc.Loading(id='igv'),
            html.Div(id='select-gen')
        ])

    def get_references(self) -> dict:
        """
        Return a dict as references for the igv-component.

        :return: reference dict
        :rtype: dict
        """

        return dict(id="A.thaliana (TAIR 10)",
                    name="A. thaliana (TAIR 10)",
                    fastaURL=self.component_controller.get_current_genome_file(),
                    indexURL=self.component_controller.get_current_index_file(),
                    tracks=self.component_controller.get_selected_files()
                    )

    @staticmethod
    def __gene_annotation_area() -> html.Div:
        """
        This method provides a section, where a gen description takes place.

        :return: location of a gene
        :rtype: html.Div
        """
        return html.Div(children=[
            html.Div(id='information-output')
        ])

    @staticmethod
    def __set_expression_graph() -> html.Div:
        """
        This method provides a section, where the expression graph takes place.
        :return: Expression-Graph layout
        :rtype: html.Div
        """
        return html.Div(children=[
            html.Hr(style=Line),
            html.H2('Expression-Graph', style=center),
            dcc.Loading(id='graph')
        ])

    def get_layout_for_display(self) -> html.Div:
        """
        Returns the layout of /page1.

        :return: html layout.
        :rtype: html.Div
        """
        return html.Div(children=[
            self.__gene_annotation_area(),
            self.__get_dropdown_and_igv(),
            self.__set_expression_graph()
        ])
