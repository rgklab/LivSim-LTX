import matplotlib.pyplot as plt
objects = []


x_lst = [0.05, 0.01, 0.005, 0.0025, 0.001]
x_lst.reverse()
y_lst1 = [4.14, 5.58, 6.1, 6.1, 6.1]
y_lst1.reverse()
y_lst2 = [1.95, 0.51, -0.1, -0.0004, -0.0001]
y_lst2.reverse()

plt.xlabel('std of noise')
plt.ylabel('Direct/Indirect Effect')
plt.plot(x_lst, y_lst1, label="Natural Direct Effect")
plt.plot(x_lst, y_lst2, label="Natural Indirect Effect")

plt.legend(loc='right')

plt.show()
