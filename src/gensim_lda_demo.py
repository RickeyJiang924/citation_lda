import pymysql
import warnings
warnings.filterwarnings(action='ignore',category=UserWarning,module='gensim')
from gensim.models import LdaModel
from gensim.corpora.dictionary import Dictionary


db = pymysql.connect('localhost', 'root', 'jrq.l.iggy09', 'historics')
citation = []
# 获取游标
cursor = db.cursor()

# 获取引文
sql = "SET session group_concat_max_len=18000"
sql1 = "SELECT sno,title,GROUP_CONCAT(citation SEPARATOR ',') FROM test_test where length(citation) > 0 GROUP BY sno"
try:
    cursor.execute(sql)
    cursor.execute(sql1)
    results = cursor.fetchall()
    for item in results:
        # print(item[2])
        flag = True
        line = item[2].split(',')
        for i in line:
            if len(i) == 0:
                flag = False
                break
        if flag:
            citation.append(item[2].split(','))
except:
    print('failure...')

# 关闭数据库连接
db.close()

for item in citation:
    print(item)
length = len(citation)
# print(length)
common_dictionary = Dictionary(citation)
common_corpus = [common_dictionary.doc2bow(text) for text in citation]

# Train the model on the corpus.
num_topics = 30;
# iterations = 100,
lda = LdaModel(common_corpus, id2word=common_dictionary, num_topics=num_topics, passes=2000, chunksize=length)
# print(len(common_corpus))

# 文章主题偏好
print('文章主题偏好')
for i in range(num_topics):
    print(lda.get_document_topics(common_corpus[i], minimum_probability=0.0))

# 主题内容展示,返回重要词以及重要 引用 概率
print('主题内容展示,返回重要词以及重要 引用 概率')
for i in range(lda.num_topics):
    print(lda.get_topic_terms(i, topn=5))

# 打印主题-引用分布
print('打印主题-引用分布')
for i in range(num_topics):
    print(lda.print_topic(i, topn=10))

# 保存结果
tc = open('output/topic_citation.txt', 'w')
topic_citation = lda.print_topics(num_topics=num_topics, num_words=10)
for v in topic_citation:
    tc.write(str(v)+'\n')
