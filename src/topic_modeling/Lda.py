import os
import random
import sys
import time
import toolkit.utility
import corpus.historics as historics
import corpus.economics as economics
import corpus.software as software
import corpus.environment as environment
import corpus.psychology as psychology
import corpus.management as management
from corpus import finance


class LDA(object):
    K = None
    D = None
    W = None
    Alpha = None
    Beta = None
    AlphaSum = None
    BetaSum = None

    ObsDW = None
    ObsDWK = None

    ObsDK = None
    ObsWK = None
    ObsK = None

    ObsW = None
    ObsD = None
    Obs = None

    BurninIter = None
    SampliIter = None

    BurninTime = None
    SampliTime = None

    iterCtrl = None
    iter = None

    thetaEstimate = None
    phiEstimate = None
    topWeiEstimate = None

    def queryDocTopic(self, d, k, exD, exW, exK):
        x = float(self.ObsDK[d].get(k, 0.0))
        if exD == d and exK == k : x -= 1.0
        return x

    def queryWordTopic(self, w, k, exD, exW, exK):
        x = float(self.ObsWK[w].get(k, 0.0))
        if exW == w and exK == k : x -= 1.0
        return x

    def queryTopic(self, k, exD, exW, exK):
        x = float(self.ObsK.get(k, 0.0))
        if exK == k : x -= 1.0
        return x

    def multinomialSampling(self, pdf):
        x = random.random()
        i = 0
        cdf = 0.0
        while True:
            cdf += pdf[i]
            if cdf >= x : return i
            i += 1
            if i > len(pdf) : return len(pdf) - 1
        # return

    def gibbsSamplingUpdateDWK(self, d, w, k):
        # python2和3的区别 3需要加list()否则返回的是map对象，无法迭代
        terms1 = list(map(lambda i: self.Alpha[i] + self.queryDocTopic(d, i, d, w, k), range(0, self.K)))
        terms2 = list(map(lambda i: self.Beta[w] + self.queryWordTopic(w, i, d, w, k), range(0, self.K)))
        terms3 = list(map(lambda i: self.BetaSum + self.queryTopic(i, d, w, k), range(0, self.K)))
        propProb = list(map(lambda i: terms1[i] * terms2[i] / terms3[i], range(0, self.K)))
        pdf = list(map(lambda i: propProb[i] / sum(propProb), range(0, self.K)))
        newK = self.multinomialSampling(pdf)

        self.ObsDWK[d][w][k] -= 1.0
        self.ObsDWK[d][w][newK] = self.ObsDWK[d][w].get(newK, 0.0) + 1.0
        self.ObsDK[d][k] -= 1.0
        self.ObsDK[d][newK] = self.ObsDK[d].get(newK, 0.0) + 1.0
        self.ObsWK[w][k] -= 1.0
        self.ObsWK[w][newK] = self.ObsWK[w].get(newK, 0.0) + 1.0
        self.ObsK[k] -= 1.0
        self.ObsK[newK] = self.ObsK.get(newK, 0.0) + 1.0
        return

    def gibbsSamplingUpdateDW(self, d, w):
        sampQueue = {}
        for k, c in self.ObsDWK[d][w].items(): sampQueue[k] = c
        for k, c in sampQueue.items(): [self.gibbsSamplingUpdateDWK(d, w, k) for t in range(0, int(c))]
        return

    def gibbsSamplingUpdateD(self, d):
        for w in self.ObsDW[d].keys(): self.gibbsSamplingUpdateDW(d, w)
        return

    def iteration(self):
        self.iter += 1
        for d in self.ObsDW.keys(): self.gibbsSamplingUpdateD(d)
        return


    # ===============================================================================
    # sInsert: Initialization
    # ===============================================================================

    def sInsertDWK(self, d, w, k):
        if d not in self.ObsDWK : self.ObsDWK[d] = {}
        if  w not in self.ObsDWK[d]: self.ObsDWK[d][w] = {}
        self.ObsDWK[d][w][k] = self.ObsDWK[d][w].get(k, 0.0) + 1.0
        return

    def sInsertDK(self, d, k):
        if d not in self.ObsDK: self.ObsDK[d] = {}
        self.ObsDK[d][k] = self.ObsDK[d].get(k, 0.0) + 1.0
        return

    def sInsertWK(self, w, k):
        if w not in self.ObsWK: self.ObsWK[w] = {}
        self.ObsWK[w][k] = self.ObsWK[w].get(k, 0.0) + 1.0
        return

    def sInsertK(self, k):
        self.ObsK[k] = self.ObsK.get(k, 0.0) + 1.0
        return

    def sInsert(self, d, w, k):
        self.sInsertDWK(d, w, k)
        self.sInsertDK(d, k)
        self.sInsertWK(w, k)
        self.sInsertK(k)
        return

    def sInsertDW(self, d, w, c):
        if d not in self.ObsDW: self.ObsDW[d] = {}
        self.ObsDW[d][w] = float(self.ObsDW[d].get(w, 0.0) + c)
        self.ObsD[d] = self.ObsD.get(d, 0.0) + c
        self.ObsW[w] = self.ObsW.get(w, 0.0) + c
        self.Obs += c
        return

    # ===========================================================================
    # update parameter estimation
    # ===========================================================================
    def updateThetaEstimate(self):
        for d in range(self.D):
            for k in range(self.K):
                self.thetaEstimate[d][k] += (self.Alpha[k] + self.ObsDK.get(d, {}).get(k, 0.0)) / (
                            self.AlphaSum + self.ObsD.get(d, 0.0))
        return

    def updatePhiEstimate(self):
        for k in range(self.K):
            for w in range(self.W):
                self.phiEstimate[k][w] += (self.Beta[w] + self.ObsWK.get(w, {}).get(k, 0.0)) / (
                            self.BetaSum + self.ObsK.get(k, 0.0))
        return

    def updateTopWeiEstimate(self):
        for k in self.ObsK.keys(): self.topWeiEstimate[k] += self.ObsK.get(k, 0) / self.Obs
        return

    # ============================================================================
    # initialization parameters
    # ============================================================================

    def __init__(self, data, K, D, W, alpha, beta, burnIter=None, sampIter=None, burnTime=None, sampTime=None,
                 iterCtrl=None):
        print('[LDA]: Initializing and Loading Data')
        print('[LDA]: K = {0}'.format(K))
        print('[LDA]: D = {0}'.format(D))
        print('[LDA]: W = {0}'.format(W))
        print('[LDA]: data size = {0}'.format(len(data)))
        self.K = K
        self.D = D
        self.W = W
        self.Alpha = [alpha for k in range(self.K)]
        self.Beta = [beta for w in range(self.W)]
        self.AlphaSum = sum(self.Alpha)
        self.BetaSum = sum(self.Beta)

        self.ObsDW = {}
        self.ObsDWK = {}

        self.ObsDK = {}
        self.ObsWK = {}
        self.ObsK = {}

        self.ObsW = {}
        self.ObsD = {}
        self.Obs = 0.0

        self.thetaEstimate = [[0.0 for k in range(self.K)] for d in range(self.D)]
        self.phiEstimate = [[0.0 for w in range(self.W)] for k in range(self.K)]
        self.topWeiEstimate = [0.0 for k in range(self.K)]

        if iterCtrl:
            self.BurninIter = burnIter
            self.SampliIter = sampIter
            self.iterCtrl = True
        else:
            self.BurninTime = burnTime
            self.SampliTime = sampTime
            self.iterCtrl = False

        self.iter = 0

        for v in data:
            d = v[0]
            w = v[1]
            c = v[2]
            self.sInsertDW(d, w, c)  # initialize obsDW
        return

    # ===========================================================================
    # Markov Chain Monte Carlo
    # ===========================================================================
    def Mcmc(self):
        '''initialization'''
        print('[LDA]: Randomizing Topic Assignment')
        for d in self.ObsDW.keys():
            for w in self.ObsDW[d].keys():
                [self.sInsert(d, w, random.randint(0, self.K - 1))
                 for t in range(int(self.ObsDW[d][w]))]
        '''run'''
        if self.iterCtrl:
            print('[LDA]: iteration-controlled')
            # burn-in
            print('[LDA]: Burning-in ... (expected iter {0})'.format(self.BurninIter))
            print('       Progress:')
            prog = 0.0
            mil = 0.0
            step = 0.05
            timeStart = time.clock()
            for t in range(0, int(self.BurninIter)):
                prog = float(t) / self.BurninIter
                toolkit.utility.printProgressBar(prog, step)
                self.iteration()
            print('')
            timeNow = time.clock()
            hr = ((timeNow - timeStart) / 3600.0)
            print('[LDA]: Burn-in time = {0}hr'.format(hr))
            self.BurninTime = hr
            # sampling
            print('[LDA]: Sampling  ... (expected iter {0})'.format(self.SampliIter))
            print('       Progress:')
            prog = 0.0
            mil = 0.0
            step = 0.05
            timeStart = time.clock()
            for t in range(0, int(self.SampliIter)):
                prog = float(t) / self.SampliIter
                toolkit.utility.printProgressBar(prog, step)
                self.iteration()
                self.updatePhiEstimate()
                self.updateThetaEstimate()
                self.updateTopWeiEstimate()
            print('')
            timeNow = time.clock()
            hr = ((timeNow - timeStart) / 3600.0)
            print('[LDA]: Sampling time = {0}hr'.format(hr))
            self.SampliTime = hr
        else:
            self.BurninIter = 0
            self.SampliIter = 0
            print('[LDA]: time-controlled')
            # burn-in
            print('[LDA]: Burning-in ... (expected time {0}hr)'.format(self.BurninTime))
            print('       Progress:')
            prog = 0.0
            mil = 0.0
            step = 0.05
            timeStart = time.process_time()
            while (True):
                timeNow = time.process_time()
                prog = ((timeNow - timeStart) / 3600.0) / self.BurninTime
                toolkit.utility.printProgressBar(prog, step, 'iter = {0}, elapsed_time = {1}'.format(self.BurninIter,
                                                                                                     timeNow - timeStart))
                if (prog >= 1.0): break
                self.iteration()
                self.BurninIter += 1
            print('')
            print('[LDA]: Burn-in iterations = {0}'.format(self.BurninIter))
            # sampling
            print('[LDA]: Sampling ... (expected time {0}hr)'.format(self.SampliTime))
            print('       Progress:')
            prog = 0.0
            mil = 0.0
            step = 0.05
            timeStart = time.process_time()
            while True:
                timeNow = time.process_time()
                prog = ((timeNow - timeStart) / 3600.0) / self.SampliTime
                toolkit.utility.printProgressBar(prog, step, 'iter = {0}, elapsed_time = {1}'.format(self.SampliIter,
                                                                                                     timeNow - timeStart))
                if prog >= 1.0:
                    break
                print(prog)
                self.iteration()
                self.updatePhiEstimate()
                self.updateThetaEstimate()
                self.updateTopWeiEstimate()
                self.SampliIter += 1
            print('')
            print('[LDA]: Sampling iterations = {0}'.format(self.SampliIter))
        '''estimation'''
        print('[LDA]: Estimating sample averages')
        self.thetaEstimate = [toolkit.utility.normalizeVector(vec) for vec in self.thetaEstimate]
        self.phiEstimate = [toolkit.utility.normalizeVector(vec) for vec in self.phiEstimate]
        self.topWeiEstimate = toolkit.utility.normalizeVector(self.topWeiEstimate)
        print('[LDA]: End')
        '''end'''
        return (self.thetaEstimate, self.phiEstimate, self.topWeiEstimate)




