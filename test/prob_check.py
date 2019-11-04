f = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\management_data\\management_citation_lda_20_5119_5119_1e-06_1e-06_timeCtrl_4_4.lda_citMatrix', 'r')
lines = f.read().replace('\n', ' ')
data = [float(i) for i in lines.split(' ')]
data.sort(reverse=True)
print(data[50])
