#!/usr/bin/env python3
# coding: utf-8
# File: build_medicalgraph.py
# Original Author: lhy<lhy_in_blcu@126.com, https://huangyong.github.io>
# Author: Tygors
# Modified by Tygors In: 2024-12

import os
import json
from py2neo import Graph, Node
from loguru import logger
from tqdm import tqdm
from typing import List

class MedicalGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/medical.json')
        self.g = Graph(auth=("neo4j","neo4jneo4j"))
        # self.g = Graph(
        #     host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
        #     http_port=7474,  # neo4j 服务器监听的端口号
        #     user="lhy",  # 数据库user name，如果没有更改过，应该是neo4j
        #     password="lhy123")

    '''读取文件'''
    def read_nodes(self):
        # 共７类节点
        drugs = [] # 药品
        foods = [] #　食物
        checks = [] # 检查
        departments = [] #科室
        producers = [] #药品大类
        diseases: List[str] = [] #疾病
        symptoms = []#症状

        disease_infos = []#疾病信息

        # 构建节点实体关系
        rels_department = [] #　科室－科室关系
        rels_noteat = [] # 疾病－忌吃食物关系
        rels_doeat = [] # 疾病－宜吃食物关系
        rels_recommandeat = [] # 疾病－推荐吃食物关系
        rels_commonddrug = [] # 疾病－通用药品关系
        rels_recommanddrug = [] # 疾病－热门药品关系
        rels_check = [] # 疾病－检查关系
        rels_drug_producer = [] # 厂商－药物关系

        rels_symptom = [] #疾病症状关系
        rels_acompany = [] # 疾病并发关系
        rels_category = [] #　疾病与科室之间的关系


        count = 0
        for data in tqdm(open(self.data_path, encoding="utf-8")):
            disease_dict = {}
            count += 1
            # logger.info(count)

            # mongodb导出来的json文件
            data_json = json.loads(data)
            disease: str = data_json['name'] 
            disease_dict['name'] = disease # str
            diseases.append(disease)
            disease_dict['desc'] = '' # str
            disease_dict['prevent'] = '' # str
            disease_dict['cause'] = '' # str
            disease_dict['easy_get'] = '' # str
            disease_dict['cure_department'] = '' # list
            disease_dict['cure_way'] = '' # list
            disease_dict['cure_lasttime'] = '' # str
            disease_dict['symptom'] = '' # list
            disease_dict['cured_prob'] = '' # str

            if 'symptom' in data_json:
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom]) # 病和症状的关系

            if 'acompany' in data_json:
                for acompany in data_json['acompany']:
                    rels_acompany.append([disease, acompany]) # 病与并发症的关系

            if 'desc' in data_json:
                disease_dict['desc'] = data_json['desc']

            if 'prevent' in data_json:
                disease_dict['prevent'] = data_json['prevent']

            if 'cause' in data_json:
                disease_dict['cause'] = data_json['cause']

            if 'get_prob' in data_json:
                disease_dict['get_prob'] = data_json['get_prob']

            if 'easy_get' in data_json:
                disease_dict['easy_get'] = data_json['easy_get']

            if 'cure_department' in data_json:
                cure_department = data_json['cure_department']
                if len(cure_department) == 1:
                     rels_category.append([disease, cure_department[0]])
                if len(cure_department) == 2:
                    big = cure_department[0]
                    small = cure_department[1]
                    rels_department.append([small, big]) # 部门间的从属关系
                    rels_category.append([disease, small]) # 病和最小部门的关系

                disease_dict['cure_department'] = cure_department
                departments += cure_department

            if 'cure_way' in data_json:
                disease_dict['cure_way'] = data_json['cure_way']

            if  'cure_lasttime' in data_json:
                disease_dict['cure_lasttime'] = data_json['cure_lasttime']

            if 'cured_prob' in data_json:
                disease_dict['cured_prob'] = data_json['cured_prob']

            if 'common_drug' in data_json:
                common_drug = data_json['common_drug']
                for drug in common_drug:
                    rels_commonddrug.append([disease, drug]) # 病和药的关系
                drugs += common_drug

            if 'recommand_drug' in data_json:
                recommand_drug = data_json['recommand_drug']
                for drug in recommand_drug:
                    rels_recommanddrug.append([disease, drug]) # 病和推荐药的关系
                # drugs里包括普通药和推荐药
                drugs += recommand_drug

            if 'not_eat' in data_json:
                not_eat = data_json['not_eat']
                for _not in not_eat:
                    rels_noteat.append([disease, _not]) # 病和忌口的关系

                foods += not_eat
                do_eat = data_json['do_eat']
                for _do in do_eat:
                    rels_doeat.append([disease, _do]) # 病和宜吃的关系

                foods += do_eat
                recommand_eat = data_json['recommand_eat']

                for _recommand in recommand_eat:
                    rels_recommandeat.append([disease, _recommand]) # 病和推荐吃的关系
                # foods包括忌口，宜吃和推荐食谱
                foods += recommand_eat

            if 'check' in data_json:
                check = data_json['check']
                for _check in check:
                    rels_check.append([disease, _check]) # 病和检查项目的关系
                checks += check

            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail] # 左括号前的内容是生产厂家
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail] # 厂家和药品的关系
                # 生产厂家的列表
                producers += producer

            disease_infos.append(disease_dict)
        return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), disease_infos,\
               rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,\
               rels_symptom, rels_acompany, rels_category

    '''建立节点'''
    def create_node(self, label, nodes):
        logger.info(f"creating {label} nodes")
        count = 0
        for node_name in tqdm(nodes):
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            # logger.info(f"count: {count}, len(nodes): {len(nodes)}")
        return

    '''创建知识图谱中心疾病的节点'''
    def create_diseases_nodes(self, disease_infos):
        logger.info("creating diseases nodes")
        count = 0
        for disease_dict in tqdm(disease_infos):
            node = Node(
                "Disease", 
                name=disease_dict['name'], 
                desc=disease_dict['desc'],
                prevent=disease_dict['prevent'],
                cause=disease_dict['cause'],
                easy_get=disease_dict['easy_get'],
                cure_lasttime=disease_dict['cure_lasttime'],
                cure_department=disease_dict['cure_department'],
                cure_way=disease_dict['cure_way'], 
                cured_prob=disease_dict['cured_prob']
                )
            self.g.create(node)
            count += 1
            # logger.info(count)
        return

    '''创建知识图谱实体节点类型schema'''
    def create_graphnodes(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos,rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        # 第一步建立病名节点，填充其属性
        self.create_diseases_nodes(disease_infos)
        # 接下来建立一般的节点，只有name属性
        self.create_node('Drug', Drugs)
        logger.info(len(Drugs))
        self.create_node('Food', Foods)
        logger.info(len(Foods))
        self.create_node('Check', Checks)
        logger.info(len(Checks))
        self.create_node('Department', Departments)
        logger.info(len(Departments))
        self.create_node('Producer', Producers)
        logger.info(len(Producers))
        self.create_node('Symptom', Symptoms)
        logger.info(len(Symptoms))
        return


    '''创建实体关系边'''
    def create_graphrels(self):
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        # 大小科室的属于关系
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
        # 厂家生产药品的关系
        self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
        # 病名与 食物、药物（药品有生产厂家的关系）、检查、症状、并发症、诊科（科室还有大小科室的从属）等等的关系
        self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状') 
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症') # 如果并发症没有作为病名被记录过，即没有该节点，则无法建立对应关系
        self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')

    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        res = []
        logger.info(f"processing rels: {rel_name}")
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            # 二元组用###拼接
            set_edges.append('###'.join(edge))
        # 去重
        set_edges = set(set_edges)
        all = len(set_edges)
        for edge in tqdm(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            # 如果节点不存在，则不尝试建立联系
            if str(self.g.run(f"match (n:{start_node}) where n.name = '{p}' return n"))=="(No data)" or str(self.g.run(f"match (n:{end_node}) where n.name = '{q}' return n"))=="(No data)":
                continue
            # 插入关系
            try:
                self.g.run(query)
                count += 1
                res.append(f"{p}-{rel_type}-{q}")
                # logger.info(f"rel_type: {start_node}{p}-{rel_type}-{end_node}{q}, count: {count}, all:{all}")
            except Exception as e:
                logger.warning(e)
        return

    '''导出数据'''
    def export_data(self):
        # 导出后放到dict文件夹
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        f_drug = open('drug.txt', 'w+')
        f_food = open('food.txt', 'w+')
        f_check = open('check.txt', 'w+')
        f_department = open('department.txt', 'w+')
        f_producer = open('producer.txt', 'w+')
        f_symptom = open('symptoms.txt', 'w+')
        f_disease = open('disease.txt', 'w+')

        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_department.write('\n'.join(list(Departments)))
        f_producer.write('\n'.join(list(Producers)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))

        f_drug.close()
        f_food.close()
        f_check.close()
        f_department.close()
        f_producer.close()
        f_symptom.close()
        f_disease.close()

        return



if __name__ == '__main__':
    handler = MedicalGraph()
    logger.info("step1: creating nodes...")
    handler.create_graphnodes()
    logger.info("step2: creating edges...")      
    handler.create_graphrels()
    
