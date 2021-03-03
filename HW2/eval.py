from data import get_doc_ids, separate_posting_and_skip, get_posting_and_skip
from utility import list_to_string, add_skip_ptr

def evaluate_postfix(postfix_expr):
    '''
    Evaluates the given string list postfix expression
    '''
    stack = [] # last in, first out
    for item in postfix_expr:
        if item == "NOT":
            # apply NOT operator to popped operand
            # push result back onto stack
            curr = stack.pop() # may be operand or an intermediate NOT
            res = eval_simple(curr)
            if curr[0] == 'operand' or curr[0] == 'res':
                stack.append(['not', res])
            else: # previously was a NOT, will cancel out
                stack.append(['res', res])
        elif item == "AND":
            # apply AND/OR operator to popped operands
            # push result back onto stack
            res = eval_AND(stack.pop(), stack.pop())
            stack.append(['res', res])
        elif item == "OR":
            res = eval_OR(stack.pop(), stack.pop())
            stack.append(['res', res])
        else:
            # item is an operand
            stack.append(['operand', item])
    
    # stack will only have one item now: the final result
    assert len(stack) == 1
    res = stack.pop()

    if res[0] == 'operand': # if the query is simply a term
        res = eval_simple(res)
    elif res[0] == 'not': # left with an intermediate 'not'
        res = eval_NOT(res)
    else:
        res = res[1]
    reg_list, skip_list = separate_posting_and_skip(res)
    
    return list_to_string(reg_list).rstrip()

def eval_simple(op):
    '''
    Simplest query to get documents that contain a term
    '''
    posting, skips = get_posting_and_skip(op)
    res = ''
    for item in posting:
        res += str(item) + ' '
    return res

# FIXME: OR does not need skip list, maybe make another method to get just the posting list?
def eval_NOT(op):
    '''
    Gets documents that do not contain `op`
    '''
    posting, skips = get_posting_and_skip(op)

    res = []
    
    for doc_id in get_doc_ids().rstrip().split(' '):
        int_form = int(doc_id) # type casting string to integer for comparison
        if int_form not in posting:
            res.append(int_form)

    res = add_skip_ptr(res)
    
    return res

# FIXME: OR does not need skip list, maybe make another method to get just the posting list?
def eval_OR(op1, op2):
    '''
    Gets union of documents containing `op1` with documents containing `op2`
    '''
    posting1, skips1 = get_posting_and_skip(op1)
    posting2, skips2 = get_posting_and_skip(op2)

    # update intermediate NOT to be actual result
    if op1[0] == 'not':
        postings_str = eval_NOT(op1).rstrip()
        posting1, skips1 = separate_posting_and_skip(postings_str)
    if op2[0] == 'not':
        postings_str = eval_NOT(op2).rstrip()
        posting2, skips2 = separate_posting_and_skip(postings_str)

    ptr1 = 0
    ptr2 = 0
    res = []
    while ptr1 < len(posting1) and ptr2 < len(posting2):
        if posting1[ptr1] == posting2[ptr2]:
            res.append(posting1[ptr1])
            ptr1 += 1
            ptr2 += 1
        elif posting1[ptr1] > posting2[ptr2]:
            res.append(posting2[ptr2])
            ptr2 += 1
        elif posting2[ptr2] > posting1[ptr1]:
            res.append(posting1[ptr1])
            ptr1 += 1
    if ptr1 == len(posting1) and ptr2 < len(posting2): # still have postings in posting2 but no more in posting1
        rem_items = posting2[ptr2:]
        for item in rem_items:
            res.append(item)
    elif ptr2 == len(posting2) and ptr1 < len(posting1): # still have postings in posting1 but no more in posting2
        rem_items = posting1[ptr1:]
        for item in rem_items:
            res.append(item)
    
    res = add_skip_ptr(res)

    return res
    
def eval_AND(op1, op2):
    '''
    Gets intersection of documents containing `op1` with documents containing `op2`
    '''
    posting1, skips1 = get_posting_and_skip(op1)
    posting2, skips2 = get_posting_and_skip(op2)

    res = []
    if op1[0] == 'not' and op2[0] != 'not': # NOT a AND b
        for posting in posting2:
            if posting not in posting1:
                res.append(posting)
    elif op1[0] != 'not' and op2[0] == 'not': # a AND NOT b
        for posting in posting1:
            if posting not in posting2:
                res.append(posting)
    elif op1[0] == 'not' and op2[0] == 'not': # NOT a AND NOT b
        for doc_id in get_doc_ids().rstrip().split(' '):
            int_form = int(doc_id)
            if int_form not in posting1 and int_form not in posting2:
                res.append(int_form)
    else: # pure a AND b
        ptr1 = 0
        ptr2 = 0
        while ptr1 < len(posting1) and ptr2 < len(posting2):
            if posting1[ptr1] == posting2[ptr2]:
                res.append(posting1[ptr1])
                ptr1 += 1
                ptr2 += 1
            elif posting1[ptr1] > posting2[ptr2]:
                if skips2[ptr2] is not None and posting2[skips2[ptr2]] <= posting1[ptr1]:
                    ptr2 = skips2[ptr2]
                else:
                    ptr2 += 1
            elif posting2[ptr2] > posting1[ptr1]:
                if skips1[ptr1] is not None and posting1[skips1[ptr1]] <= posting2[ptr2]:
                    ptr1 = skips1[ptr1]
                else:
                    ptr1 += 1

    res = add_skip_ptr(res)

    return res