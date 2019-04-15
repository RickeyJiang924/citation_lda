# @author RickeyJiang
# @date 2019/3/13

import sys
import topic_modeling.Lda as lda
import corpus.economics as economics
import toolkit.utility as utility
import jieba
import re


def filterTokLst(tokLst):
    return [tok for tok in tokLst if (len(tok) > 1)]


# 输入str 返回list
def jiebaTokenize(sentence):
    stopwords_file = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\references\\stopwords.txt', 'r',
                          encoding='utf-8')
    eng_stopwords_file = open('E:\\study\\PycharmProjects\\lda_project\\citation_lda\\references\\eng_stopwords.txt',
                              'r', encoding='utf-8')
    # stopwords_file = open('E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\references\\stopwords.txt', 'r', encoding='utf-8')
    # eng_stopwords_file = open('E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\references\\eng_stopwords.txt', 'r',
    #                       encoding='utf-8')
    stopwords = stopwords_file.read().split('\n')
    eng_stopwords = eng_stopwords_file.read().split('\n')
    results = ' '.join(jieba.cut(sentence)).split(' ')
    result = []
    # print(results)
    for r in results:
        if r not in stopwords and r not in eng_stopwords:
            result.append(r)
    # print(result)
    return result


def getTopicSummary(hd, eidToId, idToEid, ldaInstance, topDocCnt=20, topTokCnt=20, topVenueCnt=20):
    phiMatrix = ldaInstance.phiEstimate
    topWeiVec = ldaInstance.topWeiEstimate
    topicSummary = {}
    for k in range(ldaInstance.K):
        sys.stdout.write('\r[topic summary]: process topic {0}'.format(k))
        sys.stdout.flush()
        tokExptFreq = {}
        # venueDist = {}
        yearDist = {}
        topDocs = []
        topToks = []
        for d in range(ldaInstance.D):
            prob = phiMatrix[k][d]
            eid = idToEid[d]
            title = hd.docs[eid]['title']
            year = hd.docs[eid]['year']
            #  分词，过滤停用词
            tokLst = filterTokLst(jiebaTokenize(title))
            for tok in tokLst:
                tokExptFreq[tok] = tokExptFreq.get(tok, 0.0) + prob
            # venueDist[venue] = venueDist.get(venue, 0.0) + prob
            yearDist[year] = yearDist.get(year, 0.0) + prob
        topDocId = [d for d in sorted(range(ldaInstance.D), key=lambda x: phiMatrix[k][x], reverse=True)][0:topDocCnt]
        topDocs = [(phiMatrix[k][d], 'unknownVenue', hd.docs[idToEid[d]]['title']) for d in topDocId]

        # 测试，分析前50篇文章的关键词
        # top50DocId = [d for d in sorted(range(ldaInstance.D), key=lambda x:phiMatrix[k][x], reverse=True)][0:50]
        # top50Docs = [(phiMatrix[k][d], hd.docs[idToEid[d]]['title']) for d in top50DocId]
        # top50Freq = {}
        # for item in top50Docs:
        #     #  分词，过滤停用词
        #     wordLst = filterTokLst(jiebaTokenize(item[1]))
        #     for word in wordLst:
        #         top50Freq[word] = top50Freq.get(word, 0.0) + 1
        # top50Tok = [t for t in sorted(top50Freq, key=lambda x: top50Freq[x], reverse=True)][0:topTokCnt]
        # topToks = [(tokExptFreq[tok], tok) for tok in top50Tok]

        # 所有文章关键词及概率
        topTokId = [t for t in sorted(tokExptFreq, key=lambda x: tokExptFreq[x], reverse=True)][0:topTokCnt]
        topToks = [(tokExptFreq[tok], tok) for tok in topTokId]

        # topVenueId = [venue for venue in sorted(venueDist, key=lambda x:venueDist[x], reverse=True)][0:topVenueCnt]
        # topVenues = [(venueDist[venue], venue) for venue in topVenueId]
        # (topToks, venueDist, yearDist, topWeiVec[k], topDocs, topVenues)
        topicSummary[k] = (topToks, yearDist, topWeiVec[k], topDocs)
    print('')
    return topicSummary


