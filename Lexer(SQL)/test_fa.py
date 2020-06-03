from lexer import Lexer
from finite_automata import *
import token_types as tt
import pytest



int_data = [('-5sdf',   None),
        ('3453 ',   (NfaMatch('3453 ', 0, 4), tt.Number.Integer)),
        ('3F',      None),
        ('323_dF',  (NfaMatch('323_dF', 0, 2), tt.Number.Integer)),
        ('32',      (NfaMatch('32', 0, 2), tt.Number.Integer)),
        ('-5234',   (NfaMatch('-5234', 0, 5), tt.Number.Integer)),
        ('!56',     None),
        ('532 6',     (NfaMatch('532 6', 0, 3), tt.Number.Integer)),
        ('-35sa6',     (NfaMatch('-35sa6', 0, 2), tt.Number.Integer))
    ]
def test_int_fa():
    matcher = intFA.match
    for dt in int_data:
        assert matcher(dt[0], 0) == dt[1]

float2_data = [('-5.012sdf ',  (NfaMatch('-5.012sdf ', 0, 5), tt.Number.Float)),
        ('.3434',       (NfaMatch('.3434', 0, 5), tt.Number.Float)),
        ('-453123.34',  (NfaMatch('-453123.34', 0, 10), tt.Number.Float)),
        ('.5_sd2',      None),
        ('-12.2sdf',    (NfaMatch('-12.2sdf', 0, 4), tt.Number.Float)),
        ('12.sdf',      None),
        ('532.54 6',    (NfaMatch('532.54 6', 0, 6), tt.Number.Float))
    ]
def test_float2_fa():
    matcher = float2FA.match
    for dt in float2_data:
        assert matcher(dt[0], 0) == dt[1]


float_data = [('-432.23E-675',  (NfaMatch('-432.23E-675', 0, 12), tt.Number.Float)),
              ('.432E6',        (NfaMatch('.432E6', 0, 6), tt.Number.Float)),
              ('-.4E1',         (NfaMatch('-.4E1', 0, 5), tt.Number.Float)),
              ('3.4E-43221',    (NfaMatch('3.4E-43221', 0, 10), tt.Number.Float)),
    ]
def test_float_fa():
    matcher = floatFA.match
    for dt in float_data:
        assert matcher(dt[0], 0) == dt[1]


err_data = [('#abc'),
            ('!'),
            ('!adsad'),
            ('#23')
    ]
def test_error_tt():
    for dt in err_data:
        tokens = Lexer.get_tokens(err_data[0])
        assert tokens[0][0] == tt.Error


if __name__ == '__main__':
    test_error_tt()
