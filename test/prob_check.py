f = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\software_data\\software_citation_lda_50_35979_35979_1e-06_1e-06_timeCtrl_4_4.lda_citMatrix', 'r')
lines = f.read().replace('\n', ' ')
data = [float(i) for i in lines.split(' ')]
data.sort(reverse=True)
print(data[50])
