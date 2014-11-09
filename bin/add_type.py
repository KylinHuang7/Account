#!/usr/local/bin/python2.6
# -*- coding: utf-8 -*-
from __future__ import print_function, division

import sys
import MySQLdb

def showhelp():
    print("Usage: $0 type")

def add_type(title):
    conn = MySQLdb.connect(read_default_file='/var/www/accounts/conf/my.cnf', read_default_group="mysql")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM type WHERE title = %s", (title, ))
    count = len(cursor.fetchall())
    if count > 0:
        print("type {0} already exist.".format(title))
        return False
    else:
        cursor.execute("""INSERT INTO type(title) VALUES(%s)""", (title, ))
        conn.commit()
        cursor.close()
        print("successful.")
        return True

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        showhelp()
    else:
        title = sys.argv[1]
        if add_type(title):
            exit(0)
    exit(1)

