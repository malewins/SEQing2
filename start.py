#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pathlib

import app
from components import ComponentHandler
import files.FilesHandler as fileHandler
from files import ARGS


def __check_args(args):
    port = args.get_port()
    if args.has_option('dir'):
        handler = fileHandler.FileHandler(args.get_directory())
        iclip_handler = ComponentHandler.Component(handler)
        app.AppHandler(pathlib.Path.absolute(args.get_directory()), iclip_handler, port)


if __name__ == '__main__':
    """Start the application via console"""
    arguments = ARGS.Args()
    __check_args(arguments)