# ===========================================================================
# DUMP & READ
# ===========================================================================
def dumpLdaEstimateFile(ldaInstance, dumpFilePath):
    # toolkit.utility.removePath(dumpFilePath)
    print('[LDA-util]: dump file to {0}'.format(dumpFilePath))
    dumpFile = open(dumpFilePath, 'w', encoding='utf-8')
    dumpFile.write('K = {0}\n'.format(ldaInstance.K))
    dumpFile.write('D = {0}\n'.format(ldaInstance.D))
    dumpFile.write('W = {0}\n'.format(ldaInstance.W))
    dumpFile.write('burnin_iter = {0}\n'.format(int(ldaInstance.BurninIter)))
    dumpFile.write('sampli_iter = {0}\n'.format(int(ldaInstance.SampliIter)))
    dumpFile.write('alpha: [1 * K]\n')
    dumpFile.write(' '.join([str(x) for x in ldaInstance.Alpha]) + '\n')
    dumpFile.write('beta: [1 * W]\n')
    dumpFile.write(' '.join([str(x) for x in ldaInstance.Beta]) + '\n')
    dumpFile.write('theta: [D * K]\n')
    dumpFile.write('\n'.join([' '.join([str(x) for x in vec]) for vec in ldaInstance.thetaEstimate]) + '\n')
    dumpFile.write('phi: [K * W]\n')
    dumpFile.write('\n'.join([' '.join([str(x) for x in vec]) for vec in ldaInstance.phiEstimate]) + '\n')
    dumpFile.write('topic_weight: [1 * K]\n')
    dumpFile.write(' '.join([str(x) for x in ldaInstance.topWeiEstimate]))
    dumpFile.close()
    return