def dumpTopicSummary(topicSummary, dumpFilePath):
    print('[topic summary]: dump to file {0}'.format(dumpFilePath))
    dumpFile = open(dumpFilePath, 'w', encoding='utf-8')
    for k in sorted(topicSummary, key=lambda k: topicSummary[k][2], reverse=True):
        sys.stdout.write('\r[topic summary]: dump topic {0}'.format(k))
        sys.stdout.flush()
        (topToks, yearDist, topWei, topDocs) = topicSummary[k]
        dumpFile.write(
            '[Topic: {0}]:{1:.6f}  year={2:.6f}({3:.6f})\n'.format(k, topWei, utility.getDistExpectation(yearDist),
                                                                   utility.getDistStd(yearDist)))
        for topDoc in topDocs:
            dumpFile.write('Doc:{0:.6f}:[{1:^20}]:{2}\n'.format(topDoc[0], topDoc[1], topDoc[2]))
        for topTok in topToks:
            dumpFile.write('Tok:{0:.6f}:{1}\n'.format(topTok[0], topTok[1]))
        # for topVenue in topVenues: dumpFile.write('Ven:{0:.6f}:{1}\n'.format(topVenue[0], topVenue[1]))
        dumpFile.write('\n')
    print('')
    dumpFile.close()


def dumpShortTopicSummary(topicSummary, dumpFilePath):
    print('[topic short summary]: dump to file {0}'.format(dumpFilePath))
    dumpFile = open(dumpFilePath, 'w')
    for k in sorted(topicSummary, key=lambda k: topicSummary[k][2], reverse=True):
        sys.stdout.write('\r[topic short summary]: dump topic {0}'.format(k))
        sys.stdout.flush()
        (topToks, yearDist, topWei, topDocs) = topicSummary[k]
        dumpFile.write(
            '[Topic: {0}]:{1:.6f}  year={2:.2f}({3:.2f}) '.format(k, topWei, utility.getDistExpectation(yearDist),
                                                                  utility.getDistStd(yearDist)))
        for topTok in topToks: dumpFile.write('{0} '.format(topTok[1]))
        dumpFile.write('\n')
    print('')
    dumpFile.close()


def getCitationMatrix(ldaInstance):
    print('[citation matrix]: computing citation matrix')
    thetaMatrix = ldaInstance.thetaEstimate
    phiMatrix = ldaInstance.phiEstimate
    topicWeightVec = ldaInstance.topWeiEstimate
    citMatrix = [[0.0 for k1 in range(ldaInstance.K)] for k2 in range(ldaInstance.K)]
    # ===========================================================================
    # P(c2 | c1) = sum_d phi_c1(d) theta_d(c2)
    # ===========================================================================
    cnt = 0
    for d in range(ldaInstance.D):
        k1Lst = [k for k in range(ldaInstance.K) if phiMatrix[k][d] != 0.0]
        k2Lst = [k for k in range(ldaInstance.K) if thetaMatrix[d][k] != 0.0]
        for k1 in k1Lst:
            for k2 in k2Lst:
                citMatrix[k1][k2] += phiMatrix[k1][d] * thetaMatrix[d][k2]
        if (d % 10 == 0): utility.printProgressBar(float(d) / ldaInstance.D)
    print('')
    return citMatrix


def pubmedCitationMatrix(ldaFilePath):
    print('[pubmed-citation-LDA]: loading lda')
    ldaInstance = lda.readLdaEstimateFile(ldaFilePath)
    citMatrix = getCitationMatrix(ldaInstance)
    citMatrixFile = open(ldaFilePath + '_citMatrix', 'w')
    citMatrixFile.write('\n'.join([' '.join([str(x) for x in vec]) for vec in citMatrix]))
    citMatrixFile.close()
    return


