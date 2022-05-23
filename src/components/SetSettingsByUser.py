from pathlib import Path

from dash import dcc, html, Input, Output

from src.input_files import File
from src.app.AppInterface import app
import base64

"""This File provides settings to display the specific data and not all data at once. This has a performance reason."""
Line = {'textAlign': 'left', 'height': '5px', 'width': '1500px', 'backgroundColor': '#161618'}
center = {'textAlign': 'center'}


class Settings:
    """
    This class displays the settings on the webpage.

    :param component_handler: to interact with the filehandler.
    """

    def __init__(self, component_handler):
        self.handler = component_handler
        self.annotations = component_handler.get_annotations()
        self.sequencing = component_handler.get_sequencing_files()
        self.genome = component_handler.get_genome()
        self.expression = component_handler.get_expression_files()
        self.descriptions = component_handler.get_description_files()
        self.set_sequence = False

        @app.callback(
            Output('choose-annotation', 'children'),
            Input('annotation', 'value'))
        def set_and_display_annotation_file(value):
            """Set the chosen annotation input_files.
            Displays for the user the selected."""
            component_handler.set_annotation_file(value)
            return f'You have selected {value}'

        @app.callback(
            Output('choose-descAnnotation', 'children'),
            Input('desc', 'value'),
            Input('descAnnotation', 'value'))
        def set_gene_description(description, annotation):
            component_handler.set_description_files([description, annotation])
            return f'You have selected {description, annotation}'

        @app.callback(
            Output('sequence', 'children'),
            Input('data', 'value'))
        def set_and_display_chosen_file(value):
            """Set the sequence input_files.
            Displays for the user the selected input_files."""
            component_handler.set_sequence_file(value)
            if value is not None:
                self.set_sequence = True
                self.__is_set_sequence()
            return f'You have selected {value}'

        @app.callback(
            Output('expression-chooser', 'children'),
            Input('expression', 'value'))
        def set_and_display_expression_file(value):
            """Set the expression input_files.
            Displays for the user the selected input_files."""
            component_handler.set_expression_file(value)
            return f'You have selected {value}'

        @app.callback(
            Output('genome-chooser', 'children'),
            Input('genome', 'value'))
        def set_and_display_genome(value):
            """Set the genome file.
            Displays for the user the selected file."""
            component_handler.set_genome(value)
            return f'You selected as genome {value}'

        @app.callback(
            Output('output-danger', 'children'),
            Input('confirm-danger', 'submit_n_clicks'))
        def update_output(submit_n_clicks):
            """Check's if the user has selected a sequence file.
            If not, it pops up a warning message."""
            # Button has to be set here to confirm that the genome was set
            # click was not reset, that's why it shows up
            if submit_n_clicks:
                return dcc.Location(id='between-venus-and-mars', href='/page1', refresh=True)

    @staticmethod
    def __get_img():
        image_filename = Path('SEQing.png').resolve()  # current place of image
        encoded_image = base64.b64encode(open(image_filename, 'rb').read())
        return html.Div(style={'textAlign': 'center'}, children=[
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                     style={'width': '350px', 'height': '100px'})])

    def __get_annotations(self):
        if len(self.annotations) >= 2:
            return 'Annotation-input_files'
        return 'Annotation-file'

    def __get_annotation_file_options(self):
        label = self.__get_annotations()
        return html.Div([
            html.Div(children=[
                html.Hr(style=Line),
                html.H2(label, style=center),
                dcc.Checklist(
                    options={f'{i}': f'{i}' for i in self.annotations},
                    id='annotation'
                ),
                html.Div(id='choose-annotation')],
                style={'display': 'column'})
        ])

    def __get_annotation_gene_options(self):
        if self.handler.dict_is_not_set():
            return html.Div([
                html.Div(children=[
                    html.Hr(style=Line),
                    html.H2('Choose annotation-file and a description-file', style=center),
                    dcc.RadioItems(
                        options={f'{i}': f'{i}' for i in self.descriptions},
                        value=self.descriptions[0],
                        id='desc'
                    ),
                    dcc.Dropdown(
                        options={f'{i}': f'{i}' for i in self.annotations},
                        value=self.annotations[0],
                        id='descAnnotation'
                    ),
                    html.Div(id='choose-descAnnotation')
                ])
            ])
        return ""

    def __get_sequencing_annotation(self):
        if len(self.sequencing) >= 2:
            return 'Data-input_files'
        return 'Data-file'

    def __get_display_sequence_options(self):
        label = self.__get_sequencing_annotation()
        return html.Div([
            html.Div(children=[
                html.Hr(style=Line),
                html.H2(label, style=center),
                dcc.Checklist(options={f'{i}': f'{i}' for i in self.sequencing},
                              id='data'),
                html.Div(id='sequence')
            ])])

    def __get_genome_options(self):
        if not self.genome:
            raise NameError('There was no FASTA-File found.')
        if type(self.genome) is File.FileInput:
            return html.Div([
                html.Div(children=[
                    html.Hr(style=Line),
                    html.H1('The genome is ' + self.genome.get_filename(),
                            style={'color': '#1db992', 'textAlign': 'center'})
                ])
            ])
        if len(self.genome) == 1:
            self.genome = self.genome[0]
            return html.Div([
                html.Div(children=[
                    html.Hr(style=Line),
                    html.H1('The genome is ' + self.genome.get_filename(),
                            style={'color': '#1db992', 'textAlign': 'center'})
                ])
            ])
        return html.Div([
            html.Div(children=[
                html.Hr(style=Line),
                html.H2('Genome-input_files', style={'textAlign': 'center'}),
                dcc.RadioItems(options={f'{i.get_filename()}': f'{i.get_filename()}' for i in self.genome},
                               value=self.genome[0].get_filename(),  # Set first value
                               id='genome'),
                html.Div(id='genome-chooser')
            ])
        ])

    def __get_expression_label(self):
        if not self.expression:
            return 'Nothing here'
        if len(self.expression) > 1:
            return 'Expression-input_files'
        return 'Expression-file'

    def __get_display_expression_options(self):
        label = self.__get_expression_label()
        if self.expression:
            return html.Div([html.Hr(style=Line),
                             html.H2(label, style=center),
                             dcc.RadioItems(options={f'{i}': f'{i}' for i in self.expression},
                                            id='expression'),
                             html.Div(id='expression-chooser')])
        return ""

    def __get_button_interaction(self):
        if self.__is_set_sequence():
            return html.Div([
                dcc.ConfirmDialogProvider(
                    children=html.Button('Submit', n_clicks=0),
                    id='confirm-danger',
                    message='No Data-File is chosen!\n '
                            'Sure you want to continue?'),
                html.Div(id='output-danger')
            ], style=center)
        else:
            return html.Div([
                dcc.Link(html.Button('Submit', id='submit-val', n_clicks=0), href='/page1'),
            ], style={'textAlign': 'center'})

    def get_layout_for_settings(self):
        """
        Return the layout of the settings from which the user can choose its input_files.

        :return: Layout of Settings
        :rtype: html
        """
        return html.Div(children=[
            self.__get_img(),
            html.H2('Select Files to display:'),
            html.Div(style={'textAlign': 'left', 'display': 'block', 'flex-direction': 'column'}, children=[
                self.__get_genome_options(),
                self.__get_annotation_file_options(),
                self.__get_annotation_gene_options(),
                self.__get_display_sequence_options(),
                self.__get_display_expression_options(),
                self.__get_button_interaction()
            ])])

    def __is_set_sequence(self):
        if self.set_sequence:
            return True
        return False
