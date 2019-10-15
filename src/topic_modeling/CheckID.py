# @author: RickeyJiang
# @date: 2019/4/7

f = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\software_data\\software_metadata_file.txt', 'r', encoding='utf-8')
count = 1
line = ''
while line is not None:
    line = f.readline()
    print(line)
    if line.strip('\n').split(' ')[2] != str(count):
        print(line.split(' ')[2])
        break
    count += 1
    for i in range(4):
        line = f.readline()
        print(line)

