qualign
====
## Description
qualign is a demonstration software to solve sequence alignment problems using
quadratic unconstrained binary optimization.


## Requirement
- python (pyqubo, requests packages)
- D-wave or Fujitsu Digital annealer account

## Install
```
git clone github.com:ymatsumoto/qualign
pip install pyqubo requests
```

## Usage
```
qualign/qualign -g 3 "seq1" "seq2"
```
'-g' allows N maximum gap (default: 0 or difference length of two sequences)


## Licence
[MIT Licence](https://github.com/ymatsumoto/qualign/blob/master/LICENSE)

## Contact
Yuki Matsumoto (matsumoto@gen-info.osaka-u.ac.jp)

## Citation
Not published yet.

