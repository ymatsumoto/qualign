import requests
import json
from functools import reduce
from operator import add

def solveDA(api_key, q, offset, options, mode="DAPT"):
    keys = sorted(set(reduce(add, ((k1,k2) for ((k1,k2),v) in q.items()))))
    k2i = {keys[i]: i for i in range(len(keys))}

    url = "https://api.jp-east-1.digitalannealer.global.fujitsu.com/v1/qubo/solve"
    api_key = ""
    headers = {'X-DA-Access-Key': api_key,
            'Accept': 'application/json',
            'Content-type': 'application/json'}
    options = {'solution_mode' : 'COMPLETE',
            'number_iterations': 1000000,
            'number_replicas': 20,
            'offset_increase_rate': 1000}
    qubo = [{"coefficient": v, "polynomials": (k2i[k1], k2i[k2])}
            for ((k1,k2),v) in q.items()]
    qubo.append({"coefficient": offset})

    m = {'DAPT': "fujitsuDAPT",
         'DA':"fujitsuDA",
         'DAMixed': "fujitsuDAMixedMode"}

    payload = {'binary_polynomial': {'terms': qubo},
            m[mode]: options}

    return requests.post(url, headers=headers, data=json.dumps(payload))

