import requests
import json
import functools
import operator

def _solve(api_key, q, offset, options, mode):
    tmp = [[k1,k2] for ((k1,k2),v) in q.items()]
    keys = sorted(set([k for keys in tmp for k in keys]))
    #keys = sorted(set(functools.reduce(operator.add, ((k1,k2) for ((k1,k2),v) in q.items()))))
    k2i = {keys[i]: i for i in range(len(keys))}

    url = "https://api.jp-east-1.digitalannealer.global.fujitsu.com/v1/qubo/solve"
    headers = {'X-DA-Access-Key': api_key,
            'Accept': 'application/json',
            'Content-type': 'application/json'}
    qubo = [{"coefficient": v, "polynomials": (k2i[k1], k2i[k2])}
            for ((k1,k2),v) in q.items()]
    qubo.append({"coefficient": offset})

    m = {'DAPT': "fujitsuDAPT",
         'DA':"fujitsuDA",
         'DAMixed': "fujitsuDAMixedMode"}

    payload = {'binary_polynomial': {'terms': qubo},
            m[mode]: options}

    return requests.post(url, headers=headers, data=json.dumps(payload))

def _solve_v2(api_key, q, offset, options, mode):
    tmp = [[k1,k2] for ((k1,k2),v) in q.items()]
    keys = sorted(set([k for keys in tmp for k in keys]))
    #keys = sorted(set(functools.reduce(operator.add, ((k1,k2) for ((k1,k2),v) in q.items()))))
    k2i = {keys[i]: i for i in range(len(keys))}

    url = "https://api.jp-east-1.digitalannealer.global.fujitsu.com/v2/async/qubo/solve"
    headers = {'X-DA-Access-Key': api_key,
            'Accept': 'application/json',
            'Content-type': 'application/json'}
    qubo = [{"coefficient": v, "polynomials": (k2i[k1], k2i[k2])}
            for ((k1,k2),v) in q.items()]
    qubo.append({"coefficient": offset})

    m = {'DAPT': "fujitsuDA2PT",
         'DA':"fujitsuDA2",
         'DAMixed': "fujitsuDA2MixedMode"}

    payload = {'binary_polynomial': {'terms': qubo},
            m[mode]: options}

    return requests.post(url, headers=headers, data=json.dumps(payload))

def hobo2qubo(api_key, q, offset, options, mode):
    tmp = [[k1,k2] for ((k1,k2),v) in q.items()]
    keys = sorted(set([k for keys in tmp for k in keys]))
    #keys = sorted(set(functools.reduce(operator.add, ((k1,k2) for ((k1,k2),v) in q.items()))))
    k2i = {keys[i]: i for i in range(len(keys))}

    url = "https://api.jp-east-1.digitalannealer.global.fujitsu.com/v2/async/qubo/solve"
    headers = {'X-DA-Access-Key': api_key,
            'Accept': 'application/json',
            'Content-type': 'application/json'}
    qubo = [{"coefficient": v, "polynomials": (k2i[k1], k2i[k2])}
            for ((k1,k2),v) in q.items()]
    qubo.append({"coefficient": offset})

    m = {'DAPT': "fujitsuDA2PT",
         'DA':"fujitsuDA2",
         'DAMixed': "fujitsuDA2MixedMode"}

    payload = {'binary_polynomial': {'terms': qubo},
            m[mode]: options}

    return requests.post(url, headers=headers, data=json.dumps(payload))

def jobs(api_key):
    url = "https://api.jp-east-1.digitalannealer.global.fujitsu.com/v2/async/jobs"
    headers = {'X-DA-Access-Key': api_key,
            'Accept': 'application/json',
            'Content-type': 'application/json'}
    return requests.get(url, headers=headers)

def result(api_key, job):
    job_id = json.loads(job.text)['job_id']
    url = "https://api.jp-east-1.digitalannealer.global.fujitsu.com/v2/async/jobs/result/"+job_id
    headers = {'X-DA-Access-Key': api_key,
            'Accept': 'application/json',
            'Content-type': 'application/json'}
    return requests.get(url, headers=headers)

def to_sol(q, solution):
  keys = sorted(set(functools.reduce(operator.add, ((k1,k2) for ((k1,k2),v) in q.items()))))
  i2k = {i:keys[i] for i in range(len(keys))}
  return {i2k[int(i)]:1 if v else 0 for (i,v) in solution.items()}

