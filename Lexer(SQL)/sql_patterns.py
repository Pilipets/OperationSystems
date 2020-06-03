import re
import token_types as tt
import finite_automata as fa
import enum

class MType(enum.Enum):
   MyFA = 1
   REGEX = 2
   DFA = 3

SQL_PATTERNS = [
    (fa.singleCommentFA.match, MType.MyFA),
    (fa.multiCommentDFA.match, MType.DFA),
    (fa.apwDFA.match, MType.DFA),
    (fa.wsDFA.match, MType.DFA),
    (fa.nlDFA.match, MType.DFA),

    (r"`(``|[^`])*`", tt.Name, MType.REGEX),
    (r"´(´´|[^´])*´", tt.Name, MType.REGEX),

    (r'(?<!\w)[$:?]\w+', tt.Name.Placeholder, MType.REGEX),
    (r'\?', tt.Name.Placeholder, MType.REGEX),

    (r'(CASE|IN|USING|FROM|AS)\b', tt.Keyword, MType.REGEX),
    (fa.hardcodedValuesDFA.match, MType.DFA),
    (fa.nameFA.match, MType.MyFA),

    # How should name.dot_name be partitioned into tokens?!
    # (r'(?<=\.)[A-Z]\w*', tt.Name, MType.REGEX),

    (fa.funcFA.match, MType.MyFA),

    (fa.hexFA.match,  MType.MyFA),

    (fa.floatFA.match, MType.MyFA),
    (fa.float2FA.match, MType.MyFA),
    (fa.intFA.match, MType.MyFA),

    (r"'(''|\\\\|\\'|[^'])*'", tt.String.Single, MType.REGEX),
    
    # http://www.mysql.ru/docs/man/JOIN.html
    (r'((LEFT\s+|RIGHT\s+|FULL\s+)?(INNER\s+|OUTER\s+|STRAIGHT\s+)|(CROSS\s+|NATURAL\s+)?)?JOIN\b', tt.Keyword, MType.REGEX),
    (r'NOT\s+NULL\b', tt.Keyword, MType.REGEX),

    # https://www.w3schools.com/sql/sql_ref_union.asp
    (r'UNION\s+ALL\b', tt.Keyword, MType.REGEX),
    (r'CREATE(\s+OR\s+REPLACE)?\b', tt.Keyword.DDL, MType.REGEX),
    (r'DOUBLE\s+PRECISION\b', tt.Name.Builtin, MType.REGEX),
    (r'GROUP\s+BY\b', tt.Keyword, MType.REGEX),
    (r'ORDER\s+BY\b', tt.Keyword, MType.REGEX),
    (r'(NOT\s+)?LIKE\b', tt .Operator.Comparison, MType.REGEX),
    (fa.keywordFA.match, MType.MyFA),

    (fa.puncDFA.match, MType.DFA),
    (fa.opCompDFA.match, MType.DFA),
    (fa.operatorDFA.match, MType.DFA)
    ]

for idx in range(len(SQL_PATTERNS)):
    tup = SQL_PATTERNS[idx]
    if tup[-1] == MType.REGEX:
        SQL_PATTERNS[idx] = (re.compile(tup[0], re.IGNORECASE).match, tup[1], tup[2])