def readLdaEstimateFile(dumpFilePath):
    print('[LDA-util]: read file from {0}'.format(dumpFilePath))
    dumpFile = open(dumpFilePath, 'r', encoding='utf-8')
    sys.stdout.write('\r[LDA-util]: read K, D, W                   ')
    sys.stdout.flush()
    K = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(dumpFile.readline(), 'K = '))
    D = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(dumpFile.readline(), 'D = '))
    W = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(dumpFile.readline(), 'W = '))
    sys.stdout.write('\r[LDA-util]: read burninIter, sampliIter    ')
    sys.stdout.flush()
    burninIter = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(dumpFile.readline(), 'burnin_iter = '))
    sampliIter = toolkit.utility.parseNumVal(toolkit.utility.rmLeadingStr(dumpFile.readline(), 'sampli_iter = '))
    sys.stdout.write('\r[LDA-util]: read alpha, beta               ')
    sys.stdout.flush()
    dumpFile.readline()
    (alpha, eof) = toolkit.utility.readVector(dumpFile)
    dumpFile.readline()
    (beta, eof) = toolkit.utility.readVector(dumpFile)
    sys.stdout.write('\r[LDA-util]: read {theta}                   ')
    sys.stdout.flush()
    dumpFile.readline()
    (theta, eof) = toolkit.utility.readMatrix(dumpFile, D)
    sys.stdout.write('\r[LDA-util]: read {phi}                     ')
    sys.stdout.flush()
    dumpFile.readline()
    (phi, eof) = toolkit.utility.readMatrix(dumpFile, K)
    sys.stdout.write('\r[LDA-util]: read topicWeight               ')
    sys.stdout.flush()
    dumpFile.readline()
    (topicWeight, eof) = toolkit.utility.readVector(dumpFile)
    sys.stdout.write('\r[LDA-util]: read complete                  ')
    sys.stdout.flush()
    print('')
    ldaInstance = LDA([], K, D, W, 0, 0, burninIter, sampliIter, iterCtrl=True)
    ldaInstance.thetaEstimate = theta
    ldaInstance.phiEstimate = phi
    ldaInstance.topWeiEstimate = topicWeight
    dumpFile.close()
    return ldaInstance

