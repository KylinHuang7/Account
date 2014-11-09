#!/usr/local/bin/python2.6
# -*- coding: utf-8 -*-
from __future__ import print_function, division

import os
import datetime

def do_backup(backupname):
    os.system("/usr/local/bin/mysqldump --defaults-file=/var/www/accounts/conf/my.cnf --databases accounts > '/home/backup/accounts/{0}'".format(backupname))
    return True

def rm_backup(backupname):
    os.system("/bin/rm -f '/home/backup/accounts/{0}'".format(backupname))
    return True

today = datetime.datetime.today()
yesterday = today - datetime.timedelta(days=1)
weekBackup = False

if today.isoweekday() == 5:
    weekBackup = True
    lastweek = today - datetime.timedelta(days=8)
succ = do_backup("bak_acc_" + today.strftime("%Y%m%d"))
if succ:
    if weekBackup:
        rm_backup("bak_acc_" + lastweek.strftime("%Y%m%d"))
    else:
        rm_backup("bak_acc_" + yesterday.strftime("%Y%m%d"))

