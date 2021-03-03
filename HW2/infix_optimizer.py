from data import get_doc_freq, get_corpus_size
from utility import split_bool_expr, has_greater_or_equal_precedence

class BooleanUnit:
    def __init__(self):
        self.has_not = False
        self.has_parentheses = False
    
    def flip_has_not(self):
        self.has_not = not self.has_not
    
    def set_has_parentheses(self, has_parentheses):
        self.has_parentheses = has_parentheses

class AndExpr(BooleanUnit):
    def __init__(self, units):
        assert len(units) >= 2
        super().__init__()
        self.units = units
    
    def add_unit(self, unit):
        self.units.append(unit)
    
    def get_max_doc_freq(self):
        max_doc_freq = 0
        for i in range(len(self.units) - 1):
            max_doc_freq = min(self.units[i].get_max_doc_freq(), self.units[i + 1].get_max_doc_freq())
        return max_doc_freq
    
    def get_optimized_infix_string(self):
        sorted_units = sorted(self.units, key = lambda unit: unit.get_max_doc_freq())
        sorted_strings = map(lambda unit: unit.get_optimized_infix_string(), sorted_units)
        optimized_infix_string = " AND ".join(sorted_strings)
        if self.has_parentheses:
            optimized_infix_string = "(" + optimized_infix_string + ")"
        if self.has_not:
            optimized_infix_string = "NOT " + optimized_infix_string
        return optimized_infix_string

class OrExpr(BooleanUnit):
    def __init__(self, units):
        assert len(units) >= 2
        super().__init__()
        self.units = units
    
    def add_unit(self, unit):
        self.units.append(unit)
    
    def get_max_doc_freq(self):
        max_doc_freq = 0
        for i in range(len(self.units) - 1):
            max_doc_freq = self.units[i].get_max_doc_freq() + self.units[i + 1].get_max_doc_freq()
        return max_doc_freq
    
    def get_optimized_infix_string(self):
        sorted_units = sorted(self.units, key = lambda unit: unit.get_max_doc_freq())
        sorted_strings = map(lambda unit: unit.get_optimized_infix_string(), sorted_units)
        optimized_infix_string = " OR ".join(sorted_strings)
        if self.has_parentheses:
            optimized_infix_string = "(" + optimized_infix_string + ")"
        if self.has_not:
            optimized_infix_string = "NOT " + optimized_infix_string
        return optimized_infix_string

class Term(BooleanUnit):
    def __init__(self, term):
        super().__init__()
        self.term = term
    
    def get_max_doc_freq(self):
        if self.has_not:
            return get_corpus_size() - get_doc_freq(self.term)
        else:
            return get_doc_freq(self.term)
    
    def get_optimized_infix_string(self):
        optimized_infix_string = self.term
        if self.has_parentheses:
            optimized_infix_string = "(" + optimized_infix_string + ")"
        if self.has_not:
            optimized_infix_string = "NOT " + optimized_infix_string
        return optimized_infix_string

def create_boolean_unit(left_unit, right_unit, operator):
    if (operator == "AND" and isinstance(left_unit, AndExpr)) or (operator == "OR" and isinstance(left_unit, OrExpr)) and not left_unit.has_parentheses:
        left_unit.add_unit(right_unit)
        return left_unit
    elif operator == "AND":
        return AndExpr([left_unit, right_unit])
    elif operator == "OR":
        return OrExpr([left_unit, right_unit])
    else:
        raise ValueError(f"Could not create {operator} BooleanUnit")

def transform_infix_to_boolean_unit(expression):
    '''
    Translates string infix boolean expression into BooleanUnit
    Operators handled: AND, OR, NOT, ()
    Assumptions: no nested (); expression is valid
    '''
    split_expr = split_bool_expr(expression)
    output_queue = [] # first in, first out
    operator_stack = [] # last in, first out
    unary_list = []
    for item in split_expr:
        if item == "NOT":
            unary_list.append(item)
        elif item == "AND" or item == "OR":
            while ((len(operator_stack) > 0 and (operator_stack[-1] == "AND" or operator_stack[-1] == "OR")) and has_greater_or_equal_precedence(operator_stack[-1], item) and operator_stack[-1] != "("):
                right_unit = output_queue.pop()
                left_unit = output_queue.pop()
                output_queue.append(create_boolean_unit(left_unit, right_unit, operator_stack.pop()))
            operator_stack.append(item)
        elif item == "(":
            operator_stack.append(item)
            if len(unary_list) > 0:
                unary_list.append(item)
        elif item == ")":
            while operator_stack[-1] != "(":
                right_unit = output_queue.pop()
                left_unit = output_queue.pop()
                output_queue.append(create_boolean_unit(left_unit, right_unit, operator_stack.pop()))
            if operator_stack[-1] == "(":
                operator_stack.pop()
                output_queue[-1].set_has_parentheses(True)
            if len(unary_list) > 0 and unary_list[-1] == "(":
                unary_list.pop()
                while len(unary_list) > 0 and unary_list[-1] != "(":
                    unary_list.pop()
                    output_queue[-1].flip_has_not()
        else:
            # item is an operand
            output_queue.append(Term(item))
            if len(unary_list) > 0:
                while len(unary_list) > 0 and unary_list[-1] != "(":
                    unary_list.pop()
                    output_queue[-1].flip_has_not()
    
    for operator in reversed(operator_stack):
        right_unit = output_queue.pop()
        left_unit = output_queue.pop()
        output_queue.append(create_boolean_unit(left_unit, right_unit, operator))
    
    # there should now be a single BooleanUnit left in the output queue, representing the original infix boolean expression
    return output_queue[0]

def optimize_infix(infix_query):
    '''
    Placeholder return value
    '''
    if infix_query.isspace():
        return infix_query
    else:
        return transform_infix_to_boolean_unit(infix_query).get_optimized_infix_string()