import re
import subprocess
import requests
import json
import time
from res_states import ResStates

IP_PATTERN = re.compile(r'(\d+ ms|\*)\s*'
                        r'(\d+ ms|\*)\s*'
                        r'(\d+ ms|\*)\s* '
                        r'(\d+\.\d+\.\d+\.\d+|Request timed out.)')


def parse(address):
    t1 = time.time()
    bad_tryings = 0
    log = []
    process = subprocess.Popen('tracert -d {}'.format(address),
                               stdout=subprocess.PIPE,
                               universal_newlines=True)
    cur_num = 1
    for stdout_line in iter(process.stdout.readline, ""):
        log.append(stdout_line)
        res_state, res = _parse_line(stdout_line)
        if res_state == ResStates.INFO:
            yield res
        elif res_state == ResStates.IP_FOUND:
            try:
                yield '{} | {}'.format(cur_num, _handle_ip(res))
                cur_num += 1
            except Exception:
                pass
        elif res_state == ResStates.ERROR:
            if bad_tryings < 3:
                bad_tryings += 1
            else:
                process.kill()
                yield '\n\n{}:\nLOG:\n{}'.format(res, ''.join(log))
                break
    t2 = time.time()
    yield 'Done in {} seconds'.format(t2 - t1)


def _handle_ip(ip):
    holder_and_AS_json = requests.get(
        'https://stat.ripe.net/data/prefix-overview/data.json?&resource={}'.format(ip), timeout=3)
    country_json = requests.get(
        'https://stat.ripe.net/data/rir/data.json?resource={}&lod=2'.format(ip), timeout=3)
    holder_and_AS = json.loads(
        holder_and_AS_json.content.decode())['data']['asns'][0]
    holder = holder_and_AS['holder']
    AS = holder_and_AS['asn']
    country = json.loads(
        country_json.content.decode())['data']['rirs'][0]['country']
    return '{} | {} | {} | {}'.format(ip, AS, country, holder)


def _parse_line(line):
    mo = IP_PATTERN.search(line)
    if mo:
        num_found = False
        for i in range(1, 4):
            if mo[i] != '*':
                num_found = True
                break
        return ((ResStates.IP_FOUND, mo[4]) if num_found
                else (ResStates.ERROR, 'TRACE ERROR'))
    else:
        if line == '\n':
            return ResStates.USELESS, line
        elif (line.startswith('Trace complete') or
                line.startswith('Tracing route to') or
                line.startswith('over a maximum of')):
            return ResStates.INFO, line[:-1]
        else:
            return ResStates.ERROR, 'Trace error'


if __name__ == '__main__':
    print(_handle_ip('212.193.64.0'))
