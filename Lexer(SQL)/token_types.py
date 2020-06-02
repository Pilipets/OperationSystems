class _TokenBase(tuple):
    def __getattr__(self, name):
        return _TokenBase(self + (name,))
    def __repr__(self):
        return 'Token' + ('.' if self else '') + '.'.join(self)

Token = _TokenBase()

Text = Token.Text
Whitespace = Text.Whitespace
Newline = Whitespace.Newline
Error = Token.Error

Function = Token.Function
Keyword = Token.Keyword
Name = Token.Name
Literal = Token.Literal
String = Literal.String
Number = Literal.Number
Punctuation = Token.Punctuation
Operator = Token.Operator
Comparison = Operator.Comparison
Wildcard = Token.Wildcard
Comment = Token.Comment
Assignment = Token.Assignment

Generic = Token.Generic
Command = Generic.Command

DML = Keyword.DML
DDL = Keyword.DDL