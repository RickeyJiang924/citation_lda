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
sql = "SELECT SNO,LYPM,NIAN from ci_lysy"
cursor.execute(sql)
results = cursor.fetchall()
# 标题->基本信息
d = dict()
# sno->标题
dd = dict()
# 引文id->被引文id
ddd = dict()
# 自增id初始值
count = 1

for item in results:
    # 标题不为空
    if len(item[1]) > 0:
        d[item[1]] = dict()
        d[item[1]]['id'] = count
        count += 1
        d[item[1]]['sno'] = item[0]
        d[item[1]]['title'] = item[1]
        d[item[1]]['year'] = item[2]
        d[item[1]]['author'] = ''
        dd[item[0]] = item[1]
        # print(item[0])

# 获取作者
sql = "SELECT SNO,group_concat(ZZMC) from ci_lyzz group by sno"
cursor.execute(sql)
results = cursor.fetchall()
for item in results:
    if dd[item[0]] in d.keys():
        if len(item[1]) < 1:
            d[dd[item[0]]]['author'] = ''
        else:
            d[dd[item[0]]]['author'] = item[1]

# 获取引文
sql = "SELECT SNO,YWZZ,YWPM,YWND from ci_ywsy where YWLX='01'"
cursor.execute(sql)
results = cursor.fetchall()
for item in results:
    if item[2] not in d.keys() and len(item[2]) > 1:
        d[item[2]] = dict()
        d[item[2]]['id'] = count
        count += 1
        d[item[2]]['sno'] = ''
        d[item[2]]['author'] = item[1]
        d[item[2]]['title'] = item[2]
        d[item[2]]['year'] = item[3]
        if d[dd[item[0]]]['id'] not in ddd.keys():
            ddd[d[dd[item[0]]]['id']] = []
        ddd[d[dd[item[0]]]['id']].append(d[item[2]]['id'])
# print(ddd[1])

# f = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\economics_metadata_file.txt', 'a+', encoding='utf-8')
f = open('E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\economics_metadata_file.txt', 'a+', encoding='utf-8')
for item in d.keys():
    if len(d[item]['title']) > 1:
        line = 'id = ' + str(d[item]['id']) + '\n' + 'author = ' + d[item]['author'] + '\n' + 'title = ' + d[item]['title'] + '\n' + 'year = ' + \
           str(d[item]['year']) + '\n\n'
        print(line, end='')
        f.write(line)

# f = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\economics_citation_file.txt', 'a+', encoding='utf-8')
f = open('E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\economics_citation_file.txt', 'a+', encoding='utf-8')
for item in ddd.keys():
    for i in range(len(ddd[item])):
        f.write(str(item))
        f.write('\n')
        f.write(str(ddd[item][i]))
        f.write('\n')
        f.write('[]')
        f.write('\n')
        f.write('\n')

# 关闭数据库连接
db.close()
