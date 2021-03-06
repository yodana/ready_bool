def reverse_map(n):
    n = int(n * ((2**32)-1))
    k = 0
    x = 0
    y = 0
    for i in range(0, 16):
        x_mask = n & (1 << k)
        y_mask = n & (1 << (k + 1))
        x = x | (x_mask >> i)
        y = y | (y_mask >> (i + 1))
        k = k + 2
    return x, y

def map(x, y):
    #use the z curve (interleave the bits)
    z = 0
    for i in range(0, 16):
        x_mask = x & (1 << i) # mettre dans z => x bit par bit (sert a avoir le premier bit a droite puis le second etc)
        y_mask = y & (1 << i)
        z = z | (x_mask << i) #place le bit a sa place (on multiplie le bits par i pour qu il soit bien a sa place)
        z = z | (y_mask << (i + 1))
    return (z / ((2**32)-1))

def eval_set(formula, sets):
    ops = { "&": (lambda x,y: x&y),
            "!": (lambda x: not x),
            "|": (lambda x,y: x|y),
            "^": (lambda x,y: x^y),
            ">": (lambda x,y: ((not x) | y)), 
            "=": (lambda x,y: x==y)
        }
    variables = []
    i = 0
    for s in formula:
        if s >= "A" and s <= "Z":
            variables.append({"letter":s,"set":set(sets[i])})
            i += 1
    pile = []
    for s in formula:
        if s >= "A" and s <= "Z":
            pile.append(next(x["set"] for x in variables if x["letter"] == s)) #chercher dans la liste la variable correspondant au set 
        else:
            try:
                if s == "!":
                    s = set({})
                    pile.pop()
                else:
                    s = ops[s](pile[-2], pile.pop())
                    pile.pop()
                pile.append(s)
            except:
                exit("Error Formula")
    if len(pile) == 1:
        return list(pile[0])
    else:
        exit("Error Formula")

def powerset(set):
    powerset = []
    i = 0
    k = 0
    counter = 2**len(set)
    for c in range(0, counter):
        subset = []
        for j in range(0, len(set)):
            if (c & 1 << j) > 0:
                subset.append(set[j])
        powerset.append(subset)
    return powerset

def litteral_pur(variable):
    l_pure = []
    change = 0
    for s in variable:
        for i in s:
            if l_pure != []:
                for k, l in enumerate(l_pure):
                    if l["letter"] == i["letter"]:
                        if l["negation"] != i["negation"]:
                            del l_pure[k]
                        change = 1
            if change == 0:
                l_pure.append(i)
    if len(l_pure) == 0:
        change = 0
    for i, s in enumerate(variable):
        for v in s:
            if v in l_pure:
                if i >= 0:
                    del variable[i]
                i -= 1
    return variable, change

def clause_unitaire(variable):
    cu = ""
    for s in variable:
            if len(s) == 1:
                cu = s
    change = 0
    i = 0
    k = 0
    if cu != "":
        while(i < len(variable)):
            while(k < len(variable[i])):
                if variable[i][k]["letter"] == cu[0]["letter"]:
                    change = 1
                    if variable[i][k]["negation"] == cu[0]["negation"]:
                        del(variable[i])
                        if variable == []:
                            break ;
                        i = 0
                    else:
                        del(variable[i][k])
                        k = 0
                k +=1
            i +=1
            k = 0
    return variable, change

def dpll(variable):
     #fonction clause unitaire
    change = 1
    while (change == 1):
        variable, change = clause_unitaire(variable)
    #fonction litteral pur
    change = 1
    while (change == 1):
        variable, change = litteral_pur(variable)
    if variable == []:
        return True
    for s in variable:
        if s == []:
            return False
    #fonction heuristic MOMS
    new = []
    minimum = len(variable[0])
    #prendre les clauses les + petites
    for s in variable:
        if len(s) <= minimum:
            if len(s) == minimum:
                new.append(s)
            else:
                new = []
                new.append(s)
    letter = []
    #prendre la lettre la plus presentes dans les clauses
    for s in new:
        for k in s:
            letter.append(k["letter"])
    minimum = 0
    new = []
    for l in letter:
        if letter.count(l) >= minimum:
            if letter.count(l) == minimum and l not in new:
                new.append(l)
            else:
                minimum = letter.count(l)
                new = []
                new.append(l)
    l = []
    #si deux variables sont a egalite choisir la vairable la + presente dans toute la formule
    if len(new) > 1:
        for s in variable:
            for m in s:
                l.append(m["letter"])
        minimum = 0
        new = []
        for s in l:
            if l.count(s) >= minimum:
                if l.count(s) == minimum and l not in new:
                    new.append(s)
                else:
                    minimum = letter.count(s)
                    new = []
                    new.append(s)
    v1 = []
    v2 = []
    for s in variable:
        v1.append(s)
        v2.append(s)
    v1.append([{"letter":new[0], "negation":0}])
    v2.append([{"letter":new[0], "negation":1}])
    return dpll(v1) or dpll(v2)

def sat(formula):
    f = conjunctive_normal_form(formula)
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
                    clauses.append(variable[-2])
                if s == "|":
                    for v in variable[-1]:
                        variable[-2].append(v)
                    variable.pop()
    return dpll(variable)
    

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
    '''print(print_truth_table("AB|C&D|"))
    print("\n")
    print(print_truth_table("AA!&"))
    print(print_truth_table("A!B|C&"))
    print(print_truth_table("AB&!C!|") + "\n")
    print(print_truth_table("AB|C&") + "\n")
    print(print_truth_table("AA!&B|B!&"))
    print(print_truth_table("AB|D|") + "\n")
    print(print_truth_table("A!A|AA|&A!A!|AA!|&&"))
    print(print_truth_table("AA^"))
    print(print_truth_table("AD|E!|AE!|&BC!|E|&BD!|&BD|E|&A!B!|&A!B|C!|&B!D|E!|&AB!|&"))'''
    print(print_truth_table("PQ!|PQ|R!|&QR|&R&"))
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
    '''print(sat("A!B|C&")) #True
    print(sat("AB&!C!|")) #true
    print(sat("AB|C&")) #true
    print(sat("AA!&B|B!&")) #False
    print(sat("AB|D|")) #true
    print(sat("AB|"))#true
    print(sat("AB&"))#true 
    print(sat("AA!&")) #False
    print(sat("AA^")) #False
    print(sat("AD|E!|AE!|&BC!|E|&BD!|&BD|E|&A!B!|&A!B|C!|&B!D|E!&AB!|&")) #True
    print(sat("PQ!|PQ|R!|&QR|&R&")) # true
    print(sat("AB!|C|D!|F!|H!|BC|&BC|D|E|H|&BD!|E|F!|&BC!|G|H!|&BD!|F|G!|&B!C!|&B!C!|D!|&B!C|D|&B!D!|E|&B!E!|F|&G!H!|&GH|&GH|&")) #true'''
    #ex08
    #print(powerset([1,2,3]))
    #print(powerset([1,2]))
    #ex09
    '''sets = [{1,2,3}, {0,4,5}, {0,1}]
    print(eval_set("AB&C&",sets))
    print(eval_set("AB|C&",sets))
    sets = [{}, {0,4,5}]
    print(eval_set("AB|",sets))
    sets = [{1, 2}, {0,4,5}]
    print(eval_set("A!B|", sets))'''
    #ex10
    print(map((2**16)-2,(2**16)-2))
    print(map((2**16)-1,(2**16)-1))
    print(map(3,3))
    print(map(2**10,2**10))
    print(map(0, 0))
    print(map(2, 0))
    #ex11
    print(reverse_map(0.9999999993015081))
    print(reverse_map(0))
    print(reverse_map(0.0007324218751705303))