# 不同主题需修改文件前缀
def citationLdaRun(data, K, D, W, alpha, beta, burninTimeHr, sampliTimeHr, dumpFileFolder):
    dumpFilePath = os.path.join(dumpFileFolder, 'finance_citation_lda_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}.lda'.format(K, D, W, alpha, beta, 'timeCtrl', burninTimeHr, sampliTimeHr))
    # toolkit.utility.removePath(dumpFilePath)
    ldaInstance = LDA(data, K, D, W, alpha, beta, burnTime=burninTimeHr, sampTime=sampliTimeHr, iterCtrl=False)
    (postTheta, postPhi, topicWeights) = ldaInstance.Mcmc()
    dumpLdaEstimateFile(ldaInstance, dumpFilePath)
    return postTheta, postPhi, topicWeights

def historicsCitationLdaRun(K, BurninHr, SampliHr):
    dumpFileFolder = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\'
    # dumpFileFolder = 'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\'
    '''data loading'''
    print('[historics-citation-LDA]: loading historics')
    hc = historics.getHistoricsCorpus()
    print('[historics-citation-LDA]: indexing')
    hidToId, idToHid = historics.getCitMetaGraphHidIdMapping(hc)
    D = len(hidToId)
    print('                       size: {0}'.format(D))
    print('[historics-citation-LDA]: insert tuple (doc, wrd, cnt) to list')
    data = historics.getCitMetaGraphDocWrdCntTupleLst(hc, hidToId, idToHid)
    print('                       size: {0}'.format(len(data)))
    '''running LDA'''
    (postTheta, postPhi, topicWeights) = citationLdaRun(data, K, D, D, 1e-6, 1e-6, BurninHr, SampliHr, dumpFileFolder)


