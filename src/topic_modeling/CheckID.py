# @author: RickeyJiang
# @date: 2019/4/7

f = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\economic_data\\economics_metadata_file.txt', 'r', encoding='utf-8')
count = 1
line = ''
while line is not None:
    line = f.readline()
    if len(line.strip('\n')) < 1:
        break
    print(line.strip('\n'))
    if line.strip('\n').split(' ')[2] != str(count):
        print(line.split(' ')[2], end=" ")
        break
    count += 1
    for i in range(4):
        line = f.readline()
        if i == 2 and int(line[7:]) < 21:
            break
        print(line.strip('\n'))

# count1 = 0
# f = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\economic_data\\economics_citation_file.txt', 'r', encoding='utf-8')
# line = ''
# while line is not None:
#     line = f.readline()
#     if len(line.strip('\n')) < 1:
#         break
#     print(line.strip('\n'))
#     count1 += 1
#     for i in range(3):
#         line = f.readline()
#         print(line.strip('\n'))
# print(count)
# print(count1)

