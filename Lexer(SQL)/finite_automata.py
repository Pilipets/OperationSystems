import token_types as tt

class NfaMatch:
    def __init__(self, text, start, end):
        self.__group = text[start:end]
        self.__end = end
    def __eq__(self, other):
        if isinstance(other, self.__class__): return self.__dict__ == other.__dict__
        else: return False
    def end(self):
        return self.__end
    def group(self):
        return self.__group

def get_keyword_tt(value):
    val = value.upper()
    if val in KEYWORDS: return tt.Keyword
    elif val in KEYWORDS_TYPES: return tt.Name.BuiltIn
    elif val in KEYWORDS_DML: return tt.DML
    elif val in KEYWORDS_DDL: return tt.DDL
    else: return tt.Name

# r'[0-9_A-Za-z][_$#\w]*'
class KeywordFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '_' or ch.isalpha() or ch.isdigit(): next_state = 1
            elif state == 1:
                if ch in '_$#' or ch.isalnum(): next_state = 1
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 1:
            ins = NfaMatch(text, start, pos)
            return ins, get_keyword_tt(ins.group()) 
        else: return None

#r'[A-Za-z]\w*(?=\()'
class FunctionFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch.isalpha(): next_state = 1
            elif state == 1:
                if ch.isalnum() or ch == '_': next_state = 1
            if next_state is None: break
            else: state, pos = next_state, pos + 1

        if state == 1 and pos < len(text) and text[pos] == '(':
            return NfaMatch(text, start, pos), tt.Function
        else: return None

# r'0x[\da-fA-F]+'
class HexFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '0': next_state = 1
            elif state == 1:
                if ch == 'x': next_state = 2
            elif state == 2 or state == 3:
                if (ch >= 'a' and ch <= 'f') or (ch >= 'A' and ch <= 'F') or ch.isdigit(): next_state = 3
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 3: return NfaMatch(text, start, pos), tt.Number.Hexadecimal
        else: return None

# r'@[a-zA-Z]\w+'
class NameFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '@': next_state = 1
            elif state == 1:
                if ch.isalpha(): next_state = 2
            elif state == 2:
                if ch.isalnum() or ch == '_': next_state = 3
            elif state == 3:
                if ch.isalnum() or ch == '_': next_state = 3
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 3: return NfaMatch(text, start, pos), tt.Name
        else: return None

# r'\d*(\.\d+)?E-?\d+'
class FloatFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch.isdigit(): next_state = 0
                elif ch == '.': next_state = 1
                elif ch == 'E': next_state = 3
            elif state == 1:
                if ch.isdigit(): next_state = 2
            elif state == 2:
                if ch.isdigit(): next_state = 2
                elif ch == 'E': next_state = 3
            elif state == 3:
                if ch == '-': next_state = 4
                elif ch.isdigit(): next_state = 5
            elif state == 4 or state == 5:
                if ch.isdigit(): next_state = 5
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 5: return NfaMatch(text, start, pos), tt.Number.Float
        else: return None

# r'(\d+(\.\d*)|\.\d+)(?![_a-zA-Z])'
class Float2FA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch.isdigit(): next_state = 1
                elif ch == '.': next_state = 3
            elif state == 1:
                if ch.isdigit(): next_state = 1
                elif ch == '.': next_state = 2
            elif state == 2:
                if ch.isdigit(): next_state = 2
            elif state == 3 or state == 4:
                if ch.isdigit(): next_state = 4
            if next_state is None: break
            else: state, pos = next_state, pos + 1

        if state != 2 and state != 4: return None
        to_shrink = pos < len(text) and (text[pos].isalpha() or text[pos] == '_')
        if state == 4 and to_shrink:
            if pos-start > 1 and text[pos-2].isdigit(): return NfaMatch(text, start, pos-1), tt.Number.Float
            else: return None
        elif state == 2 and to_shrink:
            if pos-start > 0 and text[pos-1] != '.': return NfaMatch(text, start, pos-1), tt.Number.Float
            else: return None
        else: return NfaMatch(text, start, pos), tt.Number.Float

# 3fddfdf
# r'\d+(?![_A-Za-z])'
class IntFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0 or state == 1:
                if ch.isdigit(): next_state = 1
            if next_state is None: break
            else: state, pos = next_state, pos + 1

        if state != 1: return None
        elif pos < len(text) and (text[pos].isalpha() or text[pos] == '_'):
            if pos-start > 1 and text[pos-2].isdigit(): return NfaMatch(text, start, pos-1), tt.Number.Integer
            else: return None
        else: return NfaMatch(text, start, pos), tt.Number.Integer

# r'--.*?(\r\n|\r|\n|$)'
class SingleCommentFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '-': next_state = 1
            elif state == 1:
                if ch == '-': next_state = 3
            elif state == 3:
                if ch == '\n': next_state = 5
                elif ch == '\r': next_state = 4
                else: next_state = 3
            elif state == 4:
                if ch == '\n': next_state = 5
            if next_state is None: break
            else: state, pos = next_state, pos + 1

        if state == 4 or state == 5 or (state == 3 and pos == len(text)):
            return NfaMatch(text, start, pos), tt.Comment.Single
        else: return None

keywordFA = KeywordFA()
funcFA = FunctionFA()
hexFA = HexFA()
nameFA = NameFA()
floatFA = FloatFA()
float2FA = Float2FA()
intFA = IntFA()
singleCommentFA = SingleCommentFA()