def economicsCitationLdaSummary(ldaFilePath):
    print('[economics-citation-LDA] loading lda')
    ldaInstance = lda.readLdaEstimateFile(ldaFilePath)
    print('[economics-citation-LDA] loading economics')
    hd = economics.getEconomicsCorpus()
    print('[economics-citation-LDA] indexing')
    eidToId, idToEid = economics.getCitMetaGraphEidIdMapping(hd)
    print('[economics-citation-LDA] topic summary generation')
    topicSummary = getTopicSummary(hd, eidToId, idToEid, ldaInstance, topDocCnt=10, topTokCnt=10)
    print('[economics-citation-LDA] topic summary dump')
    dumpTopicSummary(topicSummary, ldaFilePath + '_summary')
    # dumpShortTopicSummary(topicSummary, ldaFilePath + '_shortsummary')
    return


def readTopicSummary(topicSummaryFilePath):
    topicLnRe = re.compile(r'\[Topic: (.*?)\]:(.*?)  year=(.*?)\((.*?)\)')
    docLnRe = re.compile(r'Doc:(.*?):[(.*?)]:(.*)')
    tokLnRe = re.compile(r'Tok:(.*?):(.*)')
    venLnRe = re.compile(r'Ven:(.*?):(.*)')
    topicSummaryDict = {}
    topicSummaryFile = open(topicSummaryFilePath, 'r')
    eof = False
    while (not eof):
        (chunkLnLst, eof) = utility.readChunk(topicSummaryFile)
        topicId = None
        topicProb = None
        topicYearMean = None
        topicYearVar = None
        topDocs = []
        topToks = []
        topVens = []
        for ln in chunkLnLst:
            topicLnReMatch = topicLnRe.match(ln)
            if (topicLnReMatch):
                topicId = utility.parseNumVal(topicLnReMatch.group(1))
                topicProb = utility.parseNumVal(topicLnReMatch.group(2))
                topicYearMean = utility.parseNumVal(topicLnReMatch.group(3))
                topicYearVar = utility.parseNumVal(topicLnReMatch.group(4))
                continue
            docLnReMatch = docLnRe.match(ln)
            if (docLnReMatch):
                docProb = utility.parseNumVal(docLnReMatch.group(1))
                docVen = docLnReMatch.group(2).strip()
                docTitle = docLnReMatch.group(3).strip()
                topDocs.append((docProb, docVen, docTitle))
                continue
            tokLnReMatch = tokLnRe.match(ln)
            if (tokLnReMatch):
                tokProb = utility.parseNumVal(tokLnReMatch.group(1))
                tok = tokLnReMatch.group(2).strip()
                topToks.append((tokProb, tok))
                continue
            venLnReMatch = venLnRe.match(ln)
            if (venLnReMatch):
                venProb = utility.parseNumVal(venLnReMatch.group(1))
                ven = venLnReMatch.group(2).strip()
                topVens.append((venProb, ven))
                continue
        if (topicId is not None):
            topicSummaryDict[topicId] = (topicId, topicProb, topicYearMean, topicYearVar, topDocs, topToks, topVens)
    return topicSummaryDict


def readCitMatrixSummary(citMatrixFilePath):
    citMatrixFile = open(citMatrixFilePath, 'r')
    (citMatrix, eof) = utility.readMatrix(citMatrixFile)
    return citMatrix


if __name__ == '__main__':
    # 测试中文分词方法jieba
    # sentence = '我是一个顽童，上午学习历史'
    # print(jieba.lcut(sentence))
    # print(jiebaTokenize(sentence))

    # lda.economicsCitationLdaRun(100, 3.5, 3.5)
    # economicsCitationLdaSummary('E:\\study\\PycharmProjects\\lda_project\\citation_lda\data\economics_citation_lda_50_546205_546205_1e-06_1e-06_timeCtrl_20_20.lda')
    # economicsCitationLdaSummary(
    #     'E:\\bigdata\PycharmWorkspace\\lda_project\\citation_lda\\data'
    #     '\\economics_citation_lda_50_546205_546205_1e-06_1e-06_timeCtrl_0.5_0.5.lda')

    pubmedCitationMatrix(
        '/Users/loohaze/Downloads/economics_citation_lda_50_546205_546205_1e-06_1e-06_timeCtrl_20_20.lda')
