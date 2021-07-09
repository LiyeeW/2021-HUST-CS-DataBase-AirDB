import pymysql
import pandas

db_host = 'localhost'
db_user = 'root'
db_passwd = '000000'
db_name = 'airdb'
db_code = 'utf8'
db_port = 3306







db = pymysql.connect(user=db_user, password=db_passwd, database=db_name, port=db_port, charset=db_code)
cursor = db.cursor()
sqlcommamds = ['set global log_bin_trust_function_creators=TRUE;']


filename = 'function_1.sql'
fd = open(filename, 'r', encoding='utf-8')
sqlcommamds.append(fd.read())
fd.close()

filename = 'function_2.sql'
fd = open(filename, 'r', encoding='utf-8')
sqlcommamds.append(fd.read())
fd.close()

filename = 'flight_insert.sql'
fd = open(filename, 'r', encoding='utf-8')
sqlcommamds.append(fd.read())
fd.close()

filename = 'flight_update.sql'
fd = open(filename, 'r', encoding='utf-8')
sqlcommamds.append(fd.read())
fd.close()

filename = 'datelog_insert.sql'
fd = open(filename, 'r', encoding='utf-8')
sqlcommamds.append(fd.read())
fd.close()

filename = 'generate_ticket.sql'
fd = open(filename, 'r', encoding='utf-8')
sqlcommamds.append(fd.read())
fd.close()

filename = 'procedure_1.sql'
fd = open(filename, 'r', encoding='utf-8')
sqlcommamds.append(fd.read())
fd.close()


try:
    cursor.execute('set autocommit=0;')
    for command in sqlcommamds:
        cursor.execute(command)
    db.commit()
    cursor.close()
    db.close()
except pymysql.Error as e:
    print(e.args[0], e.args[1])
    db.rollback()

