# @author: RickeyJiang
# @date: 2019/3/30

import pymysql

db = pymysql.connect('localhost', 'root', 'jrq.l.iggy09', 'economics', charset='utf8')

# 获取游标
cursor = db.cursor()

# 获取引文
sql = "SET session group_concat_max_len=18000"
cursor.execute(sql)
cursor.execute('SET NAMES UTF8')
cursor.execute(sql)

# 获取引文标题、id
sql = "SELECT LYPM from ci_lysy"
cursor.execute(sql)
results = cursor.fetchall()

title = dict()

for item in results:
    # 标题不为空
    if len(item[0]) > 0:
        title[item[0]] = 1

# 获取引文
count = 0
sql = "SELECT YWPM from ci_ywsy where YWLX='01'"
cursor.execute(sql)
results = cursor.fetchall()
for item in results:
    if len(item[0]) > 1 and item[0] in title.keys():
        count += 1
        title[item[0]] += 1

for item in title.keys():
    if title[item] > 1:
        print(item)
print(count)
# 关闭数据库连接
db.close()
