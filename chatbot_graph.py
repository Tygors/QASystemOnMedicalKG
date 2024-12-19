#!/usr/bin/env python3
# coding: utf-8
# File: chatbot_graph.py
# Original Author: lhy<lhy_in_blcu@126.com, https://huangyong.github.io>
# Author: Tygors
# Modified by Tygors In: 2024-12

from question_classifier import *
from question_parser import *
from answer_search import *

'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好，我是小勇医药智能助理，希望可以帮到您。如果没答上来，可联系https://liuhuanyong.github.io/。祝您身体棒棒！'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    handler = ChatBotGraph()
    while 1:
        question = input('请输入问题：') # 耳鸣和百日咳有什么并发症，推荐吃什么呢
        answer = handler.chat_main(question)
        print('小勇说：', answer)
        """
        耳鸣的症状包括：空调病；颞下颌关节病；偏头痛；上干型胸廓出口综合征；肾虚腰痛；咽鼓管阻塞；药物性耳聋；肾气不固；间断脉冲噪音损伤；脑血管痉挛；四肢
        不用；颞下颌关节紊乱综合征；乳突炎；鼻咽血管纤维瘤；百日咳；噪声性耳聋；肺不张；小儿咳嗽；咽部硬结病；维生素A摄入过多
        耳鸣宜食的食物包括有：小白菜;圆白菜;腰果;南瓜子仁;芝麻;鸡翅;樱桃番茄
        推荐食谱包括有：罗汉果雪耳鸡汤;排骨汤;黄瓜拌皮丝;紫菜芙蓉汤;冬菇油菜心;羊肉汤面;黄瓜拌兔丝;黄瓜三丝汤;可乐鸡翅;百合双耳鸡蛋羹;油豆腐油菜;紫菜鸡蛋莲草汤;清蒸鸡蛋羹;栗子鸡翅;小黄瓜凉拌面;乌药羊肉汤
        """

