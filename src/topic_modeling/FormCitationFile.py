import pymysql
import sys

db = pymysql.connect('localhost', 'root', 'jrq.l.iggy09', 'lda', charset='utf8')
# 获取游标
cursor = db.cursor()
# 获取引文
sql = "SET session group_concat_max_len=18000"
sql_1 = "SELECT citing, cited FROM final_relation"
f = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\test_citation_file.txt', 'a+', encoding='utf-8')
# f = open('E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\test_citation_file.txt', 'a+', encoding='utf-8')
cursor.execute('SET NAMES UTF8')
cursor.execute(sql)
cursor.execute(sql_1)
results = cursor.fetchall()
for item in results:
    f.write(str(item[0]))
    f.write('\n')
    f.write(str(item[1]))
    f.write('\n')
    f.write('[]')
    f.write('\n\n')
f.close()
# except:
#     print('failure...')
#     print(sys.exc_info()[0])

# 关闭数据库连接
db.close()