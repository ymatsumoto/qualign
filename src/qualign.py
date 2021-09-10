#!/usr/bin/env python
#from pyqubo import Sum, Matrix, Vector, Constraint, Placeholder, utils
import itertools
import functools
import operator
import json
import copy
import neal
import sys
import numpy as np
from pyqubo import Array, Constraint, Placeholder, utils, Spin
from pprint import pprint
from solveda import solve_DA, solve_DA2, solve_DAPT, solve_DA2PT, solve_DAMixed, solve_DA2Mixed, to_sol, result
from blosum62 import Blosum62
from argparse import ArgumentParser

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
        #exp += i2x(tmp) # for BINARY
        exp += (i2x(tmp) + 1) / 2
    return(exp)

def score(index):
    nucl = []
    for i in range(N):
        nucl.append(s[i][index[i]])
    return(sum(list(map(lambda a: a[0]==a[1], itertools.combinations(nucl, 2)))))

def maxScore():
    return(N*(N-1)/2)

m = Blosum62()
def score_blosum62(index, matrix):
    nucl = []
    for i in range(N):
        nucl.append(s[i][index[i]])
    return(sum(list(map(lambda a: matrix.score(a[0],a[1]), itertools.combinations(nucl, 2)))))
    #return(sum(list(map(lambda a: Blosum62.scoreblosum62[a[0]][a[1]], itertools.combinations(nucl, 2)))))

def maxScore_blosum62():
    return(N*(N-1)/2)

def parser():
    argparser = ArgumentParser()
    argparser.add_argument('-s1', help='AA Sequence 1', required=True)
    argparser.add_argument('-s2', help='AA Sequence 2', required=True)
    argparser.add_argument('-c0', help='Penalty for AA mismatch (default=4)', type=int, default=1)
    argparser.add_argument('-c1', help='Penalty for redundant alignment (default=8)', type=int, default=8)
    argparser.add_argument('-c2', help='Penalty for twisted alignment (default=8)', type=int, default=4)
    #argparser.add_argument('-g', '--gap', help='Number of outer maximum gaps (default=0)', default=0)
    argparser.add_argument('-q', '--quiet', help='Print only results', action='store_true', default=False)
    args = argparser.parse_args()
    return args

if __name__ == '__main__':
    args = parser()
    #s = ["ATGCATC", "ATCAC"]
    s = [args.s1, args.s2]

    #max_gaps = args.gap
    #diff, i = (len(s[0])-len(s[1]), 0) if len(s[0]) > len(s[1]) else (len(s[1])-len(s[0]), 1)
    #if diff < max_gaps:
    #    s[i] += '*'*(max_gaps - diff)

    c0,c1,c2 = Placeholder('C0'), Placeholder('C1'), Placeholder('C2')
    fd = {'C0':args.c0, 'C1':args.c1, 'C2':args.c2}

    N = len(s)
    slen = list(map(lambda s: len(s), s))
    print(slen)
    x = Array.create('x', shape=slen, vartype='SPIN')

    index_all = [list(i) for i in eval("itertools.product("+",".join(map(lambda s: "range("+str(s)+")", slen))+")")]
    exp = c0*sum((-score_blosum62(i, m))*(i2x(i)+1)/2 for i in index_all)
    print(exp)
    #exp = c0*sum((-score_blosum62(i, m))*i2x(i) for i in index_all) for BINARY
    for dim in range(N):
        tmp = copy.deepcopy(slen)
        tmp[dim] = 1
        index = [list(i) for i in eval("itertools.product("+",".join(map(lambda s: "range("+str(s)+")", tmp))+")")]
        exp_tmp = 0
        for i in index:
            exp_tmp += c1*(conv(i, dim) - 1.0)**2
        exp += Constraint(exp_tmp, label="one_dim")
    for index in index_all:
        ci = []
        for i1, i2 in itertools.combinations(range(N), 2):
            ci += generateCrossIndex_i(index, i1, i2)
            #exp += Constraint(c2*(i2x(index)*sum(i2x(i) for i in ci)), label="cross") # for BINARY
            exp += Constraint(c2*((i2x(index)+1)/2*sum((i2x(i)+1)/2 for i in ci)), label="cross")

    model = exp.compile()
    bqm = model.to_bqm(feed_dict=fd)
    sa = neal.SimulatedAnnealingSampler()
    sampleset = sa.sample(bqm, num_reads=10)
    samples = model.decode_sampleset(sampleset, fd)
    sol = min(samples, key=lambda s: s.energy)
    xx = list(dict(sorted(sol.sample.items())).values())
    xx = np.array(xx).reshape(*map(len, s))

    print(xx)
    success = True
    sum1 = np.sum(xx, axis=0)
    sum2 = np.sum(xx, axis=1)
    i = j = 0
    while i < slen[0] and j < slen[1]:
        if xx[i][j] == 1:
            i = i + 1
            j = j + 1
            continue
        if xx[i][j] == 0:
            if sum1[j] >= 2 or sum2[i] >= 2:
                success = False
                break
            if sum1[j] == 0 and sum2[i] != 0:
                j = j + 1
                continue
            if sum1[j] != 0 and sum2[i] == 0:
                i = i + 1
                continue
            else:
                success = False
                break

    if not success and not args.quiet:
            print("Alignment failed.", file=sys.stderr)

    if success:
        res = bytearray()
        for i in range(slen[0]):
            if sum2[i] == 0:
                s[1] = s[1][:i] + '-' + s[1][i:]
                #s[1].insert(i, '-')
        for j in range(slen[1]):
            if sum1[j] == 0:
                s[0] = s[0][:j] + '-' + s[0][j:]
                #s[0].insert(j, '-')
        score = 0
        for i in range(slen[0]):
            score -= m.blosum62[s[0][i]][s[1][i]]
        if not args.quiet:
            print("Alignment successed. Score:",+score, file=sys.stderr)
        print(s[0])
        print(s[1])

