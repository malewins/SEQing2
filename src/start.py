#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pathlib

from app import app
from components import ComponentHandler
from input_files import ARGS, FilesHandler


def __start_application(args):
    handler = FilesHandler.FileHandler(args)
    component_handler = ComponentHandler.Component(handler)
    app.AppHandler(pathlib.Path.absolute(args.get_absolut_path('dir')), component_handler, args.get_port())


if __name__ == '__main__':
    """Start the application via console"""
    arguments = ARGS.Args()
    __start_application(arguments)
