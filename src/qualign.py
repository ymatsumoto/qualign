#!/usr/bin/env python
#from pyqubo import Sum, Matrix, Vector, Constraint, Placeholder, utils
import itertools
import functools
import operator
import json
import copy
from pyqubo import Array, Sum, Constraint, Placeholder, utils
from pprint import pprint
from solveda import solve_DA, solve_DA2, solve_DAPT, solve_DA2PT, solve_DAMixed, solve_DA2Mixed, to_sol, result
from blosum62 import Blosum62

def generateCI_src(index, crossed_index, i1, i2):
    src="("
    for ci in crossed_index:
        src+="("
        for n in range(N):
            if i1 == n:
                src += str(ci[0])
            elif i2 == n:
                src += str(ci[1])
            else:
                src += "range(slen["+str(n)+"])"

            if n < N - 1:
                src += ", "
        src+="),"
    return src[:-1]+")"

def generateCrossIndex_i(index, i1, i2):
    _index = copy.deepcopy(index)
    if i1 < i2:
        _i1 = i1
        _i2 = i2
    else:
        _i1 = i2
        _i2 = i1
    # _i1 = min(i1, i2)
    # _i2 = max(i1, i2)

    crossed_index = [
        target for target in itertools.product(range(slen[_i1]), range(slen[_i2]))
        if (((_index[_i1] <= target[0] and target[1] <= index[_i2]) or
                (target[0] <= _index[_i1] and _index[_i2] <= target[1])) and
            not(target[0] == _index[_i1] and target[1] == _index[_i2]))]
    return(eval(generateCI_src(index, crossed_index, _i1, _i2)))

def i2x(index):
    return(eval("x["+"][".join(map(lambda i: str(i), index))+"]"))

def i2s(index):
    return(eval("x["+"][".join(map(lambda i: str(i), index))+"]"))

def conv(index, dim):
    exp = 0
    tmp = copy.deepcopy(index)
    for i in range(slen[dim]):
        tmp[dim] = i
        exp += i2x(tmp)
    return(exp)

def score(index):
    nucl = []
    for i in range(N):
        nucl.append(s[i][index[i]])
    return(sum(list(map(lambda a: a[0]==a[1], itertools.combinations(nucl, 2)))))

def maxScore():
    return(N*(N-1)/2)

blosum62 = Blosum62()
def score_blosum62(index):
    nucl = []
    for i in range(N):
        nucl.append(s[i][index[i]])
    return(sum(list(map(lambda a: blosum62.score(a[0],a[1]), itertools.combinations(nucl, 2)))))
    #return(sum(list(map(lambda a: Blosum62.scoreblosum62[a[0]][a[1]], itertools.combinations(nucl, 2)))))


def maxScore_blosum62():
    return(N*(N-1)/2)

#s = ["ATGCATC", "ATCAC", "ATCACCCTAA"]
max_gaps = 5
s = ["ATGCATC", "ATCAC"]

diff, i = (len(s[0])-len(s[1]), 0) if len(s[0]) > len(s[1]) else (len(s[1])-len(s[0]), 1)
if diff < max_gaps:
    s[i] += '*'*(max_gaps - diff)

a,b,c,d,e = Placeholder('a'), Placeholder('b'), Placeholder('c'), Placeholder('d'), Placeholder('e')
fd = {'a':0, 'b':1, 'c':0, 'd':8, 'e':4}

N = len(s)
slen = list(map(lambda s: len(s), s))
x = Array.create('x', shape=slen, vartype='BINARY')

index_all = [list(i) for i in eval("itertools.product("+",".join(map(lambda s: "range("+str(s)+")", slen))+")")]
exp = b*sum((-score_blosum62(i))*i2x(i) for i in index_all)
for dim in range(N):
    tmp = copy.deepcopy(slen)
    tmp[dim] = 1
    index = [list(i) for i in eval("itertools.product("+",".join(map(lambda s: "range("+str(s)+")", tmp))+")")]
    exp_tmp = 0
    for i in index:
        exp_tmp += d*(conv(i, dim) - 1.0)**2
    exp += Constraint(exp_tmp, label="one_dim")
for index in index_all:
    ci = []
    for i1, i2 in itertools.combinations(range(N), 2):
        ci += generateCrossIndex_i(index, i1, i2)
        exp += Constraint(e*(i2x(index)*sum(i2x(i) for i in ci)), label="cross")

model = exp.compile()
q, offset = model.to_qubo(feed_dict=fd)

sol = utils.solve_qubo(q, sweeps=1000)

##pprint({(k,v) for k,v in sol.items() if v == 1})
pprint(sorted([k for k,v in sol.items() if v == 1]))
decoded_solution, broken, energy =\
  model.decode_solution(sol, feed_dict=fd, vartype='BINARY')
