# @author: RickeyJiang
# @date: 2019/3/11
import sys

import toolkit.utility
import re
import os

class Psychology(object):
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
        for Eid in metaDict:
            if Eid not in self.docs: self.docs[Eid] = {}
            self.docs[Eid].update(metaDict[Eid])
            cnt += 1
        self.numDocs = len(self.docs)
        print('[Psychology] MetaData {0} entries (#Eid)'.format(cnt))
        return

    def readCitationFile(self):
        citeMetaGraph, citDict = readCitationFile(self.citFilePath)
        self.citeMetaGraph = citeMetaGraph
        cnt = 0
        for Eid in citDict:
            if Eid in self.docs:
                self.docs[Eid]['citLst'] = citDict[Eid]
                cnt += 1
        print('[Psychology] citations {0} entries (#citing paper)'.format(cnt))
        print('[Psychology] citing docs {0} (#edges)'.format(len(self.citeMetaGraph)))
        # reportCiteMetaGraph(self.citeMetaGraph)
        return

NOT_FOLD = True


# ===============================================================================
# metaDict[Eid] = {'Eid': Eid, 'title': title,'year': year}
# ===============================================================================
def readMetaFile(metaFilePath):
    metaFile = open(metaFilePath, 'r', encoding='utf-8')
    metaDict = {}
    eof = False
    # excp = 0
    while not eof:
        (lines, eof) = toolkit.utility.readLines(5, metaFile)
        Eid = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(lines[0], 'id = '))
        author = toolkit.utility.rmLeadingStr(lines[1], 'author = ')
        title = toolkit.utility.rmLeadingStr(lines[2], 'title = ')
        year = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(lines[3], 'year = '))
        metaDict[Eid] = {'Eid': Eid, 'author': author, 'title': title, 'year': year}
        print(metaDict[Eid])
    metaFile.close()
    return metaDict


# ===============================================================================
# (citeMetaGraph, citDict)
# citDict[citingDocEid].append({'citingDocEid':citingDocEid, 'citedDocEid':citedDocEid, 'coCitedDocEidLst':coCitedDocEidLst, 'txt':txt})
# ===============================================================================
def readCitationFile(citationFilePath):
    citFile = open(citationFilePath, 'r', encoding='utf-8')
    citDict = {}
    citeMetaGraph = {}
    eof = False
    while not eof:
        (lines, eof) = toolkit.utility.readLines(4, citFile)
        citingDocEid = toolkit.utility.parseNumVal(lines[0])
        citedDocEid = toolkit.utility.parseNumVal(lines[1])
        # coCitedDocEidLst = [toolkit.utility.parseNumVal(part) for part in lines[2].strip('[]').split(',')]
        # 暂时设置共同被引用的list为空
        coCitedDocEidLst = []
        # txt = lines[3]
        if citingDocEid not in citDict:
            citDict[citingDocEid] = []
        citDict[citingDocEid].append(
            {'citingDocEid': citingDocEid, 'citedDocEid': citedDocEid, 'coCitedDocEidLst': coCitedDocEidLst})
        if citingDocEid not in citeMetaGraph:
            citeMetaGraph[citingDocEid] = {}
        if citedDocEid not in citeMetaGraph[citingDocEid]:
            citeMetaGraph[citingDocEid][citedDocEid] = 0
        citeMetaGraph[citingDocEid][citedDocEid] += 1
    return citeMetaGraph, citDict

# ===============================================================================
# Psychology Utility
# ===============================================================================
#  从多行文本匹配 id = {...}  中的内容
EidReg = re.compile('id = (.*?)', re.MULTILINE)
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
    # print('[Psychology Citing Meta Graph]: report:')
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
        if not EidReg.search(txt):
            print("{0}: [{2}] {1}".format(exceptCnt, sourceFilePath, "no-Eid"))
            exceptCnt += 1
            continue
        Eid = toolkit.utility.parseNumVal(EidReg.search(txt).group(1))

        # author字段不存在
        if not EidReg.search(txt):
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

        metaFile.write('Eid = {0}\n'.format(Eid))
        metaFile.write('author = {0}\n'.format(author))
        metaFile.write('title = {0}\n'.format(title))
        metaFile.write('year = {0}\n'.format(year))
        metaFile.write('\n')
        cnt += 1
    metaFile.close()
    print('[Psychology-metadata] processing {0} docs'.format(cnt))
    print('[Psychology-metadata] Exception Doc: {0}'.format(exceptCnt))
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
# def getPsychologyCorpus(metaDataFilePath='E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\psychology_metadata_file.txt',
#                     citFilePath='E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\psychology_citation_file.txt'):
#     return Psychology(metaDataFilePath, citFilePath)

