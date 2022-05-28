#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pathlib
import sys

from src.app import app
from src.components import ComponentHandler
from src.input_files import ARGS, FilesHandler


def __start_application(args):
    if args.has_option('dir'):
        handler = FilesHandler.FileHandler(args)
        component_handler = ComponentHandler.Component(handler)
        app.AppHandler(pathlib.Path.absolute(args.get_absolut_path('dir')), component_handler, args.get_port())
    else:
        sys.stderr.write('error: No Argument was set.')
        args.parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    """Start the application via console"""
    arguments = ARGS.Args()
    __start_application(arguments)
