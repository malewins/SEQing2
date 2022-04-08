from dash import dcc, html, Input, Output

import files.File
from AppInterface import app
import base64

"""This File provides settings to display the specific data and not all data at once. This has a performance reason."""
Line = {'textAlign': 'left', 'height': '15px', 'width': '3000px', 'backgroundColor': '#161618'}


class Settings:

    def __init__(self, file_options, component_handler, annotations,
                 sequencing):
        self.file_options = file_options
        self.handler = component_handler
        self.annotations = annotations
        self.sequencing = sequencing
        self.genome = component_handler.get_genome()
        self.set_sequence = False

        @app.callback(
            Output('choose-annotation', 'children'),
            Input('annotation', 'value'))
        def display_value(value):
            component_handler.set_annotation_file(value)
            return f'You have selected {value}'

        @app.callback(
            Output('sequence', 'children'),
            Input('data', 'value'))
        def set_and_display_chosen_file(value):
            component_handler.set_sequence_file(value)
            if value is not None:
                self.set_sequence = True
                self.__is_set_sequence()
            return f'You have selected {value}'

        @app.callback(
            Output('expression-chooser', 'children'),
            Input('expression', 'value'))
        def set_and_display_expression_file(value):
            component_handler.set_expression_file(value)
            return f'You have selected {value}'

        @app.callback(
            Output('genome-chooser', 'children'),
            Input('genome', 'value'))
        def set_and_display_genome(value):
            component_handler.set_genome(value)
            return f'You selected as genome {value}'

        @app.callback(
            Output('output-danger', 'children'),
            Input('confirm-danger', 'submit_n_clicks'))
        def update_output(submit_n_clicks):
            # Button has to be set here to confirm that the genome was set
            if submit_n_clicks:
                return dcc.Location(id='between-venus-and-mars', href='/page1', refresh=True)

    @staticmethod
    def get_img():
        image_filename = 'Seqing.png'  # replace with your own image
        encoded_image = base64.b64encode(open(image_filename, 'rb').read())
        return html.Div(style={'textAlign': 'center'}, children=[
            html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                     style={'width': '350px', 'height': '100px'})])

    def get_annotations(self):
        if len(self.annotations) >= 2:
            return 'Annotation-files'
        return 'Annotation-file'

    def get_annotation_file_options(self):
        label = self.get_annotations()
        return html.Div([
            html.Div(children=[
                html.Hr(style=Line),
                html.H3(label),
                # TODO: Change to RaidoItem
                dcc.Checklist(
                    {f'{i}': f'{i}' for i in self.annotations},
                    id='annotation'
                ),
                html.Div(id='choose-annotation')],
                style={'display': 'column'})
        ])

    def get_sequencing_annotation(self):
        if len(self.sequencing) >= 2:
            return 'Data-files'
        return 'Data-file'

    def get_display_sequence_options(self):
        label = self.get_sequencing_annotation()
        return html.Div([
            html.Div(children=[
                html.Hr(style=Line),
                html.H3(label),
                dcc.Checklist({f'{i}': f'{i}' for i in self.sequencing},
                              id='data'),
                html.Div(id='sequence')
            ])])

    def get_genome_options(self):
        if not self.genome:
            raise NameError('There was no FASTA-File found.')
        if type(self.genome) is files.File.FileInput:
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
                html.H3('Genome-files'),
                dcc.RadioItems({f'{i.get_filename()}': f'{i.get_filename()}' for i in self.genome},
                               value=self.genome[0].get_filename(),
                               id='genome'),
                html.Div(id='genome-chooser')
            ])
        ])

    @staticmethod
    def get_display_expression_options():
        return html.Div([html.Hr(style=Line),
                         html.H3('Expression-file(s)'),
                         dcc.Checklist(['TSV', 'CSV'],
                                       id='expression'),
                         html.Div(id='expression-chooser')])

    def get_button_interaction(self):
        print('genome')
        print(self.__is_set_sequence())
        if self.__is_set_sequence():
            return html.Div([
                dcc.ConfirmDialogProvider(children=html.Button('Submit', n_clicks=0),
                                          id='confirm-danger',
                                          message='No Data-File is chosen!\n '
                                                  'Sure you want to continue?'),
                html.Div(id='output-danger')
            ])
        else:
            return html.Div([
                dcc.Link(html.Button('Submit', id='submit-val', n_clicks=0), href='/page1'),
            ])

    def get_layout_for_settings(self):
        return html.Div(children=[
            self.get_img(),
            html.H2('Select Files to display.'),
            html.Div(style={'textAlign': 'left', 'display': 'block', 'flex-direction': 'column'}, children=[
                self.get_genome_options(),
                self.get_annotation_file_options(),
                self.get_display_sequence_options(),
                self.get_display_expression_options(),
                self.get_button_interaction()
            ])])

    def __is_set_sequence(self):
        if self.set_sequence:
            return True
        return False
