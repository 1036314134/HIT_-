import re

# token比较大的分类
TOKEN_STYLE = [
    'KEY_WORD',  #关键字
    'id',  #标识符
    'const',  #数字
    'OPERATOR',  #运算符
    'SEPARATOR',  #分隔符
    'str'  #字符串
]

# 将关键字、运算符、分隔符进行具体化
DETAIL_TOKEN_STYLE = {
    'struct',
    'include',
    'int',
    'float',
    'char',
    'double',
    'for',
    'if',
    'else',
    'while',
    'do',
    'return',
    '=',
    '&',
    '<',
    '>',
    '++',
    '--',
    '+',
    '-',
    '*',
    '/',
    '>=',
    '<=',
    '(',
    ')',
    '{',
    '}',
    '[',
    ']',
    ',',
    '"',
    ';',
    '#',
    '==',
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
    def __init__(self, type_index, value, line):
        self.type = value if (
            type_index == 0 or type_index == 3 or type_index == 4
        ) else TOKEN_STYLE[type_index]
        self.value = '_' if (
            type_index == 0 or type_index == 3 or type_index == 4
        ) else value
        self.line = line


class Lexer(object):
    '''词法分析器'''

    def __init__(self):
        # 用来保存词法分析出来的结果
        self.tokens = []

    # 判断是否是空白字符
    def is_blank(self, index, line):
        return (
            line[index] == ' ' or
            line[index] == '\t' or
            line[index] == '\n' or
            line[index] == '\r'
        )

    # 跳过空白字符
    def skip_blank(self, index, line):
        while index < len(line) and self.is_blank(index, line):
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
        k = 0
        for line in content:
            k += 1
            i = 0
            while i < len(line):
                i = self.skip_blank(i, line)
                if line[i] == '#':
                    self.tokens.append(Token(4, line[i], k))
                    i = self.skip_blank(i + 1, line)
                    # 分析这一引入头文件
                    while i < len(line):
                        # 匹配"include"
                        if re.match('include', line[i:]):
                            self.tokens.append(Token(0, 'include', k))
                            i = self.skip_blank(i + 7, line)
                        # 匹配"或者<
                        elif line[i] == '\"' or line[i] == '<':
                            self.tokens.append(Token(4, line[i], k))
                            i = self.skip_blank(i + 1, line)
                            close_flag = '\"' if line[i] == '\"' else '>'
                            # 找到include的头文件
                            lib = ''
                            while line[i] != close_flag:
                                lib += line[i]
                                i += 1
                            self.tokens.append(Token(0, lib, k))
                            # 跳出循环后，很显然找到close_flog
                            self.tokens.append(Token(4, close_flag, k))
                            i = self.skip_blank(i + 1, line)
                            break
                        else:
                            print('include error!')
                            exit()
                    break
                # 如果是字母或者是以下划线开头
                if line[i].isalpha() or line[i] == '_':
                    # 找到该字符串
                    temp = ''
                    while i < len(line) and (
                            line[i].isalpha() or
                            line[i] == '_' or
                            line[i].isdigit()):
                        temp += line[i]
                        i += 1
                    # 判断该字符串
                    if self.is_keyword(temp):
                        self.tokens.append(Token(0, temp, k))
                    else:
                        self.tokens.append(Token(1, temp, k))
                    i = self.skip_blank(i, line)
                # 如果是数字开头
                elif line[i].isdigit():
                    temp = ''
                    while i < len(line):
                        if line[i] == '0' and i+1 < len(line) and (line[i + 1] == 'X' or line[i + 1] == 'x'):
                            temp += '0'
                            temp += line[i + 1]
                            i += 2
                        elif line[i].isdigit() or (
                                line[i] == '.' and line[i + 1].isdigit()):
                            temp += line[i]
                            i += 1
                        elif line[i] == '0' and i+1 < len(line) and (line[i + 1] == 'X' or line[i + 1] == 'x'):
                            temp += '0'
                            temp += line[i + 1]
                            i += 2
                        elif not line[i].isdigit():
                            if line[i] == '.':
                                print('float number error!')
                                i += 1
                                break
                            else:
                                break
                    self.tokens.append(Token(2, temp, k))
                    i = self.skip_blank(i, line)
                # 如果是分隔符
                elif line[i] in delimiters:
                    self.tokens.append(Token(4, line[i], k))
                    # 如果是字符串常量
                    if line[i] == '\"':
                        i += 1
                        temp = ''
                        while i < len(line):
                            if line[i] != '\"':
                                temp += line[i]
                                i += 1
                            else:
                                break
                        else:
                            print('error:lack of \"')
                            break
                        self.tokens.append(Token(5, temp, k))
                        self.tokens.append(Token(4, '\"', k))
                    i = self.skip_blank(i + 1, line)
                # 如果是运算符
                elif line[i] in operators:
                    # 如果是++、--
                    if (line[i] == '+' or line[i] == '-') and (
                            line[i + 1] == line[i]):
                        self.tokens.append(Token(3, line[i] * 2, k))
                        i = self.skip_blank(i + 2, line)
                    # 如果是>=或者<=
                    elif (line[i] == '>' or line[i] == '<') and line[i + 1] == '=':
                        self.tokens.append(Token(3, line[i] + '=', k))
                        i = self.skip_blank(i + 2, line)
                    elif line[i] == '=' and line[i + 1] == '=':
                        self.tokens.append(Token(3, line[i] + '=', k))
                        i = self.skip_blank(i + 2, line)
                    # 其他
                    else:
                        self.tokens.append(Token(3, line[i], k))
                        i = self.skip_blank(i + 1, line)



if __name__ == '__main__':
    file_name = "test.txt"
    source_file = open(file_name, 'r')
    content = source_file.read()
    content = content.split('\n')
    lexer = Lexer()
    lexer.main()
    with open('input.txt', 'w') as f:
        for token in lexer.tokens:
            f.write('%s %s %d\n' % (token.value, token.type, token.line))
    print("success")