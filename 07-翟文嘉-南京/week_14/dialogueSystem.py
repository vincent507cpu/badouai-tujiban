import copy
import pandas
import os
import json
import re

"""

任务型对话系统
基于场景文件和填槽模板
完成多轮对话

memory中包含的关键字：
user_query 用户提出的问题
available_nodes  记录当当前可以访问的节点
hit_node  命中的节点
hit_score 命中的分数
lack_slot_info 当前欠缺的槽位
dialogue_state  True节点中所有槽位都已填充，False相反
policy  回复策略，ask反问，answer回复
response 用户的回复
asking_node  上一轮正在反问这个节点
"""

class System:
    def __init__(self):
        self.load()
        self.init_memory = {"available_nodes":["scenario-买衣服_node1"]}

    #加载数据
    def load(self):
        self.load_slot_templet("slot_fitting_templet.xlsx")
        self.load_scenario()

    #读取槽位信息模板
    def load_slot_templet(self, path):
        dataframe = pandas.read_excel(path)
        self.all_slot_info = {}  #所有槽位信息
        for i in range(len(dataframe)):
            slot = dataframe["slot"][i]
            query = dataframe["query"][i]
            values = dataframe["values"][i]
            self.all_slot_info[slot] = [query, values]
        return

    #遍历文件夹， 读取下面所有scenario文件
    def load_scenario(self):
        self.all_node_info = {}
        for path in os.listdir():
            if path.startswith("scenario"):
                with open(path, encoding="utf8") as f:
                    scenario_info = json.loads(f.read())
                    scenario_name = path.split(".")[0]
                    for node in scenario_info:
                        node_name = scenario_name + "_" + node["id"]
                        self.all_node_info[node_name] = node
        return

    #意图理解
    def nlu(self, memory):
        memory = self.get_intent(memory)
        memory = self.get_slot_value(memory)
        return memory

    #获取槽位信息
    def get_slot_value(self, memory):
        query = memory["user_query"]
        hit_node = memory["hit_node"]
        slots = self.all_node_info[hit_node].get("slot", [])
        for slot in slots:
            _, values = self.all_slot_info[slot]
            result = re.search(values, query)
            if result is not None:
                memory[slot] = result.group()
        return memory

    #判断属于哪个节点
    def get_intent(self, memory):
        hit_score = 0 #命中分数
        for node in memory["available_nodes"]:
            score = self.get_node_score(node, memory)
            print(node, score, memory)
            if score > hit_score:
                hit_score = score
                hit_node = node
        memory["hit_score"] = hit_score
        memory["hit_node"] = hit_node
        return memory

    #计算单个节点的意图得分
    def get_node_score(self, node, memory):
        #上一轮正在针对这个节点进行反问
        if "asking_node" in memory and memory["asking_node"] == node:
            return 1
        query = memory["user_query"]
        intentions = self.all_node_info[node]["intent"]
        scores = [self.similar_function(query, intent) for intent in intentions]
        score = max(scores)
        return score

    #计算字符串相似度
    def similar_function(self, string1, string2):
        return len(set(string1) & set(string2)) / len(set(string2) | set(string1))

    #状态跟踪
    #当前节点的所有槽位是否都被填充了
    def state_track(self, memory):
        hit_node = memory["hit_node"]
        slots = self.all_node_info[hit_node].get("slot", [])
        memory["dialogue_state"] = True
        for slot in slots:
            if slot not in memory:
                memory["lack_slot_info"] = slot
                memory["dialogue_state"] = False
                memory["asking_node"] = hit_node
        return memory

    #对话策略选择
    #根据对话状态选择
    def policy_making(self, memory):
        #槽填满了
        if memory["dialogue_state"] == True:
            memory = self.take_action(memory)
            memory = self.open_child_node(memory)
            memory["policy"] = "ANSWER"
        #槽没填满
        else:
            memory["policy"] = "ASK"
        return memory

    #执行动作
    def take_action(self, memory):
        hit_node = memory["hit_node"]
        actions = self.all_node_info[hit_node].get("action", [])
        for action in actions:
            if action == "RUN":
                #查数据库
                pass
            else:
                pass
        return memory

    #开启所有子节点
    def open_child_node(self, memory):
        hit_node = memory["hit_node"]
        child_nodes = self.all_node_info[hit_node].get("childnode", [])
        scenario, _ = hit_node.split("_")
        memory["available_nodes"] = [scenario + "_" + node for node in child_nodes]
        return memory

    #自然语言生成
    def nlg(self, memory):
        policy = memory["policy"]
        if policy == "ASK":
            require_slot = memory["lack_slot_info"]
            response, _ = self.all_slot_info[require_slot]
        else:  #policy = “ANSWER"
            hit_node = memory["hit_node"]
            response = self.all_node_info[hit_node]["response"]
            response = self.replace_slot_info(response, memory)
        memory["response"] = response
        return memory

    #处理回复中的槽位信息
    def replace_slot_info(self, response, memory):
        hit_node = memory["hit_node"]
        slots = self.all_node_info[hit_node].get("slot", [])
        for slot in slots:
            if slot in memory:
                response = re.sub(slot, memory[slot], response)
        return response


    def query(self, user_query, memory=None):
        if memory is None:
            memory = copy.deepcopy(self.init_memory)
        memory["user_query"] = user_query
        memory = self.nlu(memory)
        memory = self.state_track(memory)
        memory = self.policy_making(memory)
        memory = self.nlg(memory)
        return memory

if __name__ == "__main__":
    system = System()
    print(system.all_slot_info)
    print(system.all_node_info)
    memory = None
    while True:
        query = input()
        memory = system.query(query, memory)
        print(memory["response"])
        print()
