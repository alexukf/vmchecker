#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialises the directory path for one course"""

from __future__ import with_statement

import os
import sqlite3
import sys
import logging
import string
import pkg_resources
from subprocess import check_call, CalledProcessError

from vmchecker import paths
from vmchecker import config


_logger = logging.getLogger("vmchecker.initialise_course")


def _install_example_config_file(default_root_path, default_repo_path, default_config_path):
    """Install an example config file to a file named 'config' in the current directory

    Initalize some config file variables to point to the location of:
        root = the root of a course's data -- the current directory
        repo = a subdir in the current directory where the git repo will be stored
    """

    # get the data from the package-provided example config template.
    template_data = ""
    with pkg_resources.resource_stream('vmchecker', 'examples/config-template') as template:
        template_data = template.read()

    # the example is a template that contains some '$var' variables.
    s = string.Template(template_data)

    # replace the $vars with these values and write the result in the destination file
    with open(default_config_path, 'w') as handle:
        handle.write(s.substitute(root=default_root_path, repo=default_repo_path))



def _install_if_needed_example_config_file(default_root_path, default_repo_path, default_config_path):
    if not os.path.exists(default_config_path):
        _install_example_config_file(default_root_path, default_repo_path, default_config_path)
        print(('A new default vmchecker configuration file was written to %s. ' +
               'Please update it before running any vmchecker code.') % default_config_path)
    else:
        print(('Configuration file %s exists. This script will not change it.') %  default_config_path)

def _mkdir_if_not_exist(path):
    """Make the path if it does not exist"""
    if not(os.path.isdir(path)):
        os.mkdir(path)
    else:
        _logger.info('Skipping existing directory %s' % path)


def _create_paths(paths):
    """ Create all paths in the received 'paths' parameter"""
    for path in paths:
        _mkdir_if_not_exist(path)


def create_tester_paths(vmpaths):
    """Create all paths used by vmchecker on the storer machine"""
    _create_paths(vmpaths.tester_paths())


def create_storer_paths(vmpaths):
    """Create all paths used by vmchecker on the storer machine"""
    _create_paths(vmpaths.storer_paths())


def create_storer_git_repo(vmpaths):
    """Creates the repo for the assignments on the storer."""
    # first make teh destination directory
    rel_repo_path = vmpaths.dir_repository()
    abs_repo_path = vmpaths.abspath(rel_repo_path)
    _mkdir_if_not_exist(abs_repo_path)

    # then, if missing, initialize a git repo in it.
    repo_path_git = os.path.join(abs_repo_path, '.git')
    if not(os.path.isdir(repo_path_git)):
        # no git repo found in the dir.
        try:
            env = os.environ
            env['GIT_DIR'] = repo_path_git
            check_call(['git', 'init'], env=env)
        except CalledProcessError:
            logging.error('cannot create git repo in %s' % repo_path_git)


def create_db_tables(db_path):
    """Create a sqlite db file în db_path for grade management."""
    db_conn = sqlite3.connect(db_path)
    db_cursor = db_conn.cursor()
    db_cursor.executescript("""
    CREATE TABLE assignments (
        id INTEGER PRIMARY KEY,
        name TEXT);
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT);
    CREATE TABLE grades (
        assignment_id INTEGER,
        user_id INTEGER,
        grade TEXT,
        mtime TIMESTAMP NOT NULL,
        PRIMARY KEY(assignment_id, user_id));
    """)
    db_cursor.close()
    db_conn.close()


def create_db(vmpaths):
    """Create the implicit db if it does not exist."""
    # check for DB existance
    db_file = vmpaths.db_file()
    if not os.path.isfile(db_file):
        create_db_tables(db_file)
    else:
        _logger.info('Skipping existing Sqlite3 DB file %s' % db_file)


def main_storer(default_root_path = ""):
    """Run initialization tasks for the storer machine."""
    if default_root_path == "":
        vmcfg = config.config_storer()
        vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    else:
        vmpaths = paths.VmcheckerPaths(default_root_path)
    create_storer_paths(vmpaths)
    create_storer_git_repo(vmpaths)
    create_db(vmpaths)
    _logger.info(' -- storer init done setting up paths and db file.')


def main_tester(default_root_path = ""):
    """Run initialization tasks for the tester machine."""
    if default_root_path == "":
        vmcfg = config.config_tester()
        vmpaths = paths.VmcheckerPaths(vmcfg.root_path())
    else:
        vmpaths = paths.VmcheckerPaths(default_root_path)
    _logger.info(' -- tester init done setting up paths and db file.')


def usage():
    """Print usage for this program."""
    print("""Usage:
\t%s storer - initialize storer machine
\t%s tester - initialize tester machine
\t%s --help - print this message"""% (sys.argv[0], sys.argv[0], sys.argv[0]))


def main():
    """Initialize course based on sys.argv."""
    logging.basicConfig(level=logging.DEBUG)
    config.parse_arguments()

    default_root_path = os.getcwd()
    default_repo_path = os.path.join(default_root_path, 'repo')
    default_config_path = os.path.join(default_root_path, 'config')
    if (len(sys.argv) < 2):
        usage()
        exit(1)
    if cmp(sys.argv[1], 'storer') == 0:
        _install_if_needed_example_config_file(default_root_path, default_repo_path, default_config_path)
        main_storer(default_root_path)
    elif cmp(sys.argv[1], 'tester') == 0:
        _install_if_needed_example_config_file(default_root_path, default_repo_path, default_config_path)
        main_tester(default_root_path)
    elif cmp(sys.argv[1], '--help') == 0:
        usage()
    else:
        usage()
        exit(1)

if __name__ == '__main__':
    main()
