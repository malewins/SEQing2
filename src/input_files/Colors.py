from enum import Enum


class Color(Enum):
    """Enum for specific colors to display for the user."""
    BLUE_RGB = 'rgb(0, 143, 255)'
    BLUE_HTML = '#008FFF'
    WHITE_RGB = 'rgb(242, 245, 244)'
    WHITE_HTML = '#F2F5F4'
    BLACK_RGB = 'rgb(22, 22, 24)'
    BLACK_HTML = '#161618'
    YELLOW_RGB = 'rgb(191, 188, 6)'
    YELLOW_HTML = '#BFBC06'
    ORANGE_RGB = 'rgb(238, 77, 46)'
    ORANGE_HTML = '#EE4D2E'
    GREEN_RGB = 'rgb(29, 185, 146)'
    GREEN_HTML = '#1DB992'
    NONE = ''
