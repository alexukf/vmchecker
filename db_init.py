#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from vmchecker import backend

if __name__ == '__main__':
    db = backend.get_db()
    db.initialize()