def economicsCitationLdaRun(K, BurninHr, SampliHr):
    dumpFileFolder = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\economic_data\\'
    # dumpFileFolder = 'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\'
    print('[economics-citation-LDA]: loading economics')
    ec = economics.getEconomicsCorpus()
    print('[economics-citation-LDA]: indexing')
    eidToId, idToEid = economics.getCitMetaGraphEidIdMapping(ec)
    D = len(eidToId)
    print('                       size: {0}'.format(D))
    print('[economics-citation-LDA]: insert tuple (doc, wrd, cnt) to list')
    data = economics.getCitMetaGraphDocWrdCntTupleLst(ec, eidToId, idToEid)
    print('                       size: {0}'.format(len(data)))
    '''running LDA'''
    (postTheta, postPhi, topicWeights) = citationLdaRun(data, K, D, D, 1e-6, 1e-6, BurninHr, SampliHr, dumpFileFolder)

def softwareCitationLdaRun(K, BurninHr, SampliHr):
    dumpFileFolder = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\software_data\\'
    # dumpFileFolder = 'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\'
    print('[software-citation-LDA]: loading software')
    ec = software.getSoftwareCorpus()
    print('[software-citation-LDA]: indexing')
    eidToId, idToEid = software.getCitMetaGraphEidIdMapping(ec)
    D = len(eidToId)
    print('                       size: {0}'.format(D))
    print('[software-citation-LDA]: insert tuple (doc, wrd, cnt) to list')
    data = software.getCitMetaGraphDocWrdCntTupleLst(ec, eidToId, idToEid)
    print('                       size: {0}'.format(len(data)))
    '''running LDA'''
    (postTheta, postPhi, topicWeights) = citationLdaRun(data, K, D, D, 1e-6, 1e-6, BurninHr, SampliHr,
                                                        dumpFileFolder)

