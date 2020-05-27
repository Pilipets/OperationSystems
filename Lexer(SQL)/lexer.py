from sql_patterns import *
from finite_automata import *

class Lexer:
    @staticmethod
    def get_tokens(sql_text):

        res = []
        iterable = enumerate(sql_text)
        for pos, ch in iterable:
            match = False
            for tup in SQL_PATTERNS:
                match_obj = tup[0](sql_text, pos)
                if not match_obj: continue

                if tup[-1] == MType.REGEX: token_type = tup[1]
                else: match_obj, token_type = match_obj
                res.append((token_type, match_obj.group()))

                iterator_advance(iterable, match_obj.end() - pos - 1)
                match = True
                break
            if match == False: res.append((tt.Error, ch))
        return res

import itertools
from collections import deque

def iterator_advance(iterator, n):
    deque(itertools.islice(iterator, n), maxlen=0)