# Extended with any char DFA
class DFA():
    def __init__(self, *, transitions,
                 initial_state, final_states, return_vals):
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.return_vals = return_vals

    def match(self, input_str, pos):
        start = pos
        current_state = self.initial_state
        while pos < len(input_str):
            input_symbol = input_str[pos]
            jumps = self.transitions.get(current_state, {})
            if input_symbol in jumps: current_state = jumps[input_symbol]
            elif '' in jumps: current_state = jumps['']
            else: break
            pos += 1
        if current_state not in self.final_states: return None
        return NfaMatch(input_str, start, pos), self.return_vals[current_state]

def get_transition_dict(st, jumps):
    res = {}
    for ch in jumps: res[ch] = st
    return res

# r':=', r'::' r'\*'
apwDFA = DFA(
    transitions={
        0: {':': 1, '*': 4},
        1: {'=': 2, ':': 3}
    },
    initial_state= 0,
    final_states={2, 3, 4},
    return_vals= {2: tt.Assignment, 3: tt.Punctuation, 4: tt.Wildcard}
)

# r'\s'
wsDFA = DFA(
    transitions={
        0: {' ':  1, '\f': 1, '\v': 1, '\t': 1}
    },
    initial_state=0,
    final_states={1},
    return_vals= {1: tt.Whitespace}
    )

# r'(\r\n|\r|\n)'
nlDFA = DFA(
    transitions={
        0: {'\r': 1, '\n': 2},
        1: {'\n': 2}
    },
    initial_state=0,
    final_states={1, 2},
    return_vals= {1: tt.Newline, 2: tt.Newline}
)

# r'[;:()\[\],\.]'
puncDFA = DFA(
    transitions={
        0: get_transition_dict(1, ';:()[],.')
    },
    initial_state=0,
    final_states={1},
    return_vals= {1: tt.Punctuation}
)

# SQL Comparison Operators
# =, <, <=, <>, >=, >, 
opCompDFA = DFA(
    transitions={
        0: {'=': 3, '<': 1, '>': 2},
        1: {'=': 3, '>': 3},
        2: {'=': 3}
    },
    initial_state=0,
    final_states={1, 2, 3},
    return_vals= {1: tt.Operator.Comparison, 2: tt.Operator.Comparison, 3: tt.Operator.Comparison}
)

# SQL Bitwise, Arithmetic, Compound Operators
operatorDFA = DFA(
    transitions={
        0: get_transition_dict(1, '+-*/&|^%'),
        1: {'=': 2}
    },
    initial_state=0,
    final_states={1, 2},
    return_vals= {1: tt.Operator, 2: tt.Operator}
)

# r'/\*[\s\S]*?\*/'
multiCommentDFA = DFA(
    transitions={
        0: {'/': 1},
        1: {'*': 2},
        2: {'*': 3, '': 2},
        3: {'/': 4, '': 2}
    },
    initial_state=0,
    final_states={4},
    return_vals= {4: tt.Comment.Multiline}
)

# 'VALUES'
hardcodedValuesDFA = DFA(
        transitions={
        0: {'V': 1},
        1: {'A': 2},
        2: {'L': 3},
        3: {'U': 4},
        4: {'E': 5},
        5: {'S': 6}
    },
    initial_state=0,
    final_states={6},
    return_vals= {6: tt.Keyword}
)

# https://www.w3schools.com/sql/sql_datatypes.asp
KEYWORDS_TYPES = (
    # String
    'CHAR', 'VARCHAR', 'BINARY', 'VARBINARY', 'TINYBLOB', 'TINYTEXT', 'TEXT', 'BLOB', 'MEDIUMTEXT', 'MEDIUMBLOB',
    'LONGTEXT', 'LONGBLOB', 'ENUM', 'SET',
    # Numeric
    'BIT', 'TINYINT', 'BOOL', 'BOOLEAN', 'SMALLINT', 'MEDIUMINT', 'INT', 'INTEGER', 'BIGINT', 'FLOAT', 'DOUBLE',
    'DECIMAL', 'DEC',
    # Date and Time
    'DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'YEAR'
    )

# https://www.w3schools.com/sql/sql_ref_keywords.asp
KEYWORDS = (
    'ADD', 'ALL', 'AND', 'ANY', 'AS', 'ASC', 'BACKUP', 'BETWEEN', 'BY', 'CASE', 'CHECK', 'COLUMN', 
    'CONSTRAINT', 'DATABASE', 'DEFAULT', 'DESC', 'DISTINCT', 'DROP', 'ELSE', 'END', 'EXEC', 'EXISTS', 
    'FOR', 'FOREIGN', 'FROM', 'FULL', 'GROUP', 'HAVING', 'IF', 'IN', 'INDEX', 'INNER', 'INTO', 'IS', 
    'JOIN', 'KEY', 'LEFT', 'LIKE', 'LIMIT', 'LOOP', 'MAX', 'MIN', 'NOT', 'NULL', 'ON', 'OR', 'ORDER', 
    'OUTER', 'PRIMARY', 'PROCEDURE', 'RIGHT', 'ROWNUM', 'SET', 'STRAIGHT_JOIN', 'TABLE', 'THEN', 'TOP', 
    'TRUNCATE', 'UNION', 'UNIQUE', 'VALUES', 'VIEW', 'WHEN', 'WHERE', 'WHILE'
)

KEYWORDS_DML = (
    'SELECT', 'INSERT', 'DELETE', 'UPDATE', 'REPLACE', 'MERGE'
    )
KEYWORDS_DDL = (
    'DROP', 'CREATE', 'ALTER'
    )