def environmentCitationLdaRun(K, BurninHr, SampliHr):
    dumpFileFolder = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\environment_data\\'
    # dumpFileFolder = 'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\'
    print('[environment-citation-LDA]: loading environment')
    ec = environment.getEnvironmentCorpus()
    print('[environment-citation-LDA]: indexing')
    eidToId, idToEid = environment.getCitMetaGraphEidIdMapping(ec)
    D = len(eidToId)
    print('                       size: {0}'.format(D))
    print('[environment-citation-LDA]: insert tuple (doc, wrd, cnt) to list')
    data = environment.getCitMetaGraphDocWrdCntTupleLst(ec, eidToId, idToEid)
    print('                       size: {0}'.format(len(data)))
    '''running LDA'''
    (postTheta, postPhi, topicWeights) = citationLdaRun(data, K, D, D, 1e-6, 1e-6, BurninHr, SampliHr,
                                                        dumpFileFolder)

def psychologyCitationLdaRun(K, BurninHr, SampliHr):
    dumpFileFolder = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\psychology_data\\'
    # dumpFileFolder = 'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\'
    print('[psychology-citation-LDA]: loading psychology')
    ec = psychology.getPsychologyCorpus()
    print('[psychology-citation-LDA]: indexing')
    eidToId, idToEid = psychology.getCitMetaGraphEidIdMapping(ec)
    D = len(eidToId)
    print('                       size: {0}'.format(D))
    print('[psychology-citation-LDA]: insert tuple (doc, wrd, cnt) to list')
    data = psychology.getCitMetaGraphDocWrdCntTupleLst(ec, eidToId, idToEid)
    print('                       size: {0}'.format(len(data)))
    '''running LDA'''
    (postTheta, postPhi, topicWeights) = citationLdaRun(data, K, D, D, 1e-6, 1e-6, BurninHr, SampliHr,
                                                        dumpFileFolder)

def managementCitationLdaRun(K, BurninHr, SampliHr):
    dumpFileFolder = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\management_data\\'
    # dumpFileFolder = 'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\'
    print('[management-citation-LDA]: loading management')
    ec = management.getManagementCorpus()
    print('[management-citation-LDA]: indexing')
    eidToId, idToEid = management.getCitMetaGraphEidIdMapping(ec)
    D = len(eidToId)
    print('                       size: {0}'.format(D))
    print('[management-citation-LDA]: insert tuple (doc, wrd, cnt) to list')
    data = management.getCitMetaGraphDocWrdCntTupleLst(ec, eidToId, idToEid)
    print('                       size: {0}'.format(len(data)))
    '''running LDA'''
    (postTheta, postPhi, topicWeights) = citationLdaRun(data, K, D, D, 1e-6, 1e-6, BurninHr, SampliHr,
                                                        dumpFileFolder)

def financeCitationLdaRun(K, BurninHr, SampliHr):
    dumpFileFolder = 'E:\\study\\PycharmProjects\\lda_project\\citation_lda\\data\\finance_data\\'
    # dumpFileFolder = 'E:\\bigdata\\PycharmWorkspace\\lda_project\\citation_lda\\data\\'
    print('[finance-citation-LDA]: loading finance')
    ec = finance.getFinanceCorpus()
    print('[finance-citation-LDA]: indexing')
    eidToId, idToEid = finance.getCitMetaGraphEidIdMapping(ec)
    D = len(eidToId)
    print('                       size: {0}'.format(D))
    print('[finance-citation-LDA]: insert tuple (doc, wrd, cnt) to list')
    data = finance.getCitMetaGraphDocWrdCntTupleLst(ec, eidToId, idToEid)
    print('                       size: {0}'.format(len(data)))
    '''running LDA'''
    (postTheta, postPhi, topicWeights) = citationLdaRun(data, K, D, D, 1e-6, 1e-6, BurninHr, SampliHr,
                                                        dumpFileFolder)


if __name__ == '__main__':
    # historicsCitationLdaRun(50, 3.5, 3.5)
    economicsCitationLdaRun(100, 6, 6)
    # softwareCitationLdaRun(50, 4, 4)
    # environmentCitationLdaRun(50, 8, 8)
    # psychologyCitationLdaRun(50, 8, 8)
    # managementCitationLdaRun(20, 4, 4)
    # financeCitationLdaRun(50, 10, 10)
