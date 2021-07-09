import json
import pymysql
import pandas
import random
import datetime

db_host = 'localhost'
db_user = 'root'
db_passwd = '000000'
db_name = 'airdb'
db_code = 'utf8'
db_port = 3306

# data: airport-city-province, fixed
json_path = "D:\\airdb_py\\db_prepare\\airport.json"
sql = []
province = []
city = []
airport = []
with open(json_path, 'r', encoding='utf_8_sig') as f:
    data_raw = json.load(f)
    for data in data_raw:
        city_name = data['areaName']
        if city_name[-1] == '市':
            city_name = city_name[0:-1]
        airport.append([data['code'], data['airportName'], city_name])
        city.append([city_name, data['provinceName']])
        province.append(data['provinceName'])

# data of table province
prov_list = []
prov_dict = {}
prov_str = ''
i = 0
for p in province:
    if p not in prov_list:
        prov_list.append(p)
        i += 1
        prov_dict[p] = i
        prov_str += str((i, p)) + ','
sql1 = 'insert into province values ' + prov_str[0:-1] + ';'
sql.append(sql1)


# data of table city
city_list = []
city_dict = {}
city_str = ''
i = 0
for c in city:
    if c[0] not in city_list:
        city_list.append(c[0])
        i += 1
        city_dict[c[0]] = i
        city_str += str((i, prov_dict[c[1]], c[0])) + ','
sql1 = 'insert into city values ' + city_str[0:-1] + ';'
sql.append(sql1)


# data of table airport
# airp_list = []
airp_str = ''
airp_dict = {}
i = 0
for a in airport:
    i += 1
    airp_dict[a[1]] = i
    airp_str += str((i, a[1], city_dict[a[2]], a[0])) + ','
sql1 = 'insert into airport values ' + airp_str[0:-1] + ';'
sql.append(sql1)




# data of company, aircraft and flight, semi-fixed
xls_path = "D:\\airdb_py\\db_prepare\\com_airc_flig.xls"
df = pandas.read_excel(xls_path)

# filter
data_list = []
company = []
com_dict = {}
cid = 0
aircraft = []
airc_dict = {}
name_list = []
aid = 0
j = 0
default_begin = '2021-06-30'
default_end = '2021-08-31'
pf = 3000
pc = 1200
py = 420
for i in range(df.shape[0]):
    if df['flight_schedules'][i] not in name_list:
        name_list.append(df['flight_schedules'][i])
    else:
        continue
    if df['departure_airport'][i] in airp_dict.keys() and df['landing_airport'][i] in airp_dict.keys():
        if df['aircraft_models'][i] == '其他机型':
            continue
        if df['airlines'][i] not in company:
            cid += 1
            company.append(df['airlines'][i])
            com_dict[df['airlines'][i]] = cid
        if df['aircraft_models'][i] not in aircraft:
            aid += 1
            aircraft.append(df['aircraft_models'][i])
            airc_dict[df['aircraft_models'][i]] = aid
        p = df['punctuality_rate'][i]
        if p == 1:
            p -= 0.01
        j += 1
        r = random.uniform(0.7, 1.3)
        data_list.append([j, df['flight_schedules'][i], com_dict[df['airlines'][i]],
                          airc_dict[df['aircraft_models'][i]], airp_dict[df['departure_airport'][i]],
                          airp_dict[df['landing_airport'][i]], str(df['departure_time'][i]),
                          str(df['landing_time'][i]), p, default_begin, default_end,
                          int(pf*r), int(pc*r), int(py*r)])

# data of company
default_str = '", "000000", 0.7, 0.3),'
com_str = ''
i = 0
for c in company:
    i += 1
    com_str += '('+str(i)+', "'+c+default_str
sql1 = 'insert into company values' + com_str[0:-1] + ';'
sql.append(sql1)
# create and grant cad
for c in company:
    # sql.append('create user %s;' % c)
    sql.append('grant company_ad to %s;' % c)
    sql.append('update mysql.user set Grant_priv="Y", Super_priv="Y" where user = "%s";' % c)
    sql.append('set default role all to %s;' % c)




# data of aircraft
default_str = '", 3, 6, 12),'
airc_str = ''
i = 0
for a in aircraft:
    i += 1
    airc_str += '('+str(i)+', "'+a+default_str
sql1 = 'insert into aircraft values' + airc_str[0:-1] + ';'
sql.append(sql1)

# data of flight
flig_str = ''
for f in data_list:
    flig_str += '(' + str(f)[1:-1] + '),'
sql1 = 'insert into flight values' + flig_str[0:-1] + ';'
sql.append(sql1)


# datelog
sql1 = 'insert into datelog value ("2021-07-01");'
sql.append(sql1)


db = pymysql.connect(user=db_user, password=db_passwd, database=db_name, port=db_port, charset=db_code)
cur = db.cursor()

try:
    cur.execute('set autocommit=0;')
    for sql1 in sql:
        print(sql1)
        cur.execute(sql1)
    db.commit()
    cur.close()
    db.close()
except pymysql.Error as e:
    print(e.args[0], e.args[1])
    db.rollback()


