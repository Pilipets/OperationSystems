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
    (fa.multiCommentDFA.match, MType.DFA),
    (fa.apwDFA.match, MType.DFA),
    (fa.wspDFA.match, MType.DFA),
    (fa.nlDFA.match, MType.DFA),

    (r"`(``|[^`])*`", tt.Name, MType.REGEX),
    (r"´(´´|[^´])*´", tt.Name, MType.REGEX),

    (fa.placeHoldFA.match, MType.MyFA),
    (r'(?<!\w)[$:?]\w+', tt.Name.Placeholder, MType.REGEX),

    (fa.commandFA.match, MType.MyFA),

    (r'(CASE|IN|USING|FROM|AS)\b', tt.Keyword, MType.REGEX),
    (fa.hardcodedValuesDFA.match, MType.DFA),
    (fa.nameFA.match, MType.MyFA),
    (fa.funcFA.match, MType.MyFA),
    (fa.hexFA.match,  MType.MyFA),
    (fa.floatFA.match, MType.MyFA),
    (r'-?(\d+(\.\d*)|\.\d+)(?![_A-Z])', tt.Number.Float, MType.REGEX),

    (r'\d+(?![_A-Z])', tt.Number.Integer, MType.REGEX),
    (r"'(''|\\\\|\\'|[^'])*'", tt.String.Single, MType.REGEX),

    (r'((LEFT\s+|RIGHT\s+)?(INNER\s+|OUTER\s+)?)?JOIN\b', tt.Keyword, MType.REGEX),
    (r'NOT\s+NULL\b', tt.Keyword, MType.REGEX),

    (r'DOUBLE\s+PRECISION\b', tt.Name.Builtin, MType.REGEX),
    (r'GROUP\s+BY\b', tt.Keyword, MType.REGEX),
    (r'ORDER\s+BY\b', tt.Keyword, MType.REGEX),
    (r'(NOT\s+)?(LIKE|ILIKE)\b', tt .Operator.Comparison, MType.REGEX),
    (fa.keywordFA.match, MType.MyFA),

    (fa.puncDFA.match, MType.DFA),
    (fa.opCompDFA.match, MType.DFA),
    (fa.operatorDFA.match, MType.DFA)
    ]

for idx in range(len(SQL_PATTERNS)):
    tup = SQL_PATTERNS[idx]
    if tup[-1] == MType.REGEX:
        SQL_PATTERNS[idx] = (re.compile(tup[0], re.IGNORECASE).match, tup[1], tup[2])