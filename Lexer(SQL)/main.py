from lexer import Lexer


def test1():
    with open('input.txt', 'r') as f:
        text = f.read()
    res = Lexer.get_tokens(text)
    for x in res:
        print(x)

def test2():
    text = 'select perId from Permission where document.docId=?1 and user.id=2'
    res = Lexer.get_tokens(text)
    for x in res:
        print(x)

def test3():
    with open('input.txt', 'r') as f:
        for line in f:
            res = Lexer.get_tokens(line)
            for x in res:
                print(x)

if __name__ == '__main__':
    test1()

