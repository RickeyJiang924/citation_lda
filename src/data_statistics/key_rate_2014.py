import pymysql
import pynlpir
import jieba
import re


class KeyWordRate(object):

    def gengerate_KeyDict(self):
        dict_file_path = "E:/dict/seg2014.txt"
        author_key_rate_2014_file_path = "history2014_author"
        venue_key_rate_2014_file_path = "history2014_venue"
        institution_key_rate_2014_file_path = "history2014_institution"
        stop_word_file = open('E:/finalDesign/citation_lda/references/stopwords.txt', 'r', encoding='utf-8')
        stopwords = stop_word_file.read().splitlines()
        jieba.load_userdict(dict_file_path)

        # key_rate_file = open(key_rate_2014_file_path, 'w', encoding="utf-8")

        db = pymysql.connect("localhost", "root", "", "history")
        cursor = db.cursor()
        cursor2 = db.cursor()
        sql = "SELECT SNO,LYPM,QKNO,NIAN FROM ci_lysy14770"
        sql2 = "SELECT ZZMC,JGMC FROM ci_lyzz14770 WHERE SNO=%s"

        authorDic = {}
        venueDict = {}
        institutionDict = {}
        yearDict = {}

        pynlpir.open()

        try:
            cursor.execute(sql)
            paperResults = cursor.fetchall()
            for paper in paperResults:
                sno = paper[0]
                title = paper[1]
                venueNo = paper[2]
                year = paper[3]

                cursor2.execute(sql2, sno)
                paperAuthors = cursor2.fetchall()
                authors = []
                institutions = []
                for author in paperAuthors:
                    authors.append(author[0])
                    institutions.append(author[1])

                title = re.sub("[\s+\.\!\/_,$%^*()+\"\']+|[+——！，。？、~@#￥%……&*（）《》・“”―]", "", title)
                split = list(jieba.cut(title, cut_all=False))
                for each_split in split:
                    if each_split in stopwords:
                        split.remove(each_split)
                nounList = split
                # nounList = []
                # for eachSplit in split:
                #     if eachSplit[1] == "noun":
                #         nounList.append(eachSplit[0])
                # print(sno,":",nounList)
                if len(nounList) > 0:
                    for noun in nounList:
                        if len(authors) > 0:
                            for singleAuthor in authors:
                                authorDic.setdefault(noun, []).append(singleAuthor)

                        if len(institutions) > 0:
                            for singleInstitution in institutions:
                                institutionDict.setdefault(noun, []).append(singleInstitution)

                        venueDict.setdefault(noun, []).append(venueNo)
                        yearDict.setdefault(noun, []).append(year)
        except:
            print("Error: unable to fetch data")

        db.close()

        # statisticAuthorFile=open("key-words-Author-2010", "a", encoding="utf-8")
        # for each_author in authorDic:
        #     statisticAuthorFile.write(each_author)
        #     statisticAuthorFile.write(":")
        #     for author_name in authorDic[each_author]:
        #         if author_name!=None:
        #             statisticAuthorFile.write(author_name)
        #             statisticAuthorFile.write(",")
        #     statisticAuthorFile.write("\n")
        # statisticAuthorFile.close()

        statisticAuthorNumFile = open(author_key_rate_2014_file_path, "a", encoding="utf-8")
        for each_author in authorDic:
            statisticAuthorNumFile.write(each_author)
            statisticAuthorNumFile.write("@@")
            length = len(authorDic[each_author])
            statisticAuthorNumFile.write((length.__str__()))
            statisticAuthorNumFile.write("@@")
            authorNameNumDict = {}
            for authorName in authorDic[each_author]:
                if authorName in authorNameNumDict:
                    authorNameNumDict[authorName] = authorNameNumDict[authorName] + 1
                else:
                    authorNameNumDict[authorName] = 1
            for dd in authorNameNumDict:
                if dd != None:
                    statisticAuthorNumFile.write(dd)
                    statisticAuthorNumFile.write(":")
                    statisticAuthorNumFile.write(authorNameNumDict[dd].__str__())
                    statisticAuthorNumFile.write(";")
            statisticAuthorNumFile.write("\n")
        statisticAuthorNumFile.close()



        statisticVenueNumFile = open(venue_key_rate_2014_file_path, "a", encoding="utf-8")
        for each_venue in venueDict:
            statisticVenueNumFile.write(each_venue)
            statisticVenueNumFile.write("@@")
            length = len(venueDict[each_venue])
            statisticVenueNumFile.write((length.__str__()))
            statisticVenueNumFile.write("@@")
            venueNoNumDict = {}
            for venueNoSta in venueDict[each_venue]:
                if venueNoSta in venueNoNumDict:
                    venueNoNumDict[venueNoSta] = venueNoNumDict[venueNoSta] + 1
                else:
                    venueNoNumDict[venueNoSta] = 1
            for dd in venueNoNumDict:
                if dd != None:
                    statisticVenueNumFile.write(dd)
                    statisticVenueNumFile.write(":")
                    statisticVenueNumFile.write(venueNoNumDict[dd].__str__())
                    statisticVenueNumFile.write(";")
            statisticVenueNumFile.write("\n")
        statisticVenueNumFile.close()



        statisticInstitutionNumFile = open(institution_key_rate_2014_file_path, "a", encoding="utf-8")
        for each_institution in institutionDict:
            statisticInstitutionNumFile.write(each_institution)
            statisticInstitutionNumFile.write("@@")
            length = len(institutionDict[each_institution])
            statisticInstitutionNumFile.write((length.__str__()))
            statisticInstitutionNumFile.write("@@")
            institutionNumDict = {}
            for institutionSta in institutionDict[each_institution]:
                if institutionSta in institutionNumDict:
                    institutionNumDict[institutionSta] = institutionNumDict[institutionSta] + 1
                else:
                    institutionNumDict[institutionSta] = 1
            for dd in institutionNumDict:
                if dd != None:
                    statisticInstitutionNumFile.write(dd)
                    statisticInstitutionNumFile.write(":")
                    statisticInstitutionNumFile.write(institutionNumDict[dd].__str__())
                    statisticInstitutionNumFile.write(";")
            statisticInstitutionNumFile.write("\n")
        statisticInstitutionNumFile.close()


if __name__ == '__main__':
    generate = KeyWordRate()
    generate.gengerate_KeyDict()
