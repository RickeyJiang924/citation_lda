# @author RickeyJiang
# @date 2019/3/13

import sys
import topic_modeling.Lda as lda
import corpus.economics as economics
import toolkit.utility as utility
import jieba

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
        topDocId = [d for d in sorted(range(ldaInstance.D), key=lambda x:phiMatrix[k][x], reverse=True)][0:topDocCnt]
        topDocs = [(phiMatrix[k][d], 'unknownVenue', hd.docs[idToEid[d]]['title']) for d in topDocId]
        topTokId = [t for t in sorted(tokExptFreq, key=lambda x:tokExptFreq[x], reverse=True)][0:topTokCnt]
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
    for k in sorted(topicSummary, key=lambda k:topicSummary[k][2], reverse=True):
        sys.stdout.write('\r[topic summary]: dump topic {0}'.format(k))
        sys.stdout.flush()
        (topToks, yearDist, topWei, topDocs) = topicSummary[k]
        dumpFile.write('[Topic: {0}]:{1:.6f}  year={2:.6f}({3:.6f})\n'.format(k, topWei, utility.getDistExpectation(yearDist),
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
    for k in sorted(topicSummary, key=lambda k:topicSummary[k][2], reverse=True):
        sys.stdout.write('\r[topic short summary]: dump topic {0}'.format(k))
        sys.stdout.flush()
        (topToks, yearDist, topWei, topDocs) = topicSummary[k]
        dumpFile.write('[Topic: {0}]:{1:.6f}  year={2:.2f}({3:.2f}) '.format(k, topWei, utility.getDistExpectation(yearDist), utility.getDistStd(yearDist)))
        for topTok in topToks: dumpFile.write('{0} '.format(topTok[1]))
        dumpFile.write('\n')
    print('')
    dumpFile.close()

def economicsCitationLdaSummary(ldaFilePath):
    print('[economics-citation-LDA] loading lda')
    ldaInstance = lda.readLdaEstimateFile(ldaFilePath)
    print('[economics-citation-LDA] loading economics')
    hd = economics.getEconomicsCorpus()
    print('[economics-citation-LDA] indexing')
    eidToId, idToEid = economics.getCitMetaGraphEidIdMapping(hd)
    print('[economics-citation-LDA] topic summary generation')
    topicSummary = getTopicSummary(hd, eidToId, idToEid, ldaInstance, topDocCnt=10, topTokCnt=20)
    print('[economics-citation-LDA] topic summary dump')
    dumpTopicSummary(topicSummary, ldaFilePath + '_summary')
    # dumpShortTopicSummary(topicSummary, ldaFilePath + '_shortsummary')
    return


if __name__ == '__main__':
    # 测试中文分词方法jieba
    # sentence = '我是一个顽童，上午学习历史'
    # print(jieba.lcut(sentence))
    # print(jiebaTokenize(sentence))

    lda.economicsCitationLdaRun(100, 3.5, 3.5)
    # economicsCitationLdaSummary(
    #     'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\'
    #     'economics_citation_lda_50_45895_45895_1e-06_1e-06_timeCtrl_3.5_3.5.lda')
    # economicsCitationLdaSummary(
    #     'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\'
    #     'economics_citation_lda_100_46101_46101_1e-06_1e-06_timeCtrl_0.1_0.1.lda')