def solve_DAPT(api_key, q, offset,
               number_iterations=100000,
               number_replicas=100,
               offset_increase_rate=1000,
               solution_mode="COMPLETE",
               guidance_config=None):
    options = {'number_iterations': number_iterations,
            'number_replicas': number_replicas,
            'offset_increase_rate': offset_increase_rate,
            'solution_mode': solution_mode,
            'guidance_config': guidance_config}
    options = {k: options[k] for k in options if options[k] is not None}
    return _solve(api_key, q, offset, options, mode="DAPT")

def solve_DA2PT(api_key, q, offset,
                number_iterations=100000,
                number_replicas=100,
                offset_increase_rate=1000,
                solution_mode="COMPLETE",
                guidance_config=None):
    options = {'number_iterations': number_iterations,
            'number_replicas': number_replicas,
            'offset_increase_rate': offset_increase_rate,
            'solution_mode': solution_mode,
            'guidance_config': guidance_config}
    options = {k: options[k] for k in options if options[k] is not None}
    return _solve_v2(api_key, q, offset, options, mode="DAPT")

def solve_DA(api_key,
             q,
             offset,
             expert_mode=False,
             noise_model=None,
             number_iterations=100000,
             number_runs=100,
             offset_increase_rate=None,
             temperature_decay=None,
             temperature_interval=None,
             temperature_mode=None,
             temperature_start=None,
             solution_mode="COMPLETE",
             guidance_config=None):
    options = {'expert_mode': expert_mode,
               'noise_model': noise_model,
               'number_iterations': number_iterations,
               'number_runs': number_runs,
               'offset_increase_rate': offset_increase_rate,
               'temperature_decay': temperature_decay,
               'temperature_interval': temperature_interval,
               'temperature_mode': temperature_mode,
               'temperature_start': temperature_start,
               'solution_mode': solution_mode,
               'guidance_config': guidance_config}
    options = {k: options[k] for k in options if options[k] is not None}
    return _solve(api_key, q, offset, options, mode="DA")

def solve_DA2(api_key,
              q,
              offset,
              expert_mode=False,
              noise_model=None,
              number_iterations=100000,
              number_runs=100,
              offset_increase_rate=None,
              temperature_decay=None,
              temperature_interval=None,
              temperature_mode=None,
              temperature_start=None,
              solution_mode="COMPLETE",
              guidance_config=None):
    options = {'expert_mode': expert_mode,
               'noise_model': noise_model,
               'number_iterations': number_iterations,
               'number_runs': number_runs,
               'offset_increase_rate': offset_increase_rate,
               'temperature_decay': temperature_decay,
               'temperature_interval': temperature_interval,
               'temperature_mode': temperature_mode,
               'temperature_start': temperature_start,
               'solution_mode': solution_mode,
               'guidance_config': guidance_config}
    options = {k: options[k] for k in options if options[k] is not None}
    return _solve_v2(api_key, q, offset, options, mode="DA")

def solve_DAMixed(api_key, q, offset,
             noise_model="METROPOLIS",
             number_iterations=100000,
             number_runs=100,
             offset_increase_rate=1000,
             temperature_decay=0.0001,
             temperature_interval=100,
             temperature_mode="EXPONENTIAL",
             temperature_start=1000,
             solution_mode="COMPLETE",
             guidance_config=None):
    options = {'noise_model': noise_model,
               'number_iterations': number_iterations,
               'number_runs': number_runs,
               'offset_increase_rate': offset_increase_rate,
               'temperature_decay': temperature_decay,
               'temperature_interval': temperature_interval,
               'temperature_mode': temperature_mode,
               'temperature_start': temperature_start,
               'solution_mode': solution_mode,
               'guidance_config': guidance_config}
    options = {k: options[k] for k in options if options[k] is not None}
    return _solve(api_key, q, offset, options, mode="DAMixed")

def solve_DA2Mixed(api_key, q, offset,
             noise_model="METROPOLIS",
             number_iterations=100000,
             number_runs=100,
             offset_increase_rate=1000,
             temperature_decay=0.0001,
             temperature_interval=100,
             temperature_mode="EXPONENTIAL",
             temperature_start=1000,
             solution_mode="COMPLETE",
             guidance_config=None):
    options = {'noise_model': noise_model,
               'number_iterations': number_iterations,
               'number_runs': number_runs,
               'offset_increase_rate': offset_increase_rate,
               'temperature_decay': temperature_decay,
               'temperature_interval': temperature_interval,
               'temperature_mode': temperature_mode,
               'temperature_start': temperature_start,
               'solution_mode': solution_mode,
               'guidance_config': guidance_config}
    options = {k: options[k] for k in options if options[k] is not None}
    return _solve_v2(api_key, q, offset, options, mode="DAMixed")

