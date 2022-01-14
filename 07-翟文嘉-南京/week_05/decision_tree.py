# 导入模块
import numpy as np
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn import datasets
# 鸢尾花数据
iris = datasets.load_iris()
X = iris.data[:, :2] # 为便于绘图仅选择2个特征
y = iris.target
# 测试样本（绘制分类区域）
xlist1 = np.linspace(X[:, 0].min(), X[:, 0].max(), 200)
xlist2 = np.linspace(X[:, 1].min(), X[:, 1].max(), 200)
XGrid1, XGrid2 = np.meshgrid(xlist1, xlist2)
# 决策树：criterion 决策根据，splitter 决策方式，max_depth 深度
dt = DecisionTreeClassifier(criterion='entropy', splitter='random', max_depth=10).fit(X, y)
# 预测并绘制结果
Z = dt.predict(np.vstack([XGrid1.ravel(), XGrid2.ravel()]).T)
Z = Z.reshape(XGrid1.shape)
plt.contourf(XGrid1, XGrid2, Z, cmap=plt.cm.hsv)
plt.contour(XGrid1, XGrid2, Z, colors=('k',))
plt.scatter(X[:, 0], X[:, 1], c=y, edgecolors='k', linewidth=1.5, cmap=plt.cm.hsv)
plt.savefig('决策树自定义参数.jpg')