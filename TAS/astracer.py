import sys
import tracert_parser
from res_states import ResStates


DOC = """
usage: python astracer.py address

Options:
\taddress - ip address or domain

Example:
python astracer.py ya.ru
Tracing route to ya.ru [87.250.250.242]
over a maximum of 30 hops:
1 | 92.54.96.157 | 35154 | RU | TELENET-AS - PJSC Rostelecom
2 | 213.180.213.18 | 13238 | RU | YANDEX - YANDEX LLC
3 | 87.250.239.127 | 13238 | RU | YANDEX - YANDEX LLC
4 | 87.250.239.149 | 13238 | RU | YANDEX - YANDEX LLC
5 | 5.255.255.77 | 13238 | RU | YANDEX - YANDEX LLC
Trace complete.
"""


def main():
    if len(sys.argv) == 1 or sys.argv[1] == 'help':
        print(DOC)
    else:
        address = sys.argv[1]
        for line in tracert_parser.parse(address):
            print(line)


if __name__ == '__main__':
    main()
