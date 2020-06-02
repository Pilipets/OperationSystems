import token_types as tt

class NfaMatch:
    def __init__(self, text, start, end):
        self.__group = text[start:end]
        self.__end = end
    def end(self):
        return self.__end
    def group(self):
        return self.__group

def get_keyword_tt(value):
    val = value.upper()
    if val in KEYWORDS_DML: return tt.DML
    elif val in KEYWORDS_TYPES: return tt.Name.BuiltIn
    elif val in KEYWORDS: return tt.Keyword
    else: return tt.Name

# r'[0-9_A-Z][_$#\w]*'
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

#r'[A-Z]\w*(?=\()'
class FunctionFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            if state == 0:
                if ch.isalpha(): state = 1
                else: break
                pos += 1
            elif state == 1:
                if ch.isalnum() or ch == '_': pos += 1
                else: state = 3
            elif state == 3:
                if ch != '(': state = 0
                break
        if state == 3: return NfaMatch(text, start, pos), tt.Function
        else: return None

# r'-?0x[\dA-F]+'
class HexFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '-': next_state = 1
                elif ch == '0': next_state = 2
            elif state == 1:
                if ch == '0': next_state = 2
            elif state == 2:
                if ch == 'x': next_state = 3
            elif state == 3:
                if ch.isalpha() or ch.isdigit(): next_state = 4
            elif state == 4:
                if ch.isalpha() or ch.isdigit(): next_state = 4
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 4: return NfaMatch(text, start, pos), tt.Number.Hexadecimal
        else: return None

# r'(@|##|#)[A-Z]\w+'
class NameFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '#': next_state = 1
                elif ch == '@': next_state = 2
            elif state == 1:
                if ch == '#': next_state = 2
                elif ch.isalpha(): next_state = 3
            elif state == 2:
                if ch.isalpha(): next_state = 3
            elif state == 3:
                if ch.isalnum() or ch == '_': next_state = 4
            elif state == 4:
                if ch.isalnum() or ch == '_': next_state = 4
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 4: return NfaMatch(text, start, pos), tt.Name
        else: return None

# r'-?(\d+(\.\d*)|\.\d+)(?![_A-Z])'
class FloatFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '-': next_state = 1
                elif ch.isdigit(): next_state = 2
            elif state == 1:
                if ch.isalpha() or ch == '_': pass
                elif ch == '.': next_state = 3
                elif ch == 'E': next_state = 5
            elif state == 3:
                if ch.isdigit(): next_state = 4
            elif state == 4:
                if ch.isdigit(): next_state = 4
                elif ch == 'E': next_state = 5
            elif state == 5:
                if ch == '-': next_state = 6
                elif ch.isdigit(): next_state = 7
            elif state == 6 or state == 7:
                if ch.isdigit(): next_state = 7
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 7: return NfaMatch(text, start, pos), tt.Number.Float
        else: return None

# r'-?\d*(\.\d+)?E-?\d+'
class FloatFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '-': next_state = 1
                elif ch.isdigit(): next_state = 2
                elif ch == '.': next_state = 3
                elif ch == 'E': next_state = 5
            elif state == 1 or state == 2:
                if ch.isdigit(): next_state = 2
                elif ch == '.': next_state = 3
                elif ch == 'E': next_state = 5
            elif state == 3:
                if ch.isdigit(): next_state = 4
            elif state == 4:
                if ch.isdigit(): next_state = 4
                elif ch == 'E': next_state = 5
            elif state == 5:
                if ch == '-': next_state = 6
                elif ch.isdigit(): next_state = 7
            elif state == 6 or state == 7:
                if ch.isdigit(): next_state = 7
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 7: return NfaMatch(text, start, pos), tt.Number.Float
        else: return None

# r'%(\(\w+\))?s'
class PlaceHolderFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '%': next_state = 1
            elif state == 1:
                if ch == '(': next_state = 2
                elif ch == 's': next_state = 5
            elif state == 2:
                if ch.isalnum() or ch == '_': next_state = 3
            elif state == 3:
                if ch.isalnum() or ch == '_': next_state = 3
                elif ch == ')': next_state = 4
            elif state == 4:
                if ch == 's': next_state = 5
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 5: return NfaMatch(text, start, pos), tt.Name.Placeholder
        else: return None

# r'\\\w+'
class CommandFA:
    def match(self, text, pos):
        start, state = pos, 0
        while pos < len(text):
            ch = text[pos]
            next_state = None
            if state == 0:
                if ch == '\\': next_state = 1
            elif state == 1:
                if ch.isalnum() or ch == '_': next_state = 2
            elif state == 2:
                if ch.isalnum() or ch == '_': next_state = 2
            if next_state is None: break
            else: state, pos = next_state, pos + 1
        if state == 2: return NfaMatch(text, start, pos), tt.Command
        else: return None

keywordFA = KeywordFA()
funcFA = FunctionFA()
hexFA = HexFA()
nameFA = NameFA()
floatFA = FloatFA()
placeHoldFA = PlaceHolderFA()
commandFA = CommandFA()

# Extended with any char DFA - rather NFA
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

def get_transition_dict(st, jumps, res={}):
    for ch in jumps: res[ch] = st
    return res

# r':=', r'::' r'\*'
apwDFA = DFA(
    transitions={
        'q0': {':': 'q1', '*': 'q4'},
        'q1': {'=': 'q2', ':': 'q3'}
    },
    initial_state='q0',
    final_states={'q2', 'q3', 'q4'},
    return_vals= {'q2': tt.Assignment, 'q3': tt.Punctuation, 'q4': tt.Wildcard}
)

