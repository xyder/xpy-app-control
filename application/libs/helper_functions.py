import inspect
import ntpath
import os
from flask.ext.restful import reqparse, fields
import signal
from sqlalchemy.sql import sqltypes


def file_from_path(fpath):
    """
    Extracts the file name from a path.

    Note: for full compatibility with Linux (which can have filenames with backslashes)
    the function would need to provide a special case for that, which it doesn't.

    :param fpath: the path

    :return: the file name
    """
    if not fpath:
        return ''
    head, tail = ntpath.split(fpath)
    return tail or ntpath.basename(head)


def str_to_bool(val):
    """
    Converts a string to the equivalent boolean value.
    """
    if val == 'true' or val == 'True' or val == 'TRUE':
        return True
    return False


def fields_dict_from_model(model):
    """
    Creates a dictionary matching the sql column types with the column names.
    """
    fields_list = {}
    # iterate over the columns
    for column in model.__table__.columns:
        ftype = fields.String
        if type(column.type) is sqltypes.Integer:
            ftype = fields.Integer
        elif type(column.type) is sqltypes.Boolean:
            ftype = fields.Boolean
        fields_list[column.name] = ftype
    return fields_list


def fields_str_from_keys(fields_list):
    """
    Converts a list of strings to a comma separated concatenated string.
    :param fields_list:
    :return:
    """
    ret = ''
    for field in fields_list:
        ret += field + ', '
    if len(ret) > 2:
        ret = ret[:-2]
    return ret


def parser_from_model(model):
    """
    Creates a request parser from the given sql columns model.
    """
    ret_parser = reqparse.RequestParser()
    for column in model.__table__.columns:
        ftype = str
        if type(column.type) is sqltypes.Integer:
            ftype = int
        elif type(column.type) is sqltypes.Boolean:
            ftype = str
        ret_parser.add_argument(column.name, type=ftype)
    return ret_parser


def terminate_process(pid):
    """
    Sends a SIGTERM signal to the process with the given process id.
    """
    os.kill(pid, signal.SIGTERM)


def str_to_pair(str_pair):
    """
    Converts a string to a (key, value) pair.
    :param str_pair:
    :return:
    """
    first_equal = str_pair.find('=')
    key = str_pair[0:first_equal]
    val = str_pair[first_equal + 1:len(str_pair)]
    return {key: val}


def get_command(file, args=None, in_prompt=False):
    """
    Builds a command line from the given arguments, appending it to a command prompt line if necessary.

    :param file: executable file for the command.

    :param args: arguments to be appended to the executable command.

    :param in_prompt: determines if command prompt would be used as a running environment.

    :return: the built command.
    """
    if file:
        ret = ''
        if in_prompt:
            ret += os.path.expandvars(r'start "" %WINDIR%\system32\cmd.exe /c ')
            ret += '"' + file + '"'
        else:
            ret += file
        ret += ((' ' + args) if args else '')
        return ret


def register_class_to_rpc(mod, mapper):
    """
    Maps the methods of a class. This is a rewrite of the add_module function from jsonrpc2 to include static methods.

    It handles bound and static methods, but not class methods.

    :param mod: the class to be mapped.

    :param mapper: the jsonrpc mapper.
    """
    name = mod.__name__
    functions = inspect.getmembers(mod, predicate=inspect.isfunction)
    for key, value in ((key, value) for key, value in functions if not key.startswith('_') and callable(value)):
        mapper[name + '.' + key] = value