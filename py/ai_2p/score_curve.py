import matplotlib.pyplot as plt
f = open("TD3.log")
cnt = 0
x = []
y = [[], []]
for l in f.readlines():
    a = l.split(";")
    if len(a) < 2:
        continue
    x.append(int(a[0].split(' ')[-2]))
    if len(x) > 1 and x[-1] < x[-2]:
        x = x[-1:]
        y[0] = []
        y[1] = []

    y[0].append(int(a[2].strip().split(' ')[-1]))
    # y[1].append(int(a[-2].strip().split(' ')[-1]))
    # y[0].append(int(a[-2].strip().split(' ')[-2]))
    # y[1].append(int(a[-2].strip().split(' ')[-1]))
# plt.plot(x, y, lw=1)


def smooth(a):
    r = 0
    windows = 100
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
print(x)
plt.plot(x[115:], y[0][115:], lw=1)
# plt.plot(x[115:], y[1][115:], lw=1)

plt.show()
