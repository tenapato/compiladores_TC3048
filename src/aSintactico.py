import ply.yacc as yacc
from aLexico import LexManager


class Symbol:

    def __init__(self, name, type, declaration_pos, value=None, init_pos=None):
        self.name = name
        self.type = type.upper()
        self.declaration_pos = declaration_pos
        self.value = value
        self.init_pos = init_pos

    def initialized(self):
        return self.init_pos is not None


class ParseManager:

    tokens = LexManager.tokens
    start = 'prog'
    precedence = (
        ('right', '='),
        ('left', 'AND', 'OR'),
        ('left', 'EQUALS', 'DIFFERENT'),
        ('nonassoc', '<', '>', 'GREAT_EQUAL', 'LESS_EQUAL'),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left', '^'),
        ('right', 'UMINUS'),
    )

    def symbol_exists(self, name):
        return name in self.symbol_table

    def __init__(self):
        self.errors = []
        self.lexManager = LexManager()
        self.lexer = self.lexManager.build()
        self.symbol_table = {}

    def p_prog(self, p):
        ''' prog : prog expression
                 | expression'''
        if len(p) == 3 and p[2][0] is not None:
            p[0] = p[1] + (p[2],)
        else:
            p[0] = (p[1],)

    def p_expression(self, p):
        ''' expression : closed_statement
                       | selection_statement
                       | iteration_statement
                       | struct_statement
                       | array_statement
                       | array_assignment
                       | function_statement
                       | function_call '''
        p[0] = p[1]

    def p_function_statement(self, p):
        ''' function_statement : FUNCTION ID '(' function_params ')' blocked_content  '''
        
        # if the function is not defined in the symbol table print error else add it
        
        if self.symbol_exists(p[2]):
            print('Error: La funcion {} ya esta definida {}'.format(p[2], p.lineno(2)))
        else:
            p[0] = (p[1], p[2], p[3])
            # add to symbol table
            self.symbol_table[p[2]] = Symbol(p[2], 'FUNCTION', p.lineno(2), p[4])
            
    def p_function_params(self, p):
        ''' function_params : function_params ',' param
                            | param '''
        if len(p) == 2:
            p[0] = (p[1],)
        else:
            p[0] = p[1] + (p[3],)
    
    def p_param(self, p):
        ''' param : declaration '''
        p[0] = p[1]

    def p_function_call(self, p):
        ''' function_call : ID '(' function_call_params ')' ';' '''
        p[0] = (p[1], p[2], p[3])
        if not self.symbol_exists(p[1]):
            print('Error: La funcion {} no esta definida, en la linea {}'.format(p[1], p.lineno(1)))

    
    def p_function_call_params(self, p):
        ''' function_call_params :  function_call_params  ',' param_call
                                | param_call '''      
        if len(p) == 2:
            p[0] = (p[1],)
        else:
            p[0] = p[1] + (p[3],)        

    # def param call with ints
    def p_param_call(self, p):
        ''' param_call : val '''
        p[0] = (p[1],)
        
    
    def p_struct_statement(self, p):
        ''' struct_statement : STRUCT ID blocked_content '''
        p[0] = (p[1], p[2], p[3])
        if self.symbol_exists(p[2]):
            print('Error: La estructura {} ya esta definida {}'.format(p[2], p.lineno(2)))
        

    def p_array_statement(self, p):
        ''' array_statement : ARRAY ID braced_content '''
        p[0] = (p[1], p[2], p[3])
    
    def p_braced_content(self, p):
        ''' braced_content :  array_dimentions  ';' '''
        p[0] = p[1]

    def p_array_dimentions(self, p):
        ''' array_dimentions : array_dimentions '[' INT_VALUE ']' 
                              | '[' INT_VALUE ']' '''
        if len(p) == 2:
            p[0] = (p[1],)
        else:
            p[0] = p[1] + str((p[3],))
    
    def p_array_assignment(self, p):
        ''' array_assignment : ARRAY ID array_dimentions  '=' op_expression ';'  '''
        p[0] = (p[1], p[2], p[3], p[5])

    def p_selection_statement(self, p):
        ''' selection_statement : IF special_statement
                                | IF special_statement ELSE blocked_content
                                | IF special_statement elif ELSE blocked_content '''
        if len(p) == 3:
            p[0] = (p[1], p[2], None, None)
        elif len(p) == 5:
            p[0] = (p[1], p[2], None, (p[3], p[4]))
        else:
            p[0] = (p[1], p[2], p[3], (p[4], p[5]))

    def p_iteration_statement(self, p):
        ''' iteration_statement : WHILE special_statement
                                | DO blocked_content WHILE blocked_op ';'
                                | FOR '(' for_first for_second ')' blocked_content
                                | FOR '(' for_first for_second op_expression ')' blocked_content '''
        if p[1] == "while":
            p[0] = (p[1], p[2])
        elif p[1] == "do":
            p[0] = (p[1], p[2], p[4])
        elif p[1] == "for" and p[5] == ')':
            p[0] = (p[1], p[3], p[4], None, p[6])
        elif p[1] == "for":
            p[0] = (p[1], p[3], p[4], p[5], p[7])

    def p_elif(self, p):
        ''' elif : ELIF special_statement
                 | elif ELIF special_statement '''
        if p[1] == 'elif':
            p[0] = ((p[1], p[2][0], p[2][1]),)
        else:
            p[0] = p[1] + ((p[2], p[3][0], p[3][1]),)

    def p_blocked_content(self, p):
        ''' blocked_content : '{' prog '}' 
                            | '{' prog return '}' '''
        p[0] = p[2]

    def p_return(self, p):
        ''' return : RETURN ';'
                    | RETURN ID ';' '''
        p[0] = (p[1],)

    def p_var_list(self, p):
        ''' var_list : var_list ',' var
                    | var '''
        if len(p) == 2:
            p[0] = (p[1],)
        else:
            p[0] = p[1] + (p[3],)

    def p_var(self, p):
        ''' var : INT '''
        p[0] = p[1]


    def p_blocked_op(self, p):
        ''' blocked_op : '(' op_expression ')' '''
        p[0] = p[2]

    def p_special_statement(self, p):
        ''' special_statement : blocked_op blocked_content'''
        p[0] = (p[1], p[2])

    def p_closed_statement(self, p):
        ''' closed_statement : ';'
                             | statement ';' '''
        if p[1] != ";":
            p[0] = p[1]

    def p_for_first(self, p):
        ''' for_first : ';'
                      | assign_op ';'
                      | declaration ';' '''
        if p[1] != ";":
            p[0] = p[1]

    def p_for_second(self, p):
        ''' for_second : ';'
                       | op_expression ';' '''
        if p[1] != ";":
            p[0] = p[1]

    def p_statement(self, p):
        ''' statement : print
                      | read
                      | op_expression
                      | declaration '''
        p[0] = p[1]

    def p_print(self, p):
        ''' print : PRINT '(' op_expression ')' '''
        p[0] = ('PRINT', p[3])

    def p_read(self, p):
        ''' read : READ '(' ID ')' '''
        if self.symbol_exists(p[3]):
            v = self.symbol_table[p[3]]
            v.value = None
            v.init_pos = p.lexer.lineno
            p[0] = ('READ', v.name)
        else:
            print("Variable {} no definida en la linea  {}".format(
                p[3], p.lexer.lineno))
            raise SyntaxError()

    def p_declaration(self, p):
        ''' declaration : type ID
                        | type ID '=' op_expression '''
        if p[2] in self.symbol_table:
            value = self.symbol_table[p[2]]
            print("Variable {} en la linea {}, redefinicion en la linea {}".format(
                p[2], value.declaration_pos, p.lexer.lineno))
            raise SyntaxError()
        elif len(p) == 3:
            self.symbol_table[p[2]] = Symbol(
                p[2], p[1], p.lexer.lineno)
            p[0] = ('DECL', p[2], p[1])
        else:
            new_value = None
            if p[4][0] == 'val':
                new_value = p[4][2]
            self.symbol_table[p[2]] = Symbol(
                p[2], p[1], p.lexer.lineno, new_value, p.lexer.lineno)
            p[0] = ('DECL', p[2], p[1], ('=', p[1],
                    ('ID', p[1].upper(), p[2]), p[4]))

    def p_op_expression(self, p):
        ''' op_expression : val
                          | assign_op
                          | bin_op
                          | '-' val %prec UMINUS
                          | '(' op_expression ')' '''
        if p[1] == '-':
            if p[2][1] != "INT" and p[2][1] != "FLOAT":
                print("No se puede utilizar negativo con un valor que no es numerico en la linea {}".format(
                    p.lexer.lineno))
            if p[2][0] == "val":
                p[0] = ('val', p[2][1], -p[2][2])
            else:
                p[0] = ('-', p[2][1], p[2])
        elif p[1] == '(':
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_assign_op(self, p):
        ''' assign_op : ID '=' op_expression '''
        if not self.symbol_exists(p[1]):
            print("Variable {} sin definir en la linea {}".format(
                p[1], p.lexer.lineno))
            raise SyntaxError()
        v1 = self.symbol_table[p[1]]
        if v1.type != p[3][1]:
            print(
                "Los tipos son incompatbibles {} y {}, en la linea {}".format(v1.type, p[3][1], p.lexer.lineno))
            raise SyntaxError()
        if p[3][0] == 'val':
            v1.value = p[3][2]
        v1.init_pos = p.lexer.lineno
        p[0] = ('=', v1.type, ('ID', v1.type, v1.name), p[3])

    def bin_op_conversions(self, p):
        if p[1][1] == "FLOAT" and p[3][1] == "INT" and p[2] != '^':
            p[3] = self.to_float(p[3])
        if p[1][1] == "INT" and p[3][1] == "FLOAT" and p[2] != '^':
            p[1] = self.to_float(p[1])
        if p[1][1] == "INT" and p[3][1] == "STRING" or p[1][1] == "FLOAT" and p[3][1] == "STRING":
            p[1] = self.to_string(p[1])
        if p[1][1] == "STRING" and p[3][1] == "INT" or p[1][1] == "STRING" and p[3][1] == "FLOAT":
            p[3] = self.to_string(p[3])
        if p[1][1] != p[3][1]:
            print(
                "El tipo {} and {}, son incompatibles en la linea  {}".format(p[1][1], p[3][1], p.lexer.lineno))
            raise SyntaxError()

    def p_bin_op(self, p):
        ''' bin_op : op_expression '+' op_expression
                   | op_expression '-' op_expression
                   | op_expression '*' op_expression
                   | op_expression '/' op_expression
                   | op_expression '^' op_expression
                   | op_expression '>' op_expression
                   | op_expression '<' op_expression
                   | op_expression AND op_expression
                   | op_expression OR op_expression
                   | op_expression EQUALS op_expression
                   | op_expression DIFFERENT op_expression
                   | op_expression GREAT_EQUAL op_expression
                   | op_expression LESS_EQUAL op_expression '''
        self.bin_op_conversions(p)
        if (
            (
                p[2] == "-" or
                p[2] == "*" or
                p[2] == "/" or
                p[2] == "^" or
                p[2] == ">" or
                p[2] == "<" or
                p[2] == "<=" or
                p[2] == ">="
            ) and (p[1][1] == "BOOL" or p[1][1] == "STRING")
        ) or (
            p[2] == "+" and p[1][1] == "BOOL"
        ) or (
            (p[2] == "&&" or p[2] == "||")
            and (p[1][1] == "FLOAT" or p[1][1] == "INT" or p[1][1] == "STRING")
        ):
            print(
                "Tipo incompatible {} con la operacion {}, en la linea {}".format(p[1][1], p[2], p.lexer.lineno))
            raise SyntaxError()
        if p[1][0] == "val" and p[3][0] == "val" and p[2] != "^":
            if p[2] == "&&":
                p[2] = " and "
            if p[2] == "||":
                p[2] = " or "
            string_op = str(p[1][2]) + p[2] + str(p[3][2])
            ans = eval(string_op)
            if type(ans) == str:
                p[0] = ('val', "STRING", '"'+ans+'"')
            else:
                p[0] = ('val', type(ans).__name__.upper(), ans)
        elif p[1][0] == "val" and p[3][0] == "val" and p[2] == "^":
            ans = pow(p[1][2], p[3][2])
            curr_type = None
            if p[3][2] % 1 == 0 and p[1][1] == "INT":
                curr_type = "INT"
            elif p[3][2] % 1 == 0 and p[1][1] == "FLOAT":
                curr_type = "FLOAT"
            elif p[3][2] % 1 != 0:
                curr_type = "FLOAT"
            p[0] = ('val', curr_type, ans)
        else:
            p[0] = (p[2], p[1][1], p[1], p[3])

    def to_float(p, t):
        if t[0] == "val":
            return ("val", "FLOAT", float(t[2]))
        return ("to_float", "FLOAT", t)

    def to_string(p, t):
        if t[0] == "val":
            return ("val", "STRING", str(t[2]))
        return ("to_string", "STRING", t)

    def p_val(self, p):
        ''' val : ID
                | lit_val '''
        if type(p[1]) == str:
            if not self.symbol_exists(p[1]):
                print("Variable {} no se ha definido en la linea {}".format(
                    p[1], p.lexer.lineno))
                exit
                raise SyntaxError()
            val = self.symbol_table[p[1]]
            if not val.initialized():
                print("Variable {} no se ha inicializado en la linea {}".format(
                    val.name, p.lexer.lineno))
                exit
                raise SyntaxError()
            p[0] = ('ID', val.type, val.name)
        else:
            p[0] = ('val',) + p[1]

    def p_lit_val(self, p):
        ''' lit_val : INT_VALUE
                    | FLOAT_VALUE
                    | STRING_VALUE
                    | BOOLEAN_VALUE_T
                    | BOOLEAN_VALUE_F '''
        if p[1] == 'true' or p[1] == 'false':
            p[0] = ('BOOL', True) if p[1] == 'true' else ('BOOL', False)
        elif type(p[1]) == int:
            p[0] = ('INT', p[1])
        elif type(p[1]) == float:
            p[0] = ('FLOAT', p[1])
        elif type(p[1]) == str:
            p[0] = ('STRING', p[1])

    def p_type(self, p):
        ''' type : INT
                 | FLOAT
                 | STRING
                 | BOOLEAN '''
        p[0] = p[1]

    def p_error(self, p):
        if p:
            print(
                "Simbolo {} no esperado en la linea {}".format(p.value, p.lineno))
            exit
        else:
            print(
                "Unexpected EOF")
            exit

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)
        return self.parser