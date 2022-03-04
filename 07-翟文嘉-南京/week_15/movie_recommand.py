import openpyxl
import numpy as np
import time
from collections import defaultdict

'''
电影打分数据集
实现协同过滤
'''

#为了好理解，将数据格式转化成user-item的打分矩阵形式
def build_u2i_matrix(user_item_score_data_path, item_name_data_path, write_file=False):
    #获取item id到电影名的对应关系
    item_id_to_item_name = {}
    with open(item_name_data_path, encoding="ISO-8859-1") as f:
        for line in f:
            item_id, item_name = line.split("|")[:2]
            item_id = int(item_id)
            item_id_to_item_name[item_id] = item_name
    total_movie_count = len(item_id_to_item_name)
    #读打分文件
    user_to_rating = {}
    with open(user_item_score_data_path, encoding="ISO-8859-1") as f:
        for line in f:
            user_id, item_id, score, time_stamp = line.split("\t")
            user_id, item_id, score = int(user_id), int(item_id), int(score)
            if user_id not in user_to_rating:
                user_to_rating[user_id] = [0] * total_movie_count
            user_to_rating[user_id][item_id - 1] = score
    
    if not write_file:
        return user_to_rating, item_id_to_item_name
    
    # 写入excel便于查看
    workbook = openpyxl.Workbook()
    sheet = workbook.create_sheet(index=0)
    #第一行：user_id, movie1, movie2...
    header = ["user_id"] + [item_id_to_item_name[i + 1] for i in range(total_movie_count)]
    sheet.append(header)
    for i in range(len(user_to_rating)):
        #每行：user_id, rate1, rate2...
        line = [i + 1] + user_to_rating[i + 1]
        sheet.append(line)
    workbook.save("user_movie_rating.xlsx")
    return user_to_rating, item_id_to_item_name

#向量余弦距离
def cosine_distance(vector1, vector2):
    ab = vector1.dot(vector2)
    a_norm = np.sqrt(np.sum(np.square(vector1)))
    b_norm = np.sqrt(np.sum(np.square(vector2)))
    return ab/(a_norm * b_norm)


#依照user对item的打分判断user之间的相似度
def find_similar_user(user_to_rating):
    user_to_similar_user = {}
    score_buffer = {}
    for user_a, ratings_a in user_to_rating.items():
        similar_user = []
        for user_b, ratings_b in user_to_rating.items():
            if user_b == user_a or user_b>100 or user_a > 100:
                continue
            #ab用户互换不用重新计算cos
            if "%d_%d"%(user_b, user_a) in score_buffer:
                similarity = score_buffer["%d_%d"%(user_b, user_a)]
            else:
                similarity = cosine_distance(np.array(ratings_a), np.array(ratings_b))
                score_buffer["%d_%d" % (user_a, user_b)] = similarity

            similar_user.append([user_b, similarity])
        similar_user = sorted(similar_user, reverse=True, key=lambda x:x[1])
        user_to_similar_user[user_a] = similar_user
    return user_to_similar_user

#基于user的协同过滤
#输入user_id, item_id, 给出预测打分
#有预测打分之后就可以对该用户所有未看过的电影打分，然后给出排序结果
#所以实现打分函数即可
#topn为考虑多少相似的用户
def user_cf(user_id, item_id, user_to_similar_user, user_to_rating, topn=30):
    pred_score = 0
    #取前topn相似用户对该电影的打分
    count = 0
    for similar_user, similarity in user_to_similar_user[user_id][:topn]:
        rating_by_similiar_user = user_to_rating[similar_user][item_id]
        pred_score += rating_by_similiar_user * similarity
        if rating_by_similiar_user != 0:
            count += 1
    pred_score /= count + 1e-5
    return pred_score

##############################################
def get_user_favorites(user_id, user_to_rating):
    ratings = np.array(user_to_rating[user_id])
    top_ratings = np.argsort(ratings)[::-1]

    return top_ratings

def get_item_similarity(favo_item, item_id):
    favo_item_rating = np.array([rating[favo_item] for rating in user_to_rating.values()])
    item_rating = np.array([rating[item_id] for rating in user_to_rating.values()])

    return cosine_distance(favo_item_rating, item_rating)

def get_item_rating_by_user(user_id, item_id):
    return user_to_rating[user_id][item_id]

#基于item的协同过滤
#类似user_cf
#自己尝试实现
def item_cf(user_id, item_id, topn):
    favorite_items = get_user_favorites(user_id, user_to_rating)  # TODO  获取这个用户喜欢的前n个电影
    favorite_item = {}

    for favo_item in favorite_items:
        score = 0
        sim = get_item_similarity(favo_item, item_id)  # TODO  对于两个电影，计算相似度
        score += sim * get_item_rating_by_user(user_id, item_id)  # TODO  获取已知喜欢的电影得分
        favorite_item[favo_item] = score
    favorite_item = sorted(favorite_item.items(), key=lambda x: x[1], reverse=True)[:topn]

    return favorite_item
##############################################

#对于一个用户做完整的item召回
def movie_recommand(user_id, similar_user, user_to_rating, item_to_name, topn=10):
    unseen_items = [item_id for item_id, rating in enumerate(user_to_rating[user_id]) if rating == 0]
    res = []
    for item_id in unseen_items:
        score = user_cf(user_id, item_id, similar_user, user_to_rating)
        res.append([item_to_name[item_id + 1], score])
    res = sorted(res, key=lambda x:x[1], reverse=True)
    return res[:topn]



if __name__ == "__main__":
    user_item_score_data_path = "ml-100k/u.data"
    item_name_data_path = "ml-100k/u.item"
    user_to_rating, item_to_name = build_u2i_matrix(user_item_score_data_path, item_name_data_path, False)

    #user-cf
    # s = time.time()
    # similar_user = find_similar_user(user_to_rating)
    # print("相似用户计算完成，耗时：", time.time() - s)
    # while True:
    #     user_id = int(input("输入用户id："))
    #     item_id = int(input("输入电影id："))
    #     res = user_cf(user_id, item_id, similar_user, user_to_rating)
    #     print(res)

    #为用户推荐电影
    # while True:
    #     user_id = int(input("输入用户id："))
    #     recommands = movie_recommand(user_id, similar_user, user_to_rating, item_to_name)
    #     for recommand, score in recommands:
    #         print("%.4f\t%s"%(score, recommand))

    # item_cf
    while True:

        user_id = int(input("输入用户id："))
        if user_id == 0:
            break

        item_id = int(input("输入电影id："))
        if item_id == 0:
            break

        if user_to_rating[user_id][item_id] == 0:
            print('该用户没有看过这部电影，无法推荐')
            print('\n')
            continue

        res = item_cf(user_id, item_id, 10)
        for key, _ in res:
            print(item_to_name[key])
        print('\n')