import pymysql
import sys

db = pymysql.connect('localhost', 'root', 'jrq.l.iggy09', 'historics', charset='utf8')
# 获取游标
cursor = db.cursor()
# 获取引文
sql = "SET session group_concat_max_len=18000"
sql_1 = "SELECT title,citation FROM info_citation where citation is not null"
f = open('E:\\bigdata\\PycharmWorkspace\\lda_project\\data\\test_citation_file.txt', 'a+', encoding='utf-8')
cursor.execute('SET NAMES UTF8')
cursor.execute(sql)
cursor.execute(sql_1)
results = cursor.fetchall()
for item in results:
    line = item[0]+'==>'+item[1]
    print(line)
    f.write(line)
    f.write('\n')
f.close()
# except:
#     print('failure...')
#     print(sys.exc_info()[0])

# 关闭数据库连接
db.close()