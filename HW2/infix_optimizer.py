from data import get_doc_freq, get_corpus_size
from utility import split_bool_expr, has_greater_or_equal_precedence

class BooleanUnit:
    '''
    Represents a boolean expression, which can be a single term (operand) or a boolean AND/OR expression.

    Attributes:
        has_not: A boolean indicating if the expression is modified by a NOT unary operator.
        has_parentheses: A boolean indicating if the expression is enclosed by parentheses.
    '''
    def __init__(self):
        self.has_not = False
        self.has_parentheses = False
    
    def flip_has_not(self):
        '''
        Sets the value of `has_not` to the opposite of its current value.
        '''
        self.has_not = not self.has_not
    
    def set_has_parentheses(self, has_parentheses):
        '''
        Sets the value of `has_parentheses` to the given value.
        '''
        self.has_parentheses = has_parentheses

class AndExpr(BooleanUnit):
    '''
    Represents a boolean AND expression. Inherits from `BooleanUnit`.

    The expression consists of two or more `BooleanUnits`, all joined by logical AND.

    Attributes:
        units: The list of `BooleanUnits` this AND expression is composed of.
    '''
    def __init__(self, units):
        assert len(units) >= 2
        super().__init__()
        self.units = units
    
    def add_unit(self, unit):
        '''
        Adds the given `BooleanUnit` to this expression's `units`.
        '''
        self.units.append(unit)
    
    def get_max_doc_freq(self):
        '''
        Returns the maximum possible document frequency of this AND expression,
        based on the maximum possible document frequencies of its `units`.
        '''
        max_doc_freq = 0
        for i in range(len(self.units) - 1):
            # the maximum document frequency of logical AND is the smallest document frequency of its operands
            max_doc_freq = min(self.units[i].get_max_doc_freq(), self.units[i + 1].get_max_doc_freq())
        return max_doc_freq
    
    def get_optimized_infix_string(self):
        '''
        Optimizes the order of evaluation of the `units` based on their document frequencies
        and returns the resulting infix boolean expression as a string.
        '''
        sorted_units = sorted(self.units, key = lambda unit: unit.get_max_doc_freq())
        sorted_strings = map(lambda unit: unit.get_optimized_infix_string(), sorted_units)
        optimized_infix_string = " AND ".join(sorted_strings)
        if self.has_parentheses:
            optimized_infix_string = "(" + optimized_infix_string + ")"
        if self.has_not:
            optimized_infix_string = "NOT " + optimized_infix_string
        return optimized_infix_string

class OrExpr(BooleanUnit):
    '''
    Represents a boolean OR expression. Inherits from `BooleanUnit`.

    The expression consists of two or more `BooleanUnits`, all joined by logical OR.

    Attributes:
        units: The list of `BooleanUnits` this OR expression is composed of.
    '''
    def __init__(self, units):
        assert len(units) >= 2
        super().__init__()
        self.units = units
    
    def add_unit(self, unit):
        '''
        Adds the given `BooleanUnit` to this expression's `units`.
        '''
        self.units.append(unit)
    
    def get_max_doc_freq(self):
        '''
        Returns the maximum possible document frequency of this OR expression,
        based on the maximum possible document frequencies of its `units`.
        '''
        max_doc_freq = 0
        for i in range(len(self.units) - 1):
            # the maximum document frequency of logical OR is the sum of the document frequencies of its operands
            max_doc_freq = self.units[i].get_max_doc_freq() + self.units[i + 1].get_max_doc_freq()
        return max_doc_freq
    
    def get_optimized_infix_string(self):
        '''
        Optimizes the order of evaluation of the `units` based on their document frequencies
        and returns the resulting infix boolean expression as a string.
        '''
        sorted_units = sorted(self.units, key = lambda unit: unit.get_max_doc_freq())
        sorted_strings = map(lambda unit: unit.get_optimized_infix_string(), sorted_units)
        optimized_infix_string = " OR ".join(sorted_strings)
        if self.has_parentheses:
            optimized_infix_string = "(" + optimized_infix_string + ")"
        if self.has_not:
            optimized_infix_string = "NOT " + optimized_infix_string
        return optimized_infix_string

class Term(BooleanUnit):
    '''
    Represents a term in a boolean expression. Inherits from `BooleanUnit`.

    The expression consists of a single term.

    Attributes:
        term: The term as a string.
    '''
    def __init__(self, term):
        super().__init__()
        self.term = term
    
    def get_max_doc_freq(self):
        '''
        Returns the document frequency of this term
        (or, if modified with NOT, its complement document frequency).
        '''
        if self.has_not:
            return get_corpus_size() - get_doc_freq(self.term)
        else:
            return get_doc_freq(self.term)
    
    def get_optimized_infix_string(self):
        '''
        Returns the term as a string. Parentheses and NOT operator are applied if present.
        '''
        optimized_infix_string = self.term
        if self.has_parentheses:
            optimized_infix_string = "(" + optimized_infix_string + ")"
        if self.has_not:
            optimized_infix_string = "NOT " + optimized_infix_string
        return optimized_infix_string

def create_boolean_unit(left_unit, right_unit, operator):
    '''
    Returns an instance of a  `BooleanUnit` child class based on the given units and operator.
    '''
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
    Transforms the given string infix boolean expression into a BooleanUnit

    Operators handled: AND, OR, NOT, ()
    
    Assumptions: no nested (); expression is valid
    '''
    split_expr = split_bool_expr(expression)
    output_queue = [] # first in, first out
    operator_stack = [] # last in, first out
    unary_list = []

    # Use a modified version of Shunting-Yard algorithm.
    # When an operator is moved from the stack to the queue,
    # it uses the two BooleanUnits at the end of the queue to form a new BooleanUnit.
    for item in split_expr:
        if item == "NOT":
            unary_list.append(item)
        elif item == "AND" or item == "OR":
            while len(operator_stack) > 0 and has_greater_or_equal_precedence(operator_stack[-1], item) and operator_stack[-1] != "(":
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
    Returns the given query with optimizations made based on document frequency.
    '''
    if infix_query.strip() == "":
        return infix_query
    else:
        return transform_infix_to_boolean_unit(infix_query).get_optimized_infix_string()