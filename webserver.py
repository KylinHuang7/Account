# -*- coding: utf-8 -*-
from __future__ import print_function, division

import datetime
import web

def start():
    global Render, DB, Session
    web.config.debug = False
    DB = web.database(dbn='mysql', read_default_file='/var/www/accounts/conf/my.cnf', read_default_group="mysql")
    urls = (
        '/bill(?:/(.*))?', 'Bill',
        '/claim(?:/(.*))?', 'Claim',
        '/summary(?:/(.*))?', 'Summary',
        '(?:/(.*))?', 'Index',
    )
    temp_global = globals()
    temp_global['__name__'] = 'webserver'
    app = web.application(urls, temp_global)
    del temp_global
    Session = web.session.Session(app, web.session.DiskStore('/var/www/accounts/session'))
    Render = web.template.render(
        "/var/www/accounts/template/",
        base='layout',
        globals = {'hasattr' : hasattr, 'session' : Session},
    )
    app.run()

class PageMixIn(object):
    def GET(self, op):
        """对某位置xxxx的GET请求一律调用get_xxxx进行响应"""
        self._domain_check()
        if isinstance(op, basestring):
            func = getattr(self, 'get_' + op, self.index)
        else:
            func = self.index
        return func()
    
    def POST(self, op):
        """对某位置xxxx的POST请求一律调用post_xxxx进行响应"""
        self._domain_check()
        if isinstance(op, basestring):
            func = getattr(self, 'post_' + op, self.index)
        else:
            func = self.index
        return func()
    
    def index(self):
        raise web.notfound()
    
    def _domain_check(self):
        if not (web.ctx.host and (web.ctx.host.startswith("accounts.kylinhome.") or web.ctx.host.startswith('127.0.0.1'))):
            raise web.notfound()

class AuthMixIn(object):
    def __init__(self):
        self.need_login()
    
    def need_login(self):
        if not hasattr(Session, 'login'):
            raise web.seeother('/')

class Index(PageMixIn):
    def index(self):
        logined = 0
        if hasattr(Session, 'login'):
            logined = 1
        return Render.welcome(logined, '')
    
    def post_login(self):
        params = web.input()
        username = params.username
        password = params.password
        users = DB.select('user', where='name = $username AND pass = UNHEX(SHA1($password))', vars={'username': username, 'password': password})
        try:
            user = users[0]
            Session['login'] = user.id
            Session['login_name'] = user.name
            Session['last_login'] = user.last_login
            Session['settle'] = user.settle_day
            today = datetime.date.today()
            if today.day < Session['settle']:
                if today.month == 1:
                    Session['month_start'] = datetime.date(today.year - 1, 12, Session['settle'])
                else:
                    Session['month_start'] = datetime.date(today.year, today.month - 1, Session['settle'])
            else:
                Session['month_start'] = datetime.date(today.year, today.month, Session['settle'])
            DB.update('user', where='name = $username', last_login=web.db.SQLLiteral('NOW()'), vars={'username': username})
            web.seeother('/')
        except IndexError:
            err = '登录失败'
            return Render.welcome(0, err)
    
    def get_logout(self):
        if hasattr(Session, 'login'):
            del(Session['login'])
            del(Session['login_name'])
            del(Session['last_login'])
            del(Session['settle'])
            del(Session['month_start'])
        web.seeother('/')

class Bill(PageMixIn, AuthMixIn):
    def get_add(self):
        params = web.input()
        if hasattr(params, "date_start"):
            sql = ""
            sql_params = {'user_id' : Session['login'], 'date_start' : params.date_start, 'date_end' : params.date_end}
            if params.claim_type != "":
                sql += " AND bill.claim_flag = $claim_type"
                sql_params["claim_type"] = params.claim_type
            if params.account_type != "":
                if params.account_type == "0":
                    sql += " AND bill.account_to_id = 0"
                elif params.account_type == "1":
                    sql += " AND bill.account_from_id = 0"
            month_bills = DB.query(
                """ SELECT bill.*, type.title as type_title, a_f.title as a_f_title, a_t.title as a_t_title 
                    FROM bill
                    JOIN type ON type.id = bill.type_id
                    LEFT JOIN account as a_f ON a_f.id = bill.account_from_id AND a_f.user_id = $user_id AND a_f.delete_flag = 0
                    LEFT JOIN account as a_t ON a_t.id = bill.account_to_id AND a_t.user_id = $user_id AND a_t.delete_flag = 0
                    WHERE bill.date >= $date_start AND bill.date <= $date_end {0}
                    ORDER BY bill.date, bill.id""".format(sql), vars=sql_params
            )
        else:
            month_bills = DB.query(
                """ SELECT bill.*, type.title as type_title, a_f.title as a_f_title, a_t.title as a_t_title 
                    FROM bill
                    JOIN type ON type.id = bill.type_id
                    LEFT JOIN account as a_f ON a_f.id = bill.account_from_id AND a_f.user_id = $user_id AND a_f.delete_flag = 0
                    LEFT JOIN account as a_t ON a_t.id = bill.account_to_id AND a_t.user_id = $user_id AND a_t.delete_flag = 0
                    WHERE bill.date >= $month_start
                    ORDER BY bill.date, bill.id""",
                vars={'user_id' : Session['login'], 'month_start' : str(Session['month_start'])}
            )
        user_f_accounts = DB.select('account', where='user_id = $user_id AND delete_flag = 0', vars={'user_id' : Session['login']})
        user_t_accounts = DB.select('account', where='user_id = $user_id AND delete_flag = 0', vars={'user_id' : Session['login']})
        bill_types = DB.select('type')
        bill = {}
        if hasattr(Session, 'bill_add'):
            bill = Session.bill_add
        return Render.bill_list(month_bills, user_f_accounts, user_t_accounts, bill_types, bill, params, {})
    
    index = get_add
    
    def post_add(self):
        params = web.input()
        DB.insert('bill', account_from_id=params.f_account, account_to_id=params.t_account, date=params.date, type_id=params.type,
            amount=params.amount, claim_flag=params.claim, description=params.description)
        web.seeother('add')

