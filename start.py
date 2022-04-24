#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pathlib

import app
from components import ComponentHandler
import files.FilesHandler as fileHandler
from files import ARGS


def __start_application(args):
    handler = fileHandler.FileHandler(args)
    component_handler = ComponentHandler.Component(handler)
    app.AppHandler(pathlib.Path.absolute(args.get_absolut_path()), component_handler, args.get_port())


if __name__ == '__main__':
    """Start the application via console"""
    arguments = ARGS.Args()
    __start_application(arguments)
