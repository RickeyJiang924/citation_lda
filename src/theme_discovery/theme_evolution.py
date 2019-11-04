
import theme_discovery.economics_based_method
import theme_discovery.software_based_method
import theme_discovery.psychology_based_method
import toolkit.utility
import toolkit.gexf
import os.path
import random
import corpus.economics
import corpus.software
import corpus.psychology
import corpus.management
import math

def getMatrixDominantEigenVec(m):
    v = [random.random() for i in range(len(m))]
    iter = 0
    while True:
        v = toolkit.utility.normalizeVector(v)
        v_new = toolkit.utility.getMatrixVecMultiply(m, v)
        if toolkit.utility.getVecNorm(toolkit.utility.getVecSubstract(v, v_new), 2) < 1e-6: break
        v = v_new
        iter += 1
    print(iter)
    return v


def getTopicCitationProb(citMatrix, topicSummaryDict, pmd):
    topicStationaryProbLst = getMatrixDominantEigenVec(toolkit.utility.getTransposeSquareMatrix(citMatrix))
    topicNum = len(citMatrix)
    forwardProb = 0.0
    backwardProb = 0.0
    selfProb = 0.0
    for k1 in range(topicNum):
        for k2 in range(topicNum):
            if topicSummaryDict[k1][2] < topicSummaryDict[k2][2]:
                forwardProb += topicStationaryProbLst[k1] * citMatrix[k1][k2]
            elif k1 == k2:
                selfProb += topicStationaryProbLst[k1] * citMatrix[k1][k2]
            else:
                backwardProb += topicStationaryProbLst[k1] * citMatrix[k1][k2]
    print('[Topic Citation Probability]: backward_prob = {0}'.format(backwardProb))
    print('[Topic Citation Probability]: forward_prob  = {0}'.format(forwardProb))
    print('[Topic Citation Probability]: self_prob     = {0}'.format(selfProb))
    deltaYrDistDict = {}
    for citingPmid in pmd.citeMetaGraph:
        for citedPmid in pmd.citeMetaGraph[citingPmid]:
            if citingPmid == 0:
                continue
            deltaYr = pmd.docs[citingPmid]['year'] - pmd.docs[citedPmid]['year']
            if deltaYr > 300:
                print(citingPmid, pmd.docs[citingPmid]['year'])
                print(citedPmid, pmd.docs[citedPmid]['year'])
            deltaYrDistDict[deltaYr] = deltaYrDistDict.get(deltaYr, 0.0) + pmd.citeMetaGraph[citingPmid][citedPmid]
    print('[Topic Citation Probability]: delta year dist')
    for deltaYr in sorted(deltaYrDistDict):
        print(deltaYr, deltaYrDistDict[deltaYr])
    return


def getVenueRanking(topicSummaryDict):
    vensDict = {}
    for topicId in range(len(topicSummaryDict)):
        (topicId, topicProb, topicYearMean, topicYearVar, topDocs, topToks, topVens) = topicSummaryDict[topicId]
        for (prob, ven) in topVens:
            vensDict[ven] = vensDict.get(ven, 0.0) + topicProb * prob
    return vensDict


def getVenueEntropy(topicSummaryDict):
    venEnt = 0.0
    for topicId in range(len(topicSummaryDict)):
        remProb = 1.0
        minProb = 1.0
        (topicId, topicProb, topicYearMean, topicYearVar, topDocs, topToks, topVens) = topicSummaryDict[topicId]
        for (prob, ven) in topVens:
            venEnt += -topicProb * prob * math.log(prob)
            remProb -= prob
            minProb = min(minProb, prob)
        venEnt += -topicProb * remProb * math.log(minProb)
    topicEnt = 0.0
    for topicId in range(len(topicSummaryDict)): topicEnt += -topicProb * math.log(topicProb)
    return venEnt, topicEnt, topicEnt + venEnt


NOT_FOLD = True


# def graphFilter(citMatrix, topicSummaryDict):
#    
#    return
# ===============================================================================
# API
# ===============================================================================
def dumpGraphFile(citMatrixFilePath, topicSummaryFilePath, edgeWeightThreshold, noSingleton=True, noBackwardEdge=True):
    citMatrix = theme_discovery.software_based_method.readCitMatrixSummary(citMatrixFilePath)
    topicSummaryDict = theme_discovery.software_based_method.readTopicSummary(topicSummaryFilePath)
    #    (topicId, topicProb, topicYearMean, topicYearVar, topDocs, topToks, topVens)
    gexfFilePath = citMatrixFilePath.replace("_citMatrix", ".gexf")
    gexfGen = toolkit.gexf.GexfGen()
    topicIdToTimeSortedId = {}
    for topicId in sorted(topicSummaryDict, key=lambda x: topicSummaryDict[x][2]): topicIdToTimeSortedId[topicId] = len(
        topicIdToTimeSortedId)
    validNodeSet = set()
    for i in range(len(topicSummaryDict)):
        for j in range(len(topicSummaryDict)):
            if i != j and citMatrix[i][j] >= edgeWeightThreshold:
                if noBackwardEdge and topicIdToTimeSortedId[i] > topicIdToTimeSortedId[j]:
                    validNodeSet.add(i)
                    validNodeSet.add(j)
    for topicId in range(len(topicSummaryDict)):
        if noSingleton and (topicId not in validNodeSet): continue
        (topicId, topicProb, topicYearMean, topicYearVar, topDocs, topToks, topVens) = topicSummaryDict[topicId]
        gexfGen.addNodeAtt(topicIdToTimeSortedId[topicId], 'topicId', topicId, 'integer')
        gexfGen.addNodeAtt(topicIdToTimeSortedId[topicId], 'timeSorted', topicIdToTimeSortedId[topicId], 'integer')
        gexfGen.addNodeAtt(topicIdToTimeSortedId[topicId], 'year', topicYearMean, 'double')
        gexfGen.addNodeAtt(topicIdToTimeSortedId[topicId], 'prob', topicProb, 'double')
    edgeNum = 0
    for i in range(len(topicSummaryDict)):
        for j in range(len(topicSummaryDict)):
            if i != j:
                if citMatrix[i][j] >= edgeWeightThreshold:
                    if noBackwardEdge and topicIdToTimeSortedId[i] > topicIdToTimeSortedId[j]:
                        gexfGen.addEdge(topicIdToTimeSortedId[i], topicIdToTimeSortedId[j], citMatrix[i][j])
                        edgeNum += 1
    print('[dump graph file]: {0} edges'.format(edgeNum))
    graphStr = gexfGen.getGraphStr()
    gexfFile = open(gexfFilePath, 'w')
    gexfFile.write(graphStr)
    gexfFile.close()
    return


def dumpVenRankingFile(topicSummaryFilePath):
    vensDictFilePath = topicSummaryFilePath.replace('_summary', '_venDict')
    vensDictFile = open(vensDictFilePath, 'w', encoding='utf-8')
    topicSummaryDict = theme_discovery.software_based_method.readTopicSummary(topicSummaryFilePath)
    vensDict = getVenueRanking(topicSummaryDict)
    for ven in sorted(vensDict, key=lambda x: vensDict[x], reverse=True):
        vensDictFile.write('[{0:.6f}]: {1}\n'.format(vensDict[ven], ven))
    vensDictFile.close()


def printVenEntropy(topicSummaryFilePath):
    topicSummaryDict = theme_discovery.software_based_method.readTopicSummary(topicSummaryFilePath)
    print(getVenueEntropy(topicSummaryDict))


if __name__ == "__main__":
    # citMatrixFilePath = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\economic_data\\economics_citation_lda_100_119670_119670_1e-06_1e-06_timeCtrl_8_8.lda_citMatrix'
    # topicSummaryFilePath = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\economic_data\\economics_citation_lda_100_119670_119670_1e-06_1e-06_timeCtrl_8_8.lda_summary'
    citMatrixFilePath = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\management_data\\management_citation_lda_20_5119_5119_1e-06_1e-06_timeCtrl_4_4.lda_citMatrix'
    topicSummaryFilePath = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\management_data\\management_citation_lda_20_5119_5119_1e-06_1e-06_timeCtrl_4_4.lda_summary'
    citMatrix = theme_discovery.psychology_based_method.readCitMatrixSummary(citMatrixFilePath)
    topicSummaryDict = theme_discovery.psychology_based_method.readTopicSummary(topicSummaryFilePath)
    # eco = corpus.economics.getEconomicsCorpus()
    # sco = corpus.software.getSoftwareCorpus()
    # psyco = corpus.psychology.getPsychologyCorpus()
    manaco = corpus.management.getManagementCorpus()
    getTopicCitationProb(citMatrix, topicSummaryDict, manaco)

    edgeWeightThreshold = 0.0500000152126348
    dumpGraphFile(citMatrixFilePath, topicSummaryFilePath, edgeWeightThreshold)
    pass
