import matplotlib.pyplot as plt

f = open("log/TD3.csv")

x = []
y = [[], [], []]
t = []
for l in f.readlines():
    a = l.split(",")
    x.append(int(a[0]))
    t.append(int(a[1]))
    y[0].append(int(a[2]) / int(a[1]))
    y[1].append(int(a[3]) / int(a[1]))
    y[2].append(1 if int(a[2]) > int(a[3]) else 0)


def smooth(a):
    r = 0
    windows = 500
    res = []
    now = 0
    nn = []
    for i in a:
        res.append(r / max(1, len(nn)))
        nn.append(i)
        r += i
        now += 1
        if now > windows:
            now -= 1
            r -= nn[0]
            nn = nn[1:]
    return res


y[0] = smooth(y[0])
y[1] = smooth(y[1])
y[2] = smooth(y[2])
t = smooth(t)


fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(x, y[0], "b", lw=1)
ax1.plot(x, y[1], "g", lw=1)
ax2.plot(x, t, "r--", lw=1)
ax1.set_ylabel("score", color="b")
ax2.set_ylabel("turn", color="r")
# ax3 = ax2.twinx()
# ax3.plot(x, y[2], 'r', lw=1)


plt.show()