class Claim(PageMixIn, AuthMixIn):
    def get_approve(self):
        first_claim = DB.query(
            """ SELECT bill.date
                FROM bill
                LEFT JOIN account as a_f ON a_f.id = bill.account_from_id AND a_f.user_id = $user_id AND a_f.delete_flag = 0
                LEFT JOIN account as a_t ON a_t.id = bill.account_to_id AND a_t.user_id = $user_id AND a_t.delete_flag = 0
                WHERE bill.claim_flag = 2
                ORDER BY bill.date LIMIT 1""",
            vars={'user_id' : Session['login']}
        )
        claim = {}
        if hasattr(Session, 'claim_approve'):
            claim = Session.claim_approve
        if (len(first_claim) == 0):
            return Render.claim_list([], claim, {})
        first_claim_date = first_claim[0].date
        if first_claim_date < Session['month_start']:
            claim_end = Session['month_start']
        else:
            claim_end = datetime.date.today() + datetime.timedelta(1)
        claim_list = DB.query(
            """ SELECT bill.*, type.title as type_title, a_f.title as a_f_title, a_t.title as a_t_title 
                FROM bill
                JOIN type ON type.id = bill.type_id
                LEFT JOIN account as a_f ON a_f.id = bill.account_from_id AND a_f.user_id = $user_id AND a_f.delete_flag = 0
                LEFT JOIN account as a_t ON a_t.id = bill.account_to_id AND a_t.user_id = $user_id AND a_t.delete_flag = 0
                WHERE bill.date < $claim_end AND bill.claim_flag = 2
                ORDER BY bill.date, bill.id""",
            vars={'user_id' : Session['login'], 'claim_end' : str(claim_end)}
        )
        return Render.claim_list(claim_list, claim, {})
    
    index = get_approve
    
    def post_approve(self):
        params = web.input(claim=[])
        if params.action == u'报销':
            DB.update('bill', where='id IN ({0})'.format(','.join(params.claim)), claim_flag = 1)
        elif params.action == u'不报销':
            DB.update('bill', where='id IN ({0})'.format(','.join(params.claim)), claim_flag = 0)
        web.seeother('approve')

class Summary(PageMixIn, AuthMixIn):
    def get_stat(self):
        stat_start = datetime.date(Session['month_start'].year, Session['month_start'].month - 1, Session['month_start'].day)
        month_outgo = DB.query(
            """ SELECT IFNULL(SUM(bill.amount), 0) AS money, type.id AS type_id
                FROM type
                LEFT JOIN bill ON type.id = bill.type_id AND bill.date >= $month_start AND bill.date < $month_end AND bill.account_to_id = 0 AND bill.claim_flag IN (0, 2)
                LEFT JOIN account as a_f ON a_f.id = bill.account_from_id AND a_f.user_id = $user_id AND a_f.delete_flag = 0
                GROUP BY type.id
                ORDER BY type.id""",
            vars={'user_id' : Session['login'], 'month_start' : str(stat_start), 'month_end' : str(Session['month_start'])}
        )
        month_income = DB.query(
            """ SELECT IFNULL(SUM(bill.amount), 0) AS money, type.id AS type_id
                FROM type
                LEFT JOIN bill ON type.id = bill.type_id AND bill.date >= $month_start AND bill.date < $month_end AND bill.account_from_id = 0 AND bill.claim_flag IN (0, 2)
                LEFT JOIN account as a_t ON a_t.id = bill.account_to_id AND a_t.user_id = $user_id AND a_t.delete_flag = 0
                GROUP BY type.id
                ORDER BY type.id""",
            vars={'user_id' : Session['login'], 'month_start' : str(stat_start), 'month_end' : str(Session['month_start'])}
        )
        month_budget = DB.query(
            """ SELECT IFNULL(summary.budget, 0) AS budget
                FROM type
                LEFT JOIN summary ON type.id = summary.type_id AND summary.date >= $month_start AND summary.date < $month_end AND summary.user_id = $user_id
                ORDER BY type.id""",
            vars={'user_id' : Session['login'], 'month_start' : str(stat_start), 'month_end' : str(Session['month_start'])}
        )
        bill_types = DB.select('type')
        return Render.stat(month_outgo, month_income, month_budget, bill_types)
    
    index = get_stat

if __name__ == '__main__':
    start()
