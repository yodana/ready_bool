def clause_unitaire(variable):
    r = 0
    cu = ""
    for s in variable:
            if len(s) == 1:
                cu = s
    #clause unitaire
    change = 0
    if cu != "":
        for i, s in enumerate(variable):
            for k, l in enumerate(s):
                if l["letter"] == cu[0]["letter"]:
                    change = 1
                    if l["negation"] == cu[0]["negation"]:
                        del(variable[i])
                    else:
                        del(variable[i][k])
                        if len(variable[i]) == 0:
                            del variable[i]
    print("variable",variable)
    return variable, change

def sat(formula):
    f = conjunctive_normal_form(formula)
    print("conjunctive normal form =>", f)
    clauses = []
    variable = []
    #fonction pour faire l'ensemble de clauses
    for i, s in enumerate(f):
            if s >= "A" and s <= "Z":
                variable.append([{"letter": s, "negation": 0}])
            if s == "!":
                variable[-1][0]["negation"] += 1
            if s == "&" or s == "|":
                if s == "&":
                    print(variable[-2])
                    clauses.append(variable[-2])
                if s == "|":
                    for v in variable[-1]:
                        variable[-2].append(v)
                    variable.pop()
            print(variable)
    #fonction clause unitaire
    change = 1
    '''while (change == 1):
        variable, change = clause_unitaire(variable)'''
    #fonction litteral pur
    l_pure = []
    print("variable =>", variable)
    change = 1
    for s in variable:
        for i in s:
            if l_pure != []:
                for k, l in enumerate(l_pure):
                    if l["letter"] == i["letter"]:
                        if l["negation"] != i["negation"]:
                            del l_pure[k]
                        change = 0
            if change == 1:
                l_pure.append(i)
            change = 1
    #fonction heuristic MOMS
    
    print("l_pure =>", l_pure)

def distributivity(bloc, variable):
    bloc = bloc[:-1]
    pile = []
    for i, s in enumerate(bloc):
        if s >= "A" and s <= "Z":
            pile.append(s)
        if s == "!":
            pile[-1] += "!"
        if s == "&" or s == "|":
            pile[-2] = pile[-2] + pile[-1]+ s
            pile.pop()
    return pile[-2] + variable + "|" + pile[-1] + variable + "|&"

def conjunctive_normal_form(formula):
    f = negation_normal_form(formula)
    print(f)
    pile = []
    change = 1
    while change == 1:
        change = 0
        for i, s in enumerate(f):
            if s >= "A" and s <= "Z":
                pile.append({"letter":s, "variable":0})
            if s == "!":
                pile[-1]["letter"] += "!"
            if s == "&" or s == "|":
                if s == "&":
                    pile[-2]["variable"] +=1
                if s == "|" and (pile[-2]["variable"] > 0 or pile[-1]["variable"] > 0): #contient un and dans un or
                    if pile[-2]["variable"] > 0:
                        pile[-2]["letter"] = distributivity(pile[-2]["letter"], pile[-1]["letter"])
                        change = 1
                    else:
                        pile[-2]["letter"] = distributivity(pile[-1]["letter"], pile[-2]["letter"])
                        change = 1
                else:
                    pile[-2]["letter"] = pile[-2]["letter"] + pile[-1]["letter"] + s
                pile.pop()
        f = pile[0]["letter"]
        pile = []
    return f

def negation_normal_form(formula):
    pile = []
    change = 1
    for s in formula:
        if s >= "A" and s <= "Z":
            pile.append(s)
        if s == "!":
            pile[-1] += "!"
        if s == "&" or s == "|":
            pile[-2] = pile[-2] + pile[-1] + s
            pile.pop()
        if s == "^":
            pile[-2] = pile[-2] + pile[-1] + "!&" + pile[-2] + "!" + pile[-1] + "&|"
            pile.pop()
        if s == ">":
            pile[-2] = pile[-2] + "!" + pile[-1] + "|"
            pile.pop()
        if s == "=":
            pile[-2] = pile[-2] + "!" + pile[-1] + "|" + pile[-2] + pile[-1] + "!|&"
            pile.pop()
    formula = pile[0]
    pile = []
    while change == 1:
        change = 0
        for i, s in enumerate(formula):
            if s >= "A" and s <= "Z":
                pile.append(s)
            if s == "&" or s == "|":
                if i + 1 < len(formula) and formula[i+1] != "!":
                    pile[-2] = pile[-2] + pile[-1] + s
                    pile.pop()
                elif i+1 >= len(formula):
                    pile[-2] = pile[-2] + pile[-1] + s
                    pile.pop()
            if s == "!":
                if formula[i-1] == "!":
                    pile[-1] = pile[-1][:-1]
                elif formula[i-1] == "&":
                    pile[-2] = pile[-2] + "!" + pile[-1] + "!|"
                    pile.pop()
                    change = 1
                elif formula[i-1] == "|":
                    pile[-2] = pile[-2] + "!" + pile[-1] + "!&"
                    pile.pop()
                    change = 1
                else:
                    pile[-1] += "!"
        formula = pile[0]
        pile = []
    return formula

