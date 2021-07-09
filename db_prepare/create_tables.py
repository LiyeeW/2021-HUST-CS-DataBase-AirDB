import json
import pymysql
import traceback

db_host = 'localhost'
db_user = 'root'
db_passwd = '000000'
db_name = 'airdb'
db_code = 'utf8'
db_port = 3306


db = pymysql.connect(user=db_user, password=db_passwd, database=db_name, port=db_port, charset=db_code)
cur = db.cursor()


# create table:
sql = []
# province
sql1 = 'create table province ' \
      '(id      int         not null  auto_increment  primary key,' \
      'name     char(50)    unique  not null);'
sql.append(sql1)
# city
sql1 = 'create table city' \
       '(id     int         not null  auto_increment  primary key,' \
       'pid     int         not null,' \
       'name    char(50)    not null,' \
       'foreign key(pid) references province(id));'
sql.append(sql1)
# airport
sql1 = 'create table airport' \
       '(id     int         not null  auto_increment  primary key,' \
       'name    char(50)    not null,' \
       'cid     int         not null,' \
       'code    char(50)    unique not null,' \
       'foreign key(cid) references city(id));'
sql.append(sql1)
# company
sql1 = 'create table company' \
       '(id     int         not null  auto_increment  primary key,' \
       'name    char(50)    unique  not null,' \
       'passwd  char(50)    not null,' \
       'debit1  float(2,2),' \
       'debit2  float(2,2));'
sql.append(sql1)
# aircraft
sql1 = 'create table aircraft' \
       '(id     int         not null  auto_increment  primary key,' \
       'name    char(50)    unique  not null,' \
       'numf    int,' \
       'numc    int,' \
       'numy    int);'
sql.append(sql1)
# flight
sql1 = 'create table flight' \
       '(id     int         not null  auto_increment  primary key,' \
       'name    char(50)    not null,' \
       'cid     int         not null,' \
       'acid    int         not null,' \
       'aid_f   int         not null,' \
       'aid_t   int         not null,' \
       'off_due     time,' \
       'land_due    time,' \
       'punctual float(2,2),' \
       'begin   date,' \
       'end     date,' \
       'av_pf   int,' \
       'av_pc   int,' \
       'av_py   int,' \
       'foreign key(cid) references company(id),' \
       'foreign key(acid) references aircraft(id),' \
       'foreign key(aid_f) references airport(id),' \
       'foreign key(aid_t) references airport(id));'
sql.append(sql1)
# fly
sql1 = 'create table fly' \
       '(id     int         not null  auto_increment  primary key,' \
       'fid     int         not null,' \
       'fdate   date        not null,' \
       'flew    bool,' \
       'off_real    time,' \
       'land_real   time,' \
       'pricef  int,' \
       'pricec  int,' \
       'pricey  int,' \
       'foreign key(fid) references flight(id));'
sql.append(sql1)
# user
sql1 = 'create table user' \
       '(id     int         not null  auto_increment  primary key,' \
       'name    char(50)    not null unique,' \
       'passwd  char(50)    not null,' \
       'bkid    char(16),' \
       'money   int);'
sql.append(sql1)
# person
sql1 = 'create table person' \
       '(id     char(18)         primary key,' \
       'name    char(50)    not null,' \
       'birth   year,' \
       'sex     int);'
sql.append(sql1)
# porder
sql1 = 'create table porder' \
        '(id    int     not null  auto_increment  primary key,' \
        'ffid   int,' \
        'stype  int,' \
        'uid    int,' \
        'odate  date    not null,' \
        'otime  time    not null,' \
        'valid  int,' \
       'num     int not null,' \
        'check(stype>0 and stype<4),' \
        'check(num>0),' \
       'foreign key(ffid) references fly(id),' \
       'foreign key(uid) references user(id));'
sql.append(sql1)
# ticket
sql1 = 'create table ticket' \
        '(id    int         not null  auto_increment  primary key,' \
        'pid    char(18),' \
        'oid    int,' \
        'seat   char(30),' \
        'passwd     char(16),' \
        'fetched    bool,' \
       'foreign key(pid) references person(id),' \
       'foreign key(oid) references porder(id));'
sql.append(sql1)
# agent
sql1 = 'create table agent' \
       '(pid     char(18)        not null,' \
       'uid     int         not null,' \
       'primary key(pid, uid),' \
       'foreign key(pid) references person(id),' \
       'foreign key(uid) references user(id));'
sql.append(sql1)

# datelog
sql1 = 'create table datelog (today date);'
sql.append(sql1)

try:
    cur.execute('set autocommit=0;')
    for sql1 in sql:
        cur.execute(sql1)
    db.commit()
    cur.close()
    db.close()
except pymysql.Error as e:
    print(e.args[0], e.args[1])
    db.rollback()


