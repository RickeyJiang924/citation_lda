# -*- coding:utf-8 -*-
from dbfread import DBF
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import time

class dbf_processor:
    def process(self):
        es = Elasticsearch(
            ['localhost'],
            port=9200
        )
        # outJson = open("history.json", "a", encoding="utf-8")
        table = DBF("E:/finalDesign/dbfFolder/ci_ywsy14770.dbf", encoding='gbk', char_decode_errors='ignore')
        # table1 = DBF("E:/finalDesign/dbfFolder/ci_lysy11770.dbf", encoding='gbk', char_decode_errors='ignore')
        actions = []

        s=time.time()
        # print(table.field_names)
        # print(table1.field_names)
        for record in table:
            dict={}
            for field in record:
                if not record["SNO"] and field != "JDY" and field != '_NullFlags':
                    dict[field] = record[field]
            action = {
                "_index": "historyreference",
                "_type": "papersreference",
                # "_id": record['SNO'],
                "_source": dict
            }
            actions.append(action)
            # print(action)
                # print(field, "=", record[field], end=",")
            # print()
        a = helpers.bulk(es, actions)
        e = time.time()
        print("{} {}s".format(a, e - s))
        # for field in table.fields:
        #     print(field)

        # print(table.fields[0].name)

        # for record in table:
        #     for field in record:
        #         print(field, record[field])

        print("*" * 40)


if __name__ == '__main__':
    dbf_process = dbf_processor()
    dbf_process.process()
