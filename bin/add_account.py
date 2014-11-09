#!/usr/local/bin/python2.6
# -*- coding: utf-8 -*-
from __future__ import print_function, division

import sys
import MySQLdb

def showhelp():
    print("Usage: $0 user account")

def add_account(user, title):
    conn = MySQLdb.connect(read_default_file='/var/www/accounts/conf/my.cnf', read_default_group="mysql")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE name = %s", (user, ))
    data = cursor.fetchall()
    count = len(data)
    if count == 0:
        print("user {0} not exist.".format(user))
        return False
    else:
        user_id = data[0][0]
        cursor.execute("SELECT * FROM account WHERE user_id = %s AND title = %s", (user_id, title))
        count = len(cursor.fetchall())
        if count > 0:
            print("account {0} already exist.".format(title))
            return False
        else:
            cursor.execute("""INSERT INTO account(user_id, title, delete_flag) VALUES(%s, %s, 0)""", (user_id, title))
            conn.commit()
            cursor.close()
            print("successful.")
            return True

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        showhelp()
    else:
        user = sys.argv[1]
        title = sys.argv[2]
        if add_account(user, title):
            exit(0)
    exit(1)

