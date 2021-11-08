#!/usr/bin/env python3

import sys, re, time, os

from lang.lexer import Lexer, LexerError
from lang.rules import rules
from lang.preprocessor import preprocessor
from lang.expr import evaluate

_vars = {}

# Generate list of statements in code
def statements(_input):
    codestart_line = _input.index("code_start;\n")
    _input =  ''.join(_input[codestart_line+1:])

    statements = []
    lx = Lexer(rules, skip_whitespace=True)
    lx.input(_input)

    try:
        statement = []
        comment = False
        for tok in lx.tokens():
            if tok.type == 'COMMENT_START':
                comment = True
                continue
            elif tok.type == 'COMMENT_END':
                comment = False
                continue
            elif tok.type == 'COMMENT_END':
                comment = False
                continue
            elif comment == True:
                continue
            if tok.type != 'LINE_END':
                statement.append(tok)
            else:
                statements.append(statement)
                statement = []
    except LexerError as err:
        print('LexerError at position %s' % err.pos)

    return statements

def tok_to_obj(tok):
    if tok.type == 'STRING':
        return parse_string(tok.val)
    if tok.type == 'BOOL':
        return parse_bool(tok.val)
    elif tok.type == 'EXPR':
        return evaluate(tok.val[2:-1])
    elif tok.type == 'TOINT':
        return evaluate(parse_string(tok.val.replace('toint', '', 1).split(' ', 1)[1]))

def parse_string(_str):
    new_str = _str[1:-1]
    for _var in re.findall(r"{.*?}", new_str):
        new_str = new_str.replace(_var, _vars[_var[1:-1]])

    return new_str

def parse_bool(_bool):
    _bool = _bool[2:-1]
    rules = [
        ('\"(\\.|[^\"])*\"',    'STRING'),
        ('n\"(\\.|[^\"])*\"',   'EXPR'),
        ('<=|>=|!=|<|>|=',      'OPER'),
    ]
    lx = Lexer(rules, skip_whitespace=True)
    lx.input(_bool)
    _compare = []
    _comparison = ''
    for tok in lx.tokens():
        if tok.type == 'STRING' or tok.type == 'EXPR':
                _compare.append(tok_to_obj(tok))
        elif tok.type == 'OPER':
            _comparison = tok.val
        else:
            print(f'Looks like {_bool[1:-1]} is an invalid boolean.')
            sys.exit(1)

    if _comparison == '<=':
        if _compare[0] <= _compare[1]:
            return 'True'
    elif _comparison == '>=':
        if _compare[0] >= _compare[1]:
            return 'True'
    elif _comparison == '!=':
        if _compare[0] != _compare[1]:
            return 'True'
    elif _comparison == '<':
        if _compare[0] < _compare[1]:
            return 'True'
    elif _comparison == '>':
        if _compare[0] > _compare[1]:
            return 'True'
    elif _comparison == '=':
        if _compare[0] == _compare[1]:
            return 'True'
        return 'False'

def _run(_input):
    statement_i = 1
    for statement in statements(preprocessor(_input)):
        for i, tok in enumerate(statement):
            if tok.val == 'println':
                print(str(tok_to_obj(statement[i+1])))
                continue
            elif tok.val == 'print':
                print(str(tok_to_obj(statement[i+1])), end='')
                continue
            elif tok.val == 'var':
                var_name = tok_to_obj(statement[i+1])
                _vars[var_name] = tok_to_obj(statement[i+3])
                continue
            elif tok.val == 'sleep':
                time.sleep(tok_to_obj(statement[i+1]))
                continue
            elif tok.val == 'read':
                var_name = tok_to_obj(statement[i+2])
                _vars[var_name] = input(tok_to_obj(statement[i+1]))
                continue
            elif tok.val == 'system':
                os.system(tok_to_obj(statement[i+1]))
                continue
