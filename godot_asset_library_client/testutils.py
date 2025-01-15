# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from contextlib import contextmanager, ExitStack
import os
from pathlib import Path

# Polyfill for Python<3.11
def enterContext(self, resource):
    """ 
    Polyfill for unittest.TestCase.enterContext introduced in Python 3.11.
    
    It opens the context handler in setUp that will be exited on teardown
    even if errors occur.
    
    class MyTestClass(unittest.TestCase):
    
        from somutils.testutils import enterContext

        def setUp(self):
            self.sandbox = self.enterContext(sandbox_dir())
        
    """
    with ExitStack() as stack:
        handler = stack.enter_context(resource)
        self.addCleanup(stack.pop_all().close)
        return handler

from unittest import TestCase
if not hasattr(TestCase, 'enterContext'):
    TestCase.enterContext = enterContext


@contextmanager
def temp_path():
    """
    Context manager that creates a temporary dir and ensures
    that all the content is removed after the with scope
    Returns the pathlib Path of the created dir.

    >>> with temp_path() as tmp:
    ...     mypath = tmp / 'myfile'
    ...     nbytes = mypath.write_text('hello world', encoding='utf8')
    ...     # TODO: remove the str bellow when Py2 dropped
    ...     str(mypath.read_text(encoding='utf8')) # returns "hello world"
    ...     assert mypath.exists(), "Should exists at this point"
    'hello world'

    >>> assert not mypath.exists(), "Sould not exist at this point"

    It will clean up even after raising an exception

    >>> with temp_path() as tmp:
    ...     mypath = tmp / 'myfile'
    ...     nbytes = mypath.write_text('hello world', encoding='utf8')
    ...     assert mypath.exists(), "Should exists at this point"
    ...     raise Exception("This will interrupt the code")
    Traceback (most recent call last):
        ...
    Exception: This will interrupt the code

    >>> assert not mypath.exists(), "Sould not exist at this point"
    """

    import shutil
    import tempfile

    path = Path(tempfile.mkdtemp())
    shutil.rmtree(str(path), ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(str(path), ignore_errors=True)

@contextmanager
def working_dir(path):
    """
    Context manager that changes the current working dir
    and restores it after executing the 'with' block.

    >>> oldwd = os.getcwd()
    >>> with working_dir('/') as path:
    ...     assert os.getcwd() == '/'
    ...     assert str(path) == '/'
    >>> assert os.getcwd() == oldwd

    Even if an exception is thrown:

    >>> with working_dir('/'):
    ...     raise Exception("Agh")
    Traceback (most recent call last):
        ...
    Exception: Agh
    >>> assert os.getcwd() == oldwd
    """

    olddir = os.getcwd()
    os.chdir(str(path))
    try:
        yield Path(path)
    finally:
        os.chdir(olddir)

@contextmanager
def sandbox_dir():
    """
    Context manager that combines temp_path and working_dir.
    It creates a temporary dir and moves to it.
    After the 'with' block is executed, even if an exception is thrown,
    the temporary directory and its content is removed
    and the previous working directory is restored.

    >>> oldwd = os.getcwd()
    >>> with sandbox_dir() as temp:
    ...     assert os.getcwd() == str(temp)
    ...     assert Path('file').write_text('content')
    ...     assert (temp/'file').exists()
    >>> assert os.getcwd() == oldwd
    >>> assert not temp.exists()

    Even if an exception is thrown:

    >>> with sandbox_dir():
    ...     raise Exception("Agh")
    Traceback (most recent call last):
        ...
    Exception: Agh
    >>> assert os.getcwd() == oldwd
    >>> assert not temp.exists()
    """

    with temp_path() as path:
        with working_dir(path):
            yield path


# vim: ts=4 sw=4 et