# r'\s', r'\?'
wspDFA = DFA(
    transitions={
        'q0': {' ':  'q1', '\f': 'q1', '\v': 'q1', '\t': 'q1', '?': 'q2'}
    },
    initial_state='q0',
    final_states={'q1', 'q2'},
    return_vals= {'q1': tt.Whitespace, 'q2': tt.Name.Placeholder}
    )

# r'(\r\n|\r|\n)'
nlDFA = DFA(
    transitions={
        'q0': {'\r': 'q1', '\n': 'q2'},
        'q1': {'\n': 'q2'}
    },
    initial_state='q0',
    final_states={'q1', 'q2'},
    return_vals= {'q1': tt.Newline, 'q2': tt.Newline}
)

# r'[;:()\[\],\.]'
puncDFA = DFA(
    transitions={
        'q0': get_transition_dict('q1', ';:()[],.')
    },
    initial_state='q0',
    final_states={'q1'},
    return_vals= {'q1': tt.Punctuation}
)

# r'[<>=~!]+'
opCompDFA = DFA(
    transitions={
        'q0': get_transition_dict('q1', '<>=~!'),
        'q1': get_transition_dict('q1', '<>=~!')
    },
    initial_state='q0',
    final_states={'q1'},
    return_vals= {'q1': tt.Operator.Comparison}
)

# r'[+/@#%^&|`?^-]+'
operatorDFA = DFA(
    transitions={
        'q0': get_transition_dict('q1', '+/@#%^&|`?^-'),
        'q1': get_transition_dict('q1', '+/@#%^&|`?^-')
    },
    initial_state='q0',
    final_states={'q1'},
    return_vals= {'q1': tt.Operator}
)

# r'(--|# ).*?(\r\n|\r|\n|$)'
singleCommentDFA = DFA(
    transitions={
        'q0': {'-': 'q7', '#': 'q8'},
        'q1': {'\n': 'q4', '': 'q2'},
        'q2': {'\r': 'q5', '\n': 'q6', '\0': 'q6', '':'q2'},
        'q5': {'\n': 'q6'},
        'q7': {'-': 'q1'}, 'q8': {' ': 'q1'}
    },
    initial_state='q0',
    final_states={'q5', 'q6'},
    return_vals= {'q5': tt.Comment.Single, 'q6': tt.Comment.Single}
)

# r'/\*[\s\S]*?\*/'
multiCommentDFA = DFA(
    transitions={
        'q0': {'/': 'q1'},
        'q1': {'*': 'q2'},
        'q2': {'*': 'q3', '': 'q2'},
        'q3': {'/': 'q4', '': 'q2'}
    },
    initial_state='q0',
    final_states={'q4'},
    return_vals= {'q4': tt.Comment.Multiline}
)

# 'VALUES'
hardcodedValuesDFA = DFA(
        transitions={
        'q0': {'V': 'q1'},
        'q1': {'A': 'q2'},
        'q2': {'L': 'q3'},
        'q3': {'U': 'q4'},
        'q4': {'E': 'q5'},
        'q5': {'S': 'q6'}
    },
    initial_state='q0',
    final_states={'q6'},
    return_vals= {'q6': tt.Keyword}
)

# I'm not sure how complex FA techniques should be
# I can try implementing/using deterministic/non-deterministic 
# turing machines/push-down automata
# Please let me know if you expect that

KEYWORDS_TYPES = (
    'ARRAY', 'BIGINT', 'BINARY', 'BIT', 'BLOB', 'BOOLEAN', 'CHAR', 'CHARACTER', 'DECIMAL',
    'FLOAT', 'INT', 'INTEGER', 'TEXT', 'VARCHAR'
    )

KEYWORDS_DML = (
    'SELECT', 'INSERT', 'DELETE', 'UPDATE', 'DROP', 'CREATE', 'ALTER'
)

KEYWORDS = (
    'ABORT', 'ABS', 'ADD', 'AFTER', 'ALIAS', 'ALL', 'ARE', 'ASC', 'AT', 'AUTO_INCREMENT',
    'BEFORE', 'BEGIN', 'BOTH',
    'CASCADE', 'CHECK', 'COUNT', 'COLUMN', 'CONSTRAINT', 'CONSTRAINTS', 'CONTAINS', 'CONTINUE', 'CLASS', 'CLOSE',
    'COLLECT', 'COLUMN', 'COLUMN_NAME', 'COMMIT', 'CONNECT', 'CONTAINS', 'CONTINUE', 'COPY', 'CORRESPONDING',
    'DATA', 'DATABASE', 'DECLARE', 'DEFAULT', 'DESC', 'DELIMITER', 'DESTROY', 'DISCONNECT', 'DISABLE'
    'EXISTING', 'EXISTS', 'EXTRACT', 'FOREACH', 'FOREIGN', 'FALSE', 'FULL', 'FUNCTION',
    'GET', 'GROUPING', 'HAVING', 'IDENTIFY', 'IGNORE', 'ILIKE', 'INCLUDING', 'INCREMENT', 'INTERSECT', 'IS',
    'ISNULL', 'ITERATE', 'KEY',
    'WHERE', 'FROM', 'INNER', 'JOIN', 'AND', 'OR', 'LIKE', 'ON', 'IN',
    'SET', 'BY', 'GROUP', 'ORDER', 'AS', 'WHEN', 'DISTINCT', 'IF', 'END', 'THEN', 'LOOP',
    'AS', 'ELSE', 'FOR', 'WHILE', 'CASE', 'MIN', 'MAX'
    )