def getPsychologyCorpus(metaDataFilePath='E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\psychology_data\\psychology_metadata_file.txt',
                    citFilePath='E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\psychology_data\\psychology_citation_file.txt'):
    return Psychology(metaDataFilePath, citFilePath)


# ===============================================================================
# Citation-based
# ===============================================================================
def getCitMetaGraphEidIdMapping(ed):
    EidToId = {}
    idToEid = {}
    id = 0
    for citingDocEid in ed.citeMetaGraph:
        if citingDocEid not in EidToId:
            EidToId[citingDocEid] = id
            idToEid[id] = citingDocEid
            id += 1
        for citedDocEid in ed.citeMetaGraph[citingDocEid]:
            if citedDocEid not in EidToId:
                EidToId[citedDocEid] = id
                idToEid[id] = citedDocEid
                id += 1
    return EidToId, idToEid


def getCitMetaGraphDocWrdCntTupleLst(ed, EidToId, idToEid):
    data = []
    for citingDocEid in ed.citeMetaGraph:
        for citedDocEid in ed.citeMetaGraph[citingDocEid]:
            data.append(
                (EidToId[citingDocEid], EidToId[citedDocEid], ed.citeMetaGraph[citingDocEid][citedDocEid]))
    return data



# ===============================================================================
# Content-based
# ===============================================================================
def getContentFreqWrdCntDict(ed, contentField='abstract'):
    freqWrdCntDict = {}
    for Eid in ed.docs:
        toks = (ed.docs[Eid][contentField]).split()
        for tok in toks: freqWrdCntDict[tok] = freqWrdCntDict.get(tok, 0) + 1
    return freqWrdCntDict


def getContentTokIdMapping(ed, freqWrdCntDict=None, threshold=None, contentField='abstract'):
    tokToId = {}
    idToTok = {}
    for Eid in ed.docs:
        toks = (ed.docs[Eid][contentField]).split()
        for tok in toks:
            if tok not in tokToId:
                if (freqWrdCntDict is not None) and (freqWrdCntDict[tok] < threshold): continue
                id = len(tokToId)
                tokToId[tok] = id
                idToTok[id] = tok
    return tokToId, idToTok


def getContentEidIdMapping(ed):
    EidToId = {}
    idToEid = {}
    for Eid in ed.docs:
        if Eid not in EidToId:
            id = len(EidToId)
            EidToId[Eid] = id
            idToEid[id] = Eid
    return EidToId, idToEid


def getContentDocWrdCntTupleLst(ed, tokToId, idToTok, EidToId, idToEid, freqWrdCntDict=None, threshold=None,
                                contentField='abstract'):
    data = []
    for Eid in ed.docs:
        doc = EidToId[Eid]
        wrdCntDict = {}
        for tok in (ed.docs[Eid][contentField]).split():
            if (freqWrdCntDict is not None) and (freqWrdCntDict[tok] < threshold): continue
            wrdCntDict[tokToId[tok]] = wrdCntDict.get(tokToId[tok], 0) + 1
        for wrd in wrdCntDict: data.append((doc, wrd, wrdCntDict[wrd]))
    return data


# ===============================================================================
# TEST
# ===============================================================================
if __name__ == '__main__':
    # ===========================================================================
    # Generate the MetaDataFile
    # ===========================================================================
    #    generateMetaFile(PsychologyFolderPathLst, metaDataFilePath)

    # ===========================================================================
    # Generate Citation File
    # ===========================================================================
    #    generateCitFile(readMetaFile(metaDataFilePath), PsychologyCitContextFilePathLst, citFilePath)

    # ===========================================================================
    # Generate Abstract File
    # ===========================================================================
    #    generateAbstractDataset(PsychologyFolderPathLst)
    #    generateAbstractFile(metaDataFilePath, citFilePath, absFilePath)

    # ===========================================================================
    # Psychology Corpus
    # ===========================================================================
    # his = Psychology('E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\psychology_metadata_file.txt',
    #                     'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\psychology_citation_file.txt')

    # ===========================================================================
    # API Example
    # ===========================================================================
    ed = getPsychologyCorpus()
    print(ed.readCitationFile())
    # eidToId, idToEid = getCitMetaGraphEidIdMapping(ed)
    # print(idToEid[87944])
    # # print(ed.docs[87944]['title'])
    # print(len(eidToId))
    # d = getCitMetaGraphDocWrdCntTupleLst(ed, eidToId, idToEid)
    # print(len(d))

    pass
