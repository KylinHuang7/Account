#!/usr/local/bin/python2.6
# -*- coding: utf-8 -*-
from __future__ import print_function, division

import sys
import getpass
import MySQLdb

def showhelp():
    print("Usage: $0 username familyid settle_day")

def create_user(username, familyid, settle_day):
    conn = MySQLdb.connect(read_default_file='/var/www/accounts/conf/my.cnf', read_default_group="mysql")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE name = %s", (username, ))
    count = len(cursor.fetchall())
    if settle_day > 28:
        print("settle_day cannot greater than 28.")
        return False
    if count > 0:
        print("user {0} already exist.".format(username))
        return False
    else:
        pass1 = getpass.getpass("Please input password:")
        pass2 = getpass.getpass("Please repeat password:")
        if pass1 != pass2:
            print("password input error.")
            return False
        cursor.execute("""INSERT INTO user(name, pass, family_id, last_login, settle_day) VALUES(%s, UNHEX(SHA1(%s)), %s, "2010-01-01 00:00:00", %s)""", 
            (username, pass1, familyid, settle_day))
        conn.commit()
        cursor.close()
        print("successful.")
        return True

if __name__ == '__main__':
    if (len(sys.argv) != 4):
        showhelp()
    else:
        username = sys.argv[1]
        familyid = sys.argv[2]
        settle_day = sys.argv[3]
        if create_user(username, familyid, settle_day):
            exit(0)
    exit(1)

