import re
import token_types as tt
import finite_automata as fa
import enum

class MType(enum.Enum):
   MyFA = 1
   REGEX = 2
   DFA = 3

SQL_PATTERNS = [
    (fa.singleCommentDFA.match, MType.DFA),
    (fa.apwDFA.match, MType.DFA),
    (fa.wsDFA.match, MType.DFA),
    (fa.nlDFA.match, MType.DFA),

    (r"`(``|[^`])*`", tt.Name, MType.REGEX),
    (r"´(´´|[^´])*´", tt.Name, MType.REGEX),

    (r'(CASE|IN|USING|FROM|AS)\b', tt.Keyword, MType.REGEX),
    ('VALUES', tt.Keyword, MType.REGEX),
    (fa.nameFA.match, MType.MyFA),
    (fa.funcFA.match, MType.MyFA),
    (fa.hexFA.match,  MType.MyFA),
    (fa.floatFA.match, MType.MyFA),
    (r'(?![_A-Z])-?(\d+(\.\d*)|\.\d+)(?![_A-Z])', tt.Number.Float, MType.REGEX),

    (r'(?![_A-Z])-?\d+(?![_A-Z])', tt.Number.Integer, MType.REGEX),
    (r"'(''|\\\\|\\'|[^'])*'", tt.String.Single, MType.REGEX),

    (r'((LEFT\s+|RIGHT\s+)?(INNER\s+|OUTER\s+)?)?JOIN\b', tt.Keyword, MType.REGEX),
    (r'NOT\s+NULL\b', tt.Keyword, MType.REGEX),
    (r'GROUP\s+BY\b', tt.Keyword, MType.REGEX),
    (r'ORDER\s+BY\b', tt.Keyword, MType.REGEX),
    (fa.keywordFA.match, MType.MyFA),

    (fa.puncDFA.match, MType.DFA),
    (fa.opCompDFA.match, MType.DFA),
    (fa.operatorDFA.match, MType.DFA)
    ]

for idx in range(len(SQL_PATTERNS)):
    tup = SQL_PATTERNS[idx]
    if tup[-1] == MType.REGEX:
        SQL_PATTERNS[idx] = (re.compile(tup[0], re.IGNORECASE).match, tup[1], tup[2])