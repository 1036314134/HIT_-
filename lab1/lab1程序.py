import re

# token比较大的分类
TOKEN_STYLE = [
    'KEY_WORD',  #关键字
    'IDENTIFIER',  #标识符
    'DIGIT_CONSTANT',  #数字
    'OPERATOR',  #运算符
    'SEPARATOR',  #分隔符
    'STRING_CONSTANT'  #字符串
]

# 将关键字、运算符、分隔符进行具体化
DETAIL_TOKEN_STYLE = {
    'struct': 'STRUCT',
    'include': 'INCLUDE',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'double': 'DOUBLE',
    'for': 'FOR',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'return': 'RETURN',
    '=': 'ASSIGN',
    '&': 'ADDRESS',
    '<': 'LT',
    '>': 'GT',
    '++': 'SELF_PLUS',
    '--': 'SELF_MINUS',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'MUL',
    '/': 'DIV',
    '>=': 'GET',
    '<=': 'LET',
    '(': 'LL',
    ')': 'RL',
    '{': 'LP',
    '}': 'RP',
    '[': 'LM',
    ']': 'RM',
    ',': 'COMMA',
    '"': 'DOUBLE_QUOTE',
    ';': 'SEMICOLON',
    '#': 'SHARP',
}

# 关键字
keywords = [
    ['struct', 'int', 'float', 'double', 'char', 'void'],
    ['if', 'for', 'while', 'do', 'else'],
    ['include', 'return'],
]

# 运算符
operators = ['=', '&', '<', '>', '++', '--', '+', '-', '*', '/', '>=', '<=', '!=', '&&', '||']

# 分隔符
delimiters = ['(', ')', '{', '}', '[', ']', ',', '\"', ';']

# c文件名字
file_name = None

# 文件内容
content = None


class Token(object):
    '''记录分析出来的单词'''
    def __init__(self, type_index, value):
        self.type = DETAIL_TOKEN_STYLE[value] if (
            type_index == 0 or type_index == 3 or type_index == 4
        ) else TOKEN_STYLE[type_index]
        self.value = value


class Lexer(object):
    '''词法分析器'''

    def __init__(self):
        # 用来保存词法分析出来的结果
        self.tokens = []

    # 判断是否是空白字符
    def is_blank(self, index):
        return (
            content[index] == ' ' or
            content[index] == '\t' or
            content[index] == '\n' or
            content[index] == '\r'
        )

    # 跳过空白字符
    def skip_blank(self, index):
        while index < len(content) and self.is_blank(index):
            index += 1
        return index

    # 判断是否是关键字
    def is_keyword(self, value):
        for item in keywords:
            if value in item:
                return True
        return False

    # 词法分析主程序
    def main(self):
        i = 0
        while i < len(content):
            i = self.skip_blank(i)
            # 如果是引入头文件，还有一种可能是16进制数，这里先不判断
            if content[i] == '#':
                self.tokens.append(Token(4, content[i]))
                i = self.skip_blank(i + 1)
                # 分析这一引入头文件
                while i < len(content):
                    # 匹配"include"
                    if re.match('include', content[i:]):
                        self.tokens.append(Token(0, 'include'))
                        i = self.skip_blank(i + 7)
                    # 匹配"或者<
                    elif content[i] == '\"' or content[i] == '<':
                        self.tokens.append(Token(4, content[i]))
                        i = self.skip_blank(i + 1)
                        close_flag = '\"' if content[i] == '\"' else '>'
                        # 找到include的头文件
                        lib = ''
                        while content[i] != close_flag:
                            lib += content[i]
                            i += 1
                        self.tokens.append(Token(1, lib))
                        # 跳出循环后，很显然找到close_flog
                        self.tokens.append(Token(4, close_flag))
                        i = self.skip_blank(i + 1)
                        break
                    else:
                        print('include error!')
                        exit()
            # 如果是字母或者是以下划线开头
            elif content[i].isalpha() or content[i] == '_':
                # 找到该字符串
                temp = ''
                while i < len(content) and (
                        content[i].isalpha() or
                        content[i] == '_' or
                        content[i].isdigit()):
                    temp += content[i]
                    i += 1
                # 判断该字符串
                if self.is_keyword(temp):
                    self.tokens.append(Token(0, temp))
                else:
                    self.tokens.append(Token(1, temp))
                i = self.skip_blank(i)
            # 如果是数字开头
            elif content[i].isdigit():
                temp = ''
                while i < len(content):
                    if content[i] == '0' and (content[i + 1] == 'X' or content[i + 1] == 'x'):
                        temp += '0'
                        temp += content[i + 1]
                        i += 2
                    elif content[i].isdigit() or (
                            content[i] == '.' and content[i + 1].isdigit()):
                        temp += content[i]
                        i += 1
                    elif content[i] == '0' and (content[i + 1] == 'X' or content[i + 1] == 'x'):
                        temp += '0'
                        temp += content[i + 1]
                        i += 2
                    elif not content[i].isdigit():
                        if content[i] == '.':
                            print('float number error!')
                            i += 1
                            break
                        else:
                            break
                self.tokens.append(Token(2, temp))
                i = self.skip_blank(i)
            # 如果是分隔符
            elif content[i] in delimiters:
                self.tokens.append(Token(4, content[i]))
                # 如果是字符串常量
                if content[i] == '\"':
                    i += 1
                    temp = ''
                    while i < len(content):
                        if content[i] != '\"':
                            temp += content[i]
                            i += 1
                        else:
                            break
                    else:
                        print('error:lack of \"')
                        break
                    self.tokens.append(Token(5, temp))
                    self.tokens.append(Token(4, '\"'))
                i = self.skip_blank(i + 1)
            # 如果是运算符
            elif content[i] in operators:
                # 如果是++、--
                if (content[i] == '+' or content[i] == '-') and (
                        content[i + 1] == content[i]):
                    self.tokens.append(Token(3, content[i] * 2))
                    i = self.skip_blank(i + 2)
                # 如果是>=或者<=
                elif (content[i] == '>' or content[i] == '<') and content[i + 1] == '=':
                    self.tokens.append(Token(3, content[i] + '='))
                    i = self.skip_blank(i + 2)
                # 其他
                else:
                    self.tokens.append(Token(3, content[i]))
                    i = self.skip_blank(i + 1)


if __name__ == '__main__':
    file_name = "test.c"
    source_file = open(file_name, 'r')
    content = source_file.read()
    lexer = Lexer()
    lexer.main()
    for token in lexer.tokens:
        print('<%s, %s>' % (token.type, token.value))
