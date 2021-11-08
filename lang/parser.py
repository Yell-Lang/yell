#!/usr/bin/env python3

import sys, re, time, os

from lang.lexer import Lexer, LexerError
from lang.rules import rules
from lang.preprocessor import preprocessor
from lang.expr import evaluate

_vars = {}
_aliases = {}

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
        return evaluate(parse_string('"' + tok.val[2:-1] + '"'))

def parse_string(_str):
    new_str = _str[1:-1]
    for _var in re.findall(r"{.*?}", new_str):
        new_str = new_str.replace(_var, str(_vars[_var[1:-1]]))

    return new_str

def parse_bool(_bool):
    _bool = _bool[2:-1]
    rules = [
        ('\"(\\.|[^\"])*\"',    'STRING'),
        ('\'(\\.|[^\'])*\'',    'STRING'),
        ('true',                'TRUE'),
        ('false',               'FALSE'),
        ('n\"(\\.|[^\"])*\"',   'EXPR'),
        ('n\'(\\.|[^\'])*\'',   'EXPR'),
        ('<=|>=|!=|<|>|=',      'OPER'),
    ]
    lx = Lexer(rules, skip_whitespace=True)
    lx.input(_bool)
    _compare = []
    _comparison = ''
    try:
        for tok in lx.tokens():
            if tok.type == 'TRUE':
                return True
            elif tok.type == 'FALSE':
                return False
            elif tok.type == 'STRING' or tok.type == 'EXPR':
                _compare.append(tok_to_obj(tok))
            elif tok.type == 'OPER':
                _comparison = tok.val
            else:
                print(f'Looks like {_bool} is an invalid boolean.')
                sys.exit(1)
    except LexerError as err:
        print(f'Looks like {_bool} is an invalid boolean.')
        sys.exit(1)

    if _comparison == '<=':
        if _compare[0] <= _compare[1]:
            return True
    elif _comparison == '>=':
        if _compare[0] >= _compare[1]:
            return True
    elif _comparison == '!=':
        if _compare[0] != _compare[1]:
            return True
    elif _comparison == '<':
        if _compare[0] < _compare[1]:
            return True
    elif _comparison == '>':
        if _compare[0] > _compare[1]:
            return True
    elif _comparison == '=':
        if _compare[0] == _compare[1]:
            return True

    return False

def _run(_input):
    statement_i = 1
    for statement in statements(preprocessor(_input)):
        for i, tok in enumerate(statement):
            if tok.val == 'a':
                try:
                    _run(_aliases[tok_to_obj(statement[i+1])])
                except Exception as e:
                    print(f"Hmm, there's no alias named {tok_to_obj(statement[i+1])}")
                break
            elif tok.val == 'println':
                print(str(tok_to_obj(statement[i+1])))
                break
            elif tok.val == 'print':
                print(str(tok_to_obj(statement[i+1])), end='')
                break
            elif tok.val == 'var':
                var_name = tok_to_obj(statement[i+1])
                _vars[var_name] = tok_to_obj(statement[i+3])
                break
            elif tok.val == 'sleep':
                time.sleep(tok_to_obj(statement[i+1]))
                break
            elif tok.val == 'read':
                var_name = tok_to_obj(statement[i+2])
                _vars[var_name] = input(tok_to_obj(statement[i+1]))
                break
            elif tok.val == 'if':
                if (tok_to_obj(statement[i+1])):
                    if_statements = ['code_start;\n']
                    for if_i, if_tok in enumerate(statement[i+3:]):
                        statement[i+3+if_i] = if_tok.val

                    for if_statement in ' '.join(statement[i+3:]).split('&&'):
                        if_statements.append(if_statement + ';\n')

                    _run(if_statements)
                break
            elif tok.val == 'repeat':
                repeat_statements = ['code_start;\n']
                for repeat_i, repeat_tok in enumerate(statement[i+3:]):
                    statement[i+3+repeat_i] = repeat_tok.val

                for repeat_statement in ' '.join(statement[i+3:]).split('&&'):
                    repeat_statements.append(repeat_statement + ';\n')

                for repeat_i in range(tok_to_obj(statement[i+1])):
                    _run(repeat_statements)
                break
            elif tok.val == 'while':
                while_statements = ['code_start;\n']
                for while_i, while_tok in enumerate(statement[i+3:]):
                    statement[i+3+while_i] = while_tok.val

                for while_statement in ' '.join(statement[i+3:]).split('&&'):
                    while_statements.append(while_statement + ';\n')

                while True:
                    if tok_to_obj(statement[i+1]):
                        _run(while_statements)
                        continue
                    else:
                        break
                break
            elif tok.val == 'alias':
                alias_statements = ['code_start;\n']
                for alias_i, alias_tok in enumerate(statement[i+3:]):
                    statement[i+3+alias_i] = alias_tok.val

                for alias_statement in ' '.join(statement[i+3:]).split('&&'):
                    alias_statements.append(alias_statement + ';\n')

                _aliases[tok_to_obj(statement[i+1])] = alias_statements
                break
            elif tok.val == 'system':
                os.system(tok_to_obj(statement[i+1]))
                break
