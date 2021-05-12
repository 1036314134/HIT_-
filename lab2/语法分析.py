class lexer(object):
    def __init__(self, value, kind, line):
        self.__value = value
        self.__kind = kind
        self.__line = line

    def value(self):
        return self.__value   

    def kind(self):
        return self.__kind

    def line(self):
        return self.__line

    def __eq__(self, other):
        if not isinstance(other, lexer):
            return False
        if self.__kind != other.kind():
            return False
        if self.__value != other.value():
            return False
        return True

def load_table(path):
    '''加载action和goto表'''
    table = {}
    with open(path, 'r') as f:
        for line in f:
            inf = line.split()
            state = int(inf[0])#状态序号
            if not state in table:#创建新状态
                table[state] = {}
            table[state][inf[1]] = inf[2]
    return table

def load_lexer(path):
    '''加载词法分析结果'''
    lexer_output = []
    with open(path, 'r') as f:
        for line in f:
            if len(line.strip()) == 0:
                continue
            current = line.split()
            lexer_output.append(lexer(current[0], current[1], int(current[2])))
    lexer_output.append(lexer('_', '#', -1))
    return lexer_output

def Syntax(action, goto, lexer_output):
    stack = [{'state': 0, 'id': -1}]#状态栈
    tree = []#语法树
    roots = []#根节点标号
    error = []#错误日志
    i = 0
    while i < len(lexer_output):
        current_action = action[stack[-1]['state']][lexer_output[i].kind()]
        #移入操作
        if current_action.startswith('s'):
            next_state = int(current_action[1:])#移入状态信息
            id = len(tree)
            stack.append({'state': next_state, 'id': id})#进入新状态
            roots.append(id)
            tree.append({'word': lexer_output[i], 'child': [], 'id': id})
            i += 1
        #规约操作
        elif current_action[0].isupper():
            current_action = current_action.split('-')
            k = int(current_action[1])#归约长度

            id = len(tree)
            father_node = {
                'word': lexer('_', current_action[0], tree[stack[-k]['id']]['word'].line()),
                'child': [],
                'id': id
            }
            roots.append(id)

            for j in range(k):
                father_node['child'].append(stack[-1]['id'])
                roots.remove(stack[-1]['id'])
                stack.pop()
            father_node['child'].reverse()

            next_state = int(goto[stack[-1]['state']][current_action[0]])
            stack.append({'state': next_state, 'id': id})#进入新状态
            tree.append(father_node)
        #acc
        elif current_action == 'acc':
            print('analyse finished')
            return tree, roots, error
        #error
        else:
            error.append('Syntax error at Line [%d]: illegal %s' %(lexer_output[i].line(), lexer_output[i].kind()))
            print('Syntax error at Line [%d]: illegal %s' %(lexer_output[i].line(), lexer_output[i].kind()))
            i += 1
            continue

    raise Exception('Syntax analyze error')


def DFS(tree, current, depth, f):
    line = '\t' * depth + tree[current]['word'].kind()
    if tree[current]['word'].value() != '_':
        line = line + ' : ' + tree[current]['word'].value()
    line = line + ' (' + str(tree[current]['word'].line()) + ')'
    f.write(line + '\n')

    for c in tree[current]['child']:
        DFS(tree, c, depth + 1, f)

def print_tree(path1, path2):
    with open(path1, 'w') as f:
        for r in root:
            DFS(tree, r, 0, f)
    with open(path2, 'w') as f:
        for e in error:
            f.write(e + '\n')


if __name__ == '__main__':
    action = load_table('action.txt')
    goto = load_table('goto.txt')
    lexer_output = load_lexer('input.txt')
    tree, root, error = Syntax(action, goto, lexer_output)
    print_tree('result.txt', 'error.log')
