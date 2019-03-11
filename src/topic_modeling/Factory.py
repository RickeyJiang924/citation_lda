import sys
import re
import random

class Factory(object):
    corpus = None;
    metadata = None;

    def readCitationFile(self, fileName):
        self.corpus = Corpus();
        infile = open(fileName, 'r', encoding='utf-8');

        for line in infile:
            parts = line.split("==>");
            citingP = parts[0].strip();
            citedP = parts[1].strip();
            self.corpus.insertCitation(citingP, citedP);

        print(len(self.corpus.docs));
        infile.close();

    def readMetadataFile(self, fileName):
        self.metadata = {};
        infile = open(fileName, 'r', encoding='utf-8');

        text = '';
        for line in infile:
            text += line;
            if len(line.strip()) == 0:
                text = text.strip();
                if text:
                    mtdt = MetaData.extractFromStringAndConvert(text);
                    self.metadata[mtdt.id] = mtdt;
                    text = '';
        text = text.strip();
        if text:
            mtdt = MetaData.extractFromStringAndConvert(text);
            self.metadata[mtdt.id] = mtdt;
            # text = '';

        infile.close();
        return self.metadata;

    def matchFileWithMetadata(self, fileName):
        infile = open(fileName, 'r');
        outfile = open(fileName + '.meta', 'w', encoding='utf-8');
        regId = re.compile('\((.*?)\)');
        nomatch = 0;
        for line in infile:
            outfile.write(line);
            mId = regId.search(line);
            if mId:
                id = mId.group(1);
                if id in self.metadata:
                    outfile.write(str(self.metadata[id].title) + '\n');
                else:
                    nomatch += 1;
        infile.close();
        outfile.close();
        print('No Match Num: {0}'.format(nomatch));

    def __init__(self):
        """
        construct method
        to be continued...
        """


# 元数据
class MetaData(object):
    id = None;
    author = None;
    title = None;
    year = None;

    #  从多行文本匹配 id = {...}  中的内容
    idReg = re.compile('id = (.*?)', re.MULTILINE);
    authorReg = re.compile('author = (.*?)', re.MULTILINE);
    titleReg = re.compile('title = (.*?)', re.MULTILINE);
    yearReg = re.compile('year = (.*?)', re.MULTILINE);

    @staticmethod
    def extractFromStringAndConvert(text):
        mId = MetaData.idReg.search(text);
        id = mId.group(1);
        mAuthor = MetaData.authorReg.search(text);
        author = mAuthor.group(1);
        mTitle = MetaData.titleReg.search(text);
        title = mTitle.group(1);
        mYear = MetaData.yearReg.search(text);
        if mYear is not None:
            year = mYear.group(1);
        else:
            year = 'unknown'
        return MetaData(id, author, title, year)

    def __init__(self, id, author, title, year):
        self.id = id;
        self.author = author;
        self.title = title;
        self.year = year;


# 语料库
class Corpus(object):
    docs = [];
    docsNameToId = {};
    docsIdToName = {};

    def parseDocName(self, docName):
        # A00-1001
        conf = docName[0];
        biparts = docName[1:].split('-');
        year = biparts[0];
        idx = biparts[1];
        return {'docName': docName, 'conf': conf, 'year': year, 'idx': idx, 'cite': []};

    # 建立id-name和name-id双重字典
    def insertDoc(self, docName):
        if docName not in self.docsNameToId:
            id = len(self.docsNameToId);
            self.docsNameToId[docName] = id;
            self.docsIdToName[id] = docName;
            self.docs.append({'docName':docName, 'cite':[]});

    # 语料库增加文章，并在引用文章的cite属性里添加被引用的文章
    def insertCitation(self, citingPaperName, citedPaperName):
        self.insertDoc(citingPaperName);
        self.insertDoc(citedPaperName);
        citingPaperId = self.getDocId(citingPaperName);
        citedPaperId = self.getDocId(citedPaperName);
        self.docs[citingPaperId]['cite'].append(citedPaperId);

    def getDocId(self, docName):
        return self.docsNameToId[docName];

    def getDocName(self, docId):
        return self.docsIdToName[docId];


def dump(pTheta, pPhi, topicWeights, D, K, pThetaFileName, pPhiFileName, topicWeightFileName, corpus):
    pThetaFile = open(pThetaFileName, 'w');
    for d in range(0, D):
        line = "[" + str(corpus.docsIdToName[d]) + "]\n";
        for k in range(0, K):
            line += "(" + str(k) + "):" + str(pTheta[d][k]) + "\n";
        pThetaFile.write(line + "\n");
    pThetaFile.close();

    pPhiFile = open(pPhiFileName, 'w');
    for k in range(0, K):
        line = "[" + str(k) + "]\n";
        hmap = {};
        for d in range(0, D):
            hmap[corpus.docsIdToName[d]] = pPhi[k][d];
        for docName in sorted(hmap.keys(), key=lambda x: -hmap[x]):
            line += "(" + str(docName) + "):" + str(hmap[docName]) + "\n";
        pPhiFile.write(line + "\n");
    pPhiFile.close();

    topicWeightFile = open(topicWeightFileName, 'w');
    for k in range(0, K): topicWeightFile.write('[' + str(k) + ']:\t' + str(topicWeights[k]) + "\n");
    topicWeightFile.close();


def kMeansDump(topics, topicFileName, corpus):
    topicFile = open(topicFileName, 'w');
    for k in range(0, len(topics)):
        topicFile.write('[' + str(k) + ']\n');
        for docId in topics[k]: topicFile.write('(' + str(corpus.docsIdToName[docId]) + ')' + '\n');
        topicFile.write('\n');

def randomNumberGeneration(d, k):
    arr = [[random.uniform(0,100) for j in range(0, k)] for i in range(0, d)]
    return arr

def topicWeightGeneration(k):
    arr = [1/k for i in range(0, k)]
    return arr

if __name__ == '__main__':
    factory = Factory()
    # print(randomNumberGeneration(10, 5))
    factory.readCitationFile('E:\\bigdata\\PycharmWorkspace\\lda_project\\data\\test_citation_file.txt')
    metadata_obj = factory.readMetadataFile('E:\\bigdata\\PycharmWorkspace\\lda_project\\data\\test_metadata_file.txt')
    d = len(factory.corpus.docs)
    k = 100
    p_theta = randomNumberGeneration(d, k)
    p_phi = randomNumberGeneration(k, d)
    topic_weights = topicWeightGeneration(k)
    # print(factory.corpus.docs)
    dump(p_theta, p_phi, topic_weights, d, k,
         'E:\\bigdata\\PycharmWorkspace\\lda_project\\data\\test_theta_file.txt',
         'E:\\bigdata\\PycharmWorkspace\\lda_project\\data\\test_phi_file.txt',
         'E:\\bigdata\\PycharmWorkspace\\lda_project\\data\\test_topic_weight_file.txt',
         factory.corpus)




