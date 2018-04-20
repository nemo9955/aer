from __future__ import division, print_function

import copy
import os
import urllib
from os.path import join as pjoin
from string import Formatter

from fabric.api import env, lcd, local, prompt, quiet

# pylint: disable=I0011,E1129


def elements_contain(the_list, the_elements, decide_function=all):
    ok_list = []
    for i_ in the_list:
        has_list = (str(ele_) in str(i_) for ele_ in the_elements)
        if decide_function(has_list):
            ok_list.append(i_)
    return ok_list


def elements_endswith(the_list, the_elements):
    ok_list = []
    for i_ in the_list:
        has_list = (str(i_).endswith(str(ele_)) for ele_ in the_elements)
        if any(has_list):
            ok_list.append(i_)
    return ok_list


def all_subfiles(root_folder, remove_root_str=False):
    file_list = []
    for root_, dir_, files_ in os.walk(root_folder):
        for file_ in files_:
            full_path = pjoin(root_, file_)
            if remove_root_str:
                file_list.append(full_path[len(root_folder) + 1:])
            else:
                file_list.append(full_path)
    return file_list


def all_subdirs(root_folder):
    dir_list = []
    for root_, dir_, files_ in os.walk(root_folder):
        dir_list.append(root_)
    return dir_list


def pick_valid(options):
    return lambda v: options[int(v)]


def pick_from_list(options):
    """
    Prompts the user to pick one element from a presented list
    """

    if options is None or len(options) == 0:
        return None

    options = list(options)

    if len(options) == 1:
        return options[0]

    prefix_ = os.path.commonprefix(options)
    for index_, option_ in enumerate(options):
        pr_len = len(prefix_)
        cut_prefix = option_ != prefix_ and pr_len > 20
        element_str = option_[pr_len:] if cut_prefix else option_
        print("->", str(index_) + ".", element_str)

    picked = prompt("Select option\'s index:", validate=int)
    # picked = prompt("Select option\'s index:", validate=pick_valid(options))
    return options[picked]


class EasyDictValidator(object):
    """
        Utility class for EasyDict so it can check if a variable exists using
        EasyDict({}).has.SOME_KEY
    """

    def __init__(self, easy_dict):
        self.easy_dict = easy_dict

    def __getattr__(self, key):
        return self.easy_dict.get(key, None) is not None

    def __getitem__(self, key):
        return self.easy_dict.get(key, None) is not None


class _RecursiveFormatterClass_(Formatter):
    """
    from https://gist.github.com/wickman/26f09ae6f551d12e4249
    """

    def _contains_underformatted_field_names(self, format_tuple):
        literal_text, field_name, format_spec, conversion = format_tuple
        if field_name is not None:
            return any(component[1] is not None for component in self.parse(field_name))
        return False

    def _split_format_tuple(self, format_tuple):
        literal_text, field_name, format_spec, conversion = format_tuple

        yield (literal_text + '{', None, None, None)

        for format_tuple in self.parse(field_name):
            yield format_tuple

        literal_text = ''.join([
            '' if not conversion else ('!' + conversion),
            '' if not format_spec else (':' + format_spec),
            '}'])

        yield (literal_text, None, None, None)

    def parse(self, format_string):
        def iter_tuples():
            for format_tuple in super(_RecursiveFormatterClass_, self).parse(format_string):
                if not self._contains_underformatted_field_names(format_tuple):
                    yield format_tuple
                else:
                    for subtuple in self._split_format_tuple(format_tuple):
                        yield subtuple
        return list(iter_tuples())

    def vformat(self, format_string, args, kwargs):
        while True:
            # print( "---- ",format_string)
            format_string = super(_RecursiveFormatterClass_, self).vformat(
                format_string, args, kwargs)

            # if any field_names remain uninterpolated
            if any(format_tuple[1] is not None for format_tuple in self.parse(format_string)):
                continue
            else:
                return format_string


class EasyDict(dict):
    """
    Dictionary subclass enabling attribute lookup/assignment of keys/values.

    For example::

        >>> m = EasyDict({'foo': 'bar'})
        >>> m.foo
        'bar'
        >>> m.has.foo
        True
        >>> m.has.not_here
        False
        >>> m.foo = 'not bar'
        >>> m['foo']
        'not bar'

    ``EasyDict`` objects also provide ``.first()`` which acts like
    ``.get()`` but accepts multiple keys as arguments, and returns the value of
    the first hit, e.g.::

        >>> m = EasyDict({'foo': 'bar', 'biz': 'baz'})
        >>> m.first('wrong', 'incorrect', 'foo', 'biz')
        'bar'

    """

    def __getattr__(self, key):
        if key == "has":
            return EasyDictValidator(self)

        try:
            return self[key]
        except KeyError:
            # to conform with __getattr__ spec
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if key == "has":
            print(red('"has" is a reserved EasyDict word'))
            return
        self[key] = value

    def format(self, str_, *args):
        args_ = []

        for arg in args:
            # print( arg)
            args_.append(arg)
            # if isinstance(arg, (list, tuple)):
            #     args_.append(arg)
            # if isinstance(arg, dict):
            #     kwargs_.append(arg)
        return _RecursiveFormatterClass_().format(str_, *args_, **self)


class RecursiveFormatter():
    """
    piece = EasyDict()

    other = EasyDict()
    other.fa = "OTTT"

    piece.fir = "fir"
    piece.sec = ("zero","f:{fir}:{fir}",200,3000,111111)
    piece.out = " YYYYY "
    piece.pri = "{fir} {sec[1]}"
    piece.base = "{pri}"
    piece.out = " YYYYY "
    piece.com = "{base} {out}"

    cmd = RecursiveFormatter(piece,piece.sec,other)
    print( cmd.com)

    piece.fir = "!!! {fa}"
    print( cmd.com)

    piece.fir = "{sec[4]}"
    print( cmd.com)

    # piece.sec[3] = "tri"
    piece.fir = "{0} {2} {2} {2}"
    # piece.fir = "{0} {3}"
    other.fa = "BBBAA"
    piece.fir = "!!! {fa}"
    print( cmd.com)
    """

    def __init__(self, *args):
        self._args_ = []
        self._kwargs_ = []

        for arg in args:
            if isinstance(arg, (list, tuple)):
                self._args_.append(arg)
            if isinstance(arg, dict):
                self._kwargs_.append(arg)

        assert len(self._kwargs_) > 0, "Must have at least one dict as parameter"
        # assert isinstance(self._args_, (list,tuple)) , "_args_ must have the baseclass list or tuple , _args_ type is {}".format(type(self._args_))
        # assert isinstance(self._kwargs_, dict) , "_kwargs_ must have the baseclass dict, _kwargs_ type is {}".format(type(self._kwargs_))

    def raw_(self, raw_str):
        tl = []
        td = {}
        for it_ in self._args_:
            tl.extend(it_)
        for it_ in self._kwargs_:
            td.update(it_)
        return _RecursiveFormatterClass_().format(raw_str, *tl, **td)

    def __getattr__(self, key):
        tl = []
        td = {}
        for it_ in self._args_:
            tl.extend(it_)
        for it_ in self._kwargs_:
            td.update(it_)

        assert key in td, "No such key '{}' in _kwargs_ {} ".format(key, td)
        return _RecursiveFormatterClass_().format(td[key], *tl, **td)
