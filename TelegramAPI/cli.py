import sys

from threading import Thread
from UserDescriberBot import UserDescriberBot


def main(token):
    my_bot = UserDescriberBot(token)
    my_bot.run()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("ERROR! UserDescriberBot can't work without token-parameter")
