import pymysql
import sys

db = pymysql.connect('localhost', 'root', 'jrq.l.iggy09', 'historics', charset='utf8')
# 获取游标
cursor = db.cursor()
# 获取引文
sql = "SET session group_concat_max_len=18000"
sql_1 = "SELECT * FROM final_info"
f = open('E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\test_metadata_file.txt', 'a+', encoding='utf-8')
cursor.execute('SET NAMES UTF8')
cursor.execute(sql)
cursor.execute(sql_1)
results = cursor.fetchall()
for item in results:
    line = 'id = ' + str(item[0]) + '\n' + 'author = ' + item[2] + '\n' + 'title = ' + item[1] + '\n' + 'year = ' + item[3] + '\n\n'
    print(line, end='')
    f.write(line)
f.close()
# except:
#     print('failure...')
#     print(sys.exc_info()[0])

# 关闭数据库连接
db.close()