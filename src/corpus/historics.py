# @author: RickeyJiang
# @date: 2019/3/11
import sys

import toolkit.utility
import re
import os

class Historics(object):
    docs = None
    numDocs = None
    metaDataFilePath = None
    citFilePath = None
    citeMetaGraph = None

    def __init__(self, metaDataFilePath=None, citFilePath=None):
        self.docs = {}
        self.metaDataFilePath = metaDataFilePath
        self.citFilePath = citFilePath
        if self.metaDataFilePath is not None: self.readMetaDataFile()
        if self.citFilePath is not None: self.readCitationFile()

    def readMetaDataFile(self):
        metaDict = readMetaFile(self.metaDataFilePath)
        cnt = 0
        for Hid in metaDict:
            if Hid not in self.docs: self.docs[Hid] = {}
            self.docs[Hid].update(metaDict[Hid])
            cnt += 1
        self.numDocs = len(self.docs)
        print('[historics] MetaData {0} entries (#Hid)'.format(cnt))
        return

    def readCitationFile(self):
        citeMetaGraph, citDict = readCitationFile(self.citFilePath)
        self.citeMetaGraph = citeMetaGraph
        cnt = 0
        for Hid in citDict:
            if Hid in self.docs:
                self.docs[Hid]['citLst'] = citDict[Hid]
                cnt += 1
        print('[Historics] citations {0} entries (#citing paper)'.format(cnt))
        print('[Historics] citing docs {0} (#edges)'.format(len(self.citeMetaGraph)))
        # reportCiteMetaGraph(self.citeMetaGraph)
        return

NOT_FOLD = True


# ===============================================================================
# metaDict[Hid] = {'Hid': Hid, 'title': title,'year': year}
# ===============================================================================
def readMetaFile(metaFilePath):
    metaFile = open(metaFilePath, 'r', encoding='utf-8')
    metaDict = {}
    eof = False
    while not eof:
        (lines, eof) = toolkit.utility.readLines(5, metaFile)
        Hid = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(lines[0], 'id = '))
        author = toolkit.utility.rmLeadingStr(lines[1], 'author = ')
        title = toolkit.utility.rmLeadingStr(lines[2], 'title = ')
        year = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(lines[3], 'year = '))
        metaDict[Hid] = {'Hid': Hid, 'author': author, 'title': title, 'year': year}
    metaFile.close()
    return metaDict


# ===============================================================================
# (citeMetaGraph, citDict)
# citDict[citingDocHid].append({'citingDocHid':citingDocHid, 'citedDocHid':citedDocHid, 'coCitedDocHidLst':coCitedDocHidLst, 'txt':txt})
# ===============================================================================
def readCitationFile(citationFilePath):
    citFile = open(citationFilePath, 'r', encoding='utf-8')
    citDict = {}
    citeMetaGraph = {}
    eof = False
    while not eof:
        (lines, eof) = toolkit.utility.readLines(4, citFile)
        citingDocHid = toolkit.utility.parseNumVal(lines[0])
        citedDocHid = toolkit.utility.parseNumVal(lines[1])
        # coCitedDocHidLst = [toolkit.utility.parseNumVal(part) for part in lines[2].strip('[]').split(',')]
        # 暂时设置共同被引用的list为空
        coCitedDocHidLst = []
        # txt = lines[3]
        if citingDocHid not in citDict:
            citDict[citingDocHid] = []
        citDict[citingDocHid].append(
            {'citingDocHid': citingDocHid, 'citedDocHid': citedDocHid, 'coCitedDocHidLst': coCitedDocHidLst})
        if citingDocHid not in citeMetaGraph:
            citeMetaGraph[citingDocHid] = {}
        if citedDocHid not in citeMetaGraph[citingDocHid]:
            citeMetaGraph[citingDocHid][citedDocHid] = 0
        citeMetaGraph[citingDocHid][citedDocHid] += 1
    return citeMetaGraph, citDict

# ===============================================================================
# Historics Utility
# ===============================================================================
#  从多行文本匹配 id = {...}  中的内容
HidReg = re.compile('id = (.*?)', re.MULTILINE)
authorReg = re.compile('author = (.*?)', re.MULTILINE)
titleReg = re.compile('title = (.*?)', re.MULTILINE)
yearReg = re.compile('year = (.*?)', re.MULTILINE)


def reportCiteMetaGraph(citeMetaGraph):
    # citingDocHist = {}
    # citingCntHist = {}
    # for citingDocId in citeMetaGraph:
    #     citingDoc = len(citeMetaGraph[citingDocId])
    #     citingCnt = sum(citeMetaGraph[citingDocId].values())
    #     if citingDoc not in citingDocHist: citingDocHist[citingDoc] = 0
    #     if citingCnt not in citingCntHist: citingCntHist[citingCnt] = 0
    #     citingDocHist[citingDoc] += 1
    #     citingCntHist[citingCnt] += 1
    # m = max(max(citingDocHist.keys()), max(citingCntHist.keys()))
    # print('[Historics Citing Meta Graph]: report:')
    # print('                          : {0:<20}{1:<20}{2:<20}'.format('i', 'citingDocHist[i]', 'citingCntHist[i]'))
    # for i in range(m):
    #     if (i in citingDocHist) or (i in citingCntHist):
    #         print('                          : {0:<20}{1:<20}{2:<20}'.format(i, citingDocHist.get(i, 0),
    #                                                                          citingCntHist.get(i, 0)))
    # return
    for i in citeMetaGraph.keys():
        print('i:', i, 'citing:', citeMetaGraph[i])


def generateMetaFile(sourceFilePath, metaFilePath):
    metaFile = open(metaFilePath, 'w', encoding='utf-8')
    cnt = 0
    exceptCnt = 0
    file = open(sourceFilePath, 'r')
    while 1:
        txt = ''.join(file.readlines(5))
        if not txt:
            file.close()
            break
        # txt = '\n'.join(file.readlines())

        # id字段不存在
        if not HidReg.search(txt):
            print("{0}: [{2}] {1}".format(exceptCnt, sourceFilePath, "no-Hid"))
            exceptCnt += 1
            continue
        Hid = toolkit.utility.parseNumVal(HidReg.search(txt).group(1))

        # author字段不存在
        if not HidReg.search(txt):
            print("{0}: [{2}] {1}".format(exceptCnt, sourceFilePath, "no-author"))
            exceptCnt += 1
            continue
        author = toolkit.utility.parseNumVal(authorReg.search(txt).group(1))

        # title字段不存在
        if not titleReg.search(txt):
            print("{0}: [{2}] {1}".format(exceptCnt, sourceFilePath, "no-title"))
            exceptCnt += 1
        title = titleReg.search(txt).group(1)

        # year字段不存在
        if not titleReg.search(txt):
            print("{0}: [{2}] {1}".format(exceptCnt, sourceFilePath, "no-year"))
            exceptCnt += 1
        year = yearReg.search(txt).group(1)

        metaFile.write('Hid = {0}\n'.format(Hid))
        metaFile.write('author = {0}\n'.format(author))
        metaFile.write('title = {0}\n'.format(title))
        metaFile.write('year = {0}\n'.format(year))
        metaFile.write('\n')
        cnt += 1
    metaFile.close()
    print('[Historics-metadata] processing {0} docs'.format(cnt))
    print('[Historics-metadata] Exception Doc: {0}'.format(exceptCnt))
    return


def generateCitFile(citationFilePath, citFilePath):

    citFile = open(citFilePath, 'w', encoding='utf-8')

    citFile.close()
    print('')
    citFile.close()
    return


# ===============================================================================
# API
# ===============================================================================
def getHistoricsCorpus(metaDataFilePath='E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\test_metadata_file.txt',
                    citFilePath='E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\test_citation_file.txt'):
    return Historics(metaDataFilePath, citFilePath)


# ===============================================================================
# Citation-based
# ===============================================================================
def getCitMetaGraphHidIdMapping(hd):
    HidToId = {}
    idToHid = {}
    id = 0
    for citingDocHid in hd.citeMetaGraph:
        if citingDocHid not in HidToId:
            HidToId[citingDocHid] = id
            idToHid[id] = citingDocHid
            id += 1
        for citedDocHid in hd.citeMetaGraph[citingDocHid]:
            if citedDocHid not in HidToId:
                HidToId[citedDocHid] = id
                idToHid[id] = citedDocHid
                id += 1
    return HidToId, idToHid


def getCitMetaGraphDocWrdCntTupleLst(hd, HidToId, idToHid):
    data = []
    for citingDocHid in hd.citeMetaGraph:
        for citedDocHid in hd.citeMetaGraph[citingDocHid]:
            data.append(
                (HidToId[citingDocHid], HidToId[citedDocHid], hd.citeMetaGraph[citingDocHid][citedDocHid]))
    return data



# ===============================================================================
# Content-based
# ===============================================================================
def getContentFreqWrdCntDict(hd, contentField='abstract'):
    freqWrdCntDict = {}
    for Hid in hd.docs:
        toks = (hd.docs[Hid][contentField]).split()
        for tok in toks: freqWrdCntDict[tok] = freqWrdCntDict.get(tok, 0) + 1
    return freqWrdCntDict


def getContentTokIdMapping(hd, freqWrdCntDict=None, threshold=None, contentField='abstract'):
    tokToId = {}
    idToTok = {}
    for Hid in hd.docs:
        toks = (hd.docs[Hid][contentField]).split()
        for tok in toks:
            if tok not in tokToId:
                if (freqWrdCntDict is not None) and (freqWrdCntDict[tok] < threshold): continue
                id = len(tokToId)
                tokToId[tok] = id
                idToTok[id] = tok
    return tokToId, idToTok


def getContentHidIdMapping(hd):
    HidToId = {}
    idToHid = {}
    for Hid in hd.docs:
        if Hid not in HidToId:
            id = len(HidToId)
            HidToId[Hid] = id
            idToHid[id] = Hid
    return HidToId, idToHid


def getContentDocWrdCntTupleLst(hd, tokToId, idToTok, HidToId, idToHid, freqWrdCntDict=None, threshold=None,
                                contentField='abstract'):
    data = []
    for Hid in hd.docs:
        doc = HidToId[Hid]
        wrdCntDict = {}
        for tok in (hd.docs[Hid][contentField]).split():
            if (freqWrdCntDict is not None) and (freqWrdCntDict[tok] < threshold): continue
            wrdCntDict[tokToId[tok]] = wrdCntDict.get(tokToId[tok], 0) + 1
        for wrd in wrdCntDict: data.append((doc, wrd, wrdCntDict[wrd]))
    return data


# ===============================================================================
# TEST
# ===============================================================================
if __name__ == '__main__':
    # HistoricsFolderPathA_B = os.path.join(variables.DATA_DIR, 'Historics/Historics')
    # HistoricsFolderPathC_H = os.path.join(variables.DATA_DIR, 'Historics/HistoricsC-H')
    # HistoricsFolderPathI_N = os.path.join(variables.DATA_DIR, 'Historics/HistoricsI-N')
    # HistoricsFolderPathO_Z = os.path.join(variables.DATA_DIR, 'Historics/HistoricsO-Z')
    #
    # HistoricsCitContextFilePathA_B = os.path.join(variables.DATA_DIR, 'Historics/ContextOutputA-B.txt')
    # HistoricsCitContextFilePathC_H = os.path.join(variables.DATA_DIR, 'Historics/ContextOutputC-H.txt')
    # HistoricsCitContextFilePathI_N = os.path.join(variables.DATA_DIR, 'Historics/ContextOutputI-N.txt')
    # HistoricsCitContextFilePathO_Z = os.path.join(variables.DATA_DIR, 'Historics/ContextOutputO-Z.txt')
    #
    # HistoricsFolderPathLst = [HistoricsFolderPathA_B, HistoricsFolderPathC_H, HistoricsFolderPathI_N, HistoricsFolderPathO_Z]
    # HistoricsCitContextFilePathLst = [HistoricsCitContextFilePathA_B, HistoricsCitContextFilePathC_H,
    #                                HistoricsCitContextFilePathI_N, HistoricsCitContextFilePathO_Z]
    #
    # metaDataFilePath = os.path.join(variables.DATA_DIR, 'Historics/Historics_metadata.txt')
    # citFilePath = os.path.join(variables.DATA_DIR, 'Historics/Historics_citation.txt')
    # absFilePath = os.path.join(variables.DATA_DIR, 'Historics/Historics_abstract.txt')

    # ===========================================================================
    # Generate the MetaDataFile
    # ===========================================================================
    #    generateMetaFile(HistoricsFolderPathLst, metaDataFilePath)

    # ===========================================================================
    # Generate Citation File
    # ===========================================================================
    #    generateCitFile(readMetaFile(metaDataFilePath), HistoricsCitContextFilePathLst, citFilePath)

    # ===========================================================================
    # Generate Abstract File
    # ===========================================================================
    #    generateAbstractDataset(HistoricsFolderPathLst)
    #    generateAbstractFile(metaDataFilePath, citFilePath, absFilePath)

    # ===========================================================================
    # Historics Corpus
    # ===========================================================================
    # his = Historics('E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\test_metadata_file.txt',
    #                     'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\test_citation_file.txt')

    # ===========================================================================
    # API Example
    # ===========================================================================
    hd = getHistoricsCorpus()
    hidToId, idToHid = getCitMetaGraphHidIdMapping(hd)
    print(len(hidToId))
    d = getCitMetaGraphDocWrdCntTupleLst(hd, hidToId, idToHid)
    print(len(d))

    pass