def pow(l):
    r = 1
    for i in range(0,l):
        r = r * 2
    return r

def create_list(forma, letter):
    l = {}
    for i, b in enumerate(forma):
        l[letter[i]] = b
    return l

def print_truth_table(formula):
    letter = []
    l = {}
    form = ""
    final = "|"
    letters = []
    for s in formula:
        if s >= "A" and s <= "Z":
            if s not in letter:
                letter.append(s)
                final += " " + s + " |"
    final += " = |\n|"
    for i in range(0, pow(len(letter))):
        t = format(i, 'b').zfill(len(letter))
        l = create_list(t, letter)
        for s in formula:
            if s >= "A" and s <= "Z":
                form += l[s]
                if s not in letters:
                    final += " " + l[s] + " |"
                    letters.append(s)
            else:
                form += s
        if eval_formula(form) == True:
            final += " 1 |"  
        else: 
            final += " 0 |"
        letters = []
        final += "\n|"
        form = ""
    final = final[:-2]
    return final


def eval_formula(formula):
    ops = { "&": (lambda x,y: x&y),
            "!": (lambda x: not x),
            "|": (lambda x,y: x|y),
            "^": (lambda x,y: x^y),
            ">": (lambda x,y: ((not x) | y)), 
            "=": (lambda x,y: x==y)
        }
    pile = []
    for s in formula:
        if s == "1" or s == "0":
            pile.append(ord(s) - ord('0'))
        else:
            try:
                if s == "!":
                    s = ops[s](pile.pop())
                else:
                    s = ops[s](pile[-2], pile.pop())
                    pile.pop()
                pile.append(s)
            except:
                exit("Error Formula")
    if len(pile) == 1:
        return True if pile[0] == 1 else False
    else:
        exit("Error Formula")

def gray_code(n):
    return ((n ^ (n << 1)) >> 1)

def adder(a, b):
    if a < 0 or b < 0:
        return "Only natural numbers"
    sum = a
    while b != 0:
        carry = sum & b
        sum = sum ^ b
        b = carry << 1
    return sum

def multiplier(a, b):
    if a < 0 or b < 0:
        return "Only natural numbers"
    stop = 1
    number = a
    while stop < b:
        a = adder(a, number)
        stop += 1
    return a

if __name__ == '__main__':
    '''a = 30
    b = 14
    #ex00
    ret = adder(a, b)
    print(ret)
    a = 3
    b = 30
    #ex01
    ret = multiplier(a, b)
    print(ret)
    #ex02
    for i in range(0, 10):
        ret = gray_code(i)
        print(ret)'''
    #ex03
    '''print(eval_formula("11>"))
    #print(eval_formula("!"))
    print(eval_formula("1011||="))
    print(eval_formula("10="))
    #ex04
    #print(print_truth_table("AB="))
    #print(print_truth_table("A!B|AB!|&"))
    #print(print_truth_table("ABCD&!&!&!"))
    #print(print_truth_table("ABC&&D|!E>")+"\n")
    #print(print_truth_table("ABC&&!D!&!E|"))
    #print(print_truth_table("ABC&&!D!&!E|"))
    #print(print_truth_table("ABC&&D|E|"))
    print(print_truth_table("AB="))
    print(print_truth_table("A!B|AB!|&"))
    print()
    print(print_truth_table("AB!&A!B&|"))
    print(print_truth_table("AB^"))'''
    '''print(print_truth_table("AB|C&D|"))
    print("\n")
    print(print_truth_table("AB|D|CD|&"))'''
    print(print_truth_table("AB|C&D|"))
    print("\n")
    print(print_truth_table("AA!&"))
    #ex05
    '''print(negation_normal_form("ABC&&!D!&!E|"))
    print(negation_normal_form("AB|C&!"))
    print(negation_normal_form("AB="))
    print(negation_normal_form("AB^"))
    #ex06
    '''
    ''''print(conjunctive_normal_form("AB&C|"))
    print(conjunctive_normal_form("ABCD&|&"))
    print(conjunctive_normal_form("AB&!"))
    print(conjunctive_normal_form("AB|!"))
    print(conjunctive_normal_form("AB|C&"))
    print(conjunctive_normal_form("AB|C&D|")) 
    print(conjunctive_normal_form("AB|C|D|"))
    print(conjunctive_normal_form("AB&!C!|"))
    print(conjunctive_normal_form("AB|!C!&"))'''
    #ex07
    #print(sat("A!B|C&"))
    #print(sat("AB&!C!|"))
    #print(sat("AB|C&"))
    print(sat("AA&B!C!|&"))
    #print(sat("AB|D|"))