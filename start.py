#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pathlib

import app
from components import iclip
import files.FilesHandler
from files import ARGS


def __check_args(args):
    if args.has_option('dir'):
        handler = files.FilesHandler.FileHandler(args.get_directory())
        iclip_handler = iclip.IClipHandler(handler)
        app.AppHandler(pathlib.Path.absolute(args.get_directory()), iclip_handler)
    # TODO: further argument check


if __name__ == '__main__':
    """Start the application via console"""
    arguments = ARGS.Args()
    __check_args(arguments)
