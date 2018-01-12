#!/usr/bin/python

from promise import Promise
import time

BIG_LIST = range(0,100000000)

def big_list_breakup(big_list):
    chunk = len(big_list) / 3
    chunks = []
    chunks.append(big_list[0:chunk])
    chunks.append(big_list[chunk:chunk*2])
    chunks.append(big_list[chunk*2:len(big_list)])
    return chunks

def iterme(mylist):
    cnt = 0
    for i in mylist:
        cnt = i
    return cnt

st = time.time()
p1 = Promise(
    lambda resolve, reject: resolve(iterme(BIG_LIST))
)

print p1.get()
print time.time() - st

st = time.time()
print time.time() - st
blb = big_list_breakup(BIG_LIST)
p2 = Promise.all([
        Promise.resolve(iterme(blb[0])),
        Promise.resolve(iterme(blb[1])),
        Promise.resolve(iterme(blb[2]))
    ]).then(
        lambda res: res
    )

print p2.get()
print time.time() - st


# print len(big_list_breakup(BIG_LIST))
# print len(big_list_breakup(BIG_LIST)[0])
# print len(big_list_breakup(BIG_LIST)[1])
# print len(big_list_breakup(BIG_LIST)[2])
#
# print big_list_breakup(BIG_LIST)[0][0]
# print big_list_breakup(BIG_LIST)[0][-1]
# print big_list_breakup(BIG_LIST)[1][0]
# print big_list_breakup(BIG_LIST)[1][-1]
# print big_list_breakup(BIG_LIST)[2][0]
# print big_list_breakup(BIG_LIST)[2][-1]

# manlist = big_list_breakup(BIG_LIST)[0] + \
#             big_list_breakup(BIG_LIST)[1] + \
#             big_list_breakup(BIG_LIST)[2]
#
# for i in manlist:
#     print i
