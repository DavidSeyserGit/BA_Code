import logging
import re
import math
from collections import Counter
#import radon.complexity as radon_complexity
#import radon.metrics as radon_metrics
#import radon.raw as radon_raw
# import language_tool_python

def halsteadVolume(code):
    # Tokenize the code
    tokens = re.findall(r'\b\w+\b|[^\w\s]', code)

    # Define operators and categorize tokens
    operators = set(['+', '-', '*', '/', '%', '++', '--', '==', '!=', '>', '<', '>=', '<=', 
                     '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '=', '+=', '-=', 
                     '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>='])
    operands = set()

    operator_count = Counter()
    operand_count = Counter()

    for token in tokens:
        if token in operators:
            operator_count[token] += 1
        else:
            operands.add(token)
            operand_count[token] += 1

    # Calculate Halstead metrics
    n1 = len(operator_count)
    n2 = len(operand_count)
    N1 = sum(operator_count.values())
    N2 = sum(operand_count.values())

    n = n1 + n2
    N = N1 + N2

    if n == 0:
        V = 0
    else:
        V = N * math.log2(n)

    if n2 == 0:
        D = 0
    else:
        D = (n1 / 2) * (N2 / n2)

    E = D * V

    return 1/V #higher V indicates more complex code


def Complexity(code):
    tokens = re.findall(r'\b\w+\b|[^\w\s]', code)

    complexity_keywords = set(['if', 'else', 'while', 'for', 'case', '&&', '||', 'catch', 'throw', '?', 'return'])

    nodes = 1
    edges = 0

    # Count the nodes and edges based on the tokens
    for token in tokens:
        if token in complexity_keywords:
            nodes += 1
            edges += 2
        elif token == 'else':
            edges += 1

    P = 1  
    cyclomatic_complexity = edges - nodes + 2 * P

    return 1/cyclomatic_complexity


def CodePromptLength(prompt, code):
    if not isinstance(code, str) or code is None:
        code_length = float('inf')  #penalize for no code
    else:
        code_length =  len(code)
        
    prompt_length = len(prompt)
    
    return prompt_length, code_length


def LevenshteinDistance(code, kc):
    if code is None:
        return float('inf')
    
    with open('target.txt', 'r') as file:
        target = file.read()

    m = len(code)
    n = len(target)
    
    # Create a matrix to store the distances
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases: initialize first row and column
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Compute the distances
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if code[i - 1] == target[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
    # Return the Levenshtein distance
    return kc / ((dp[m][n])+1)

def hasDoubleWords(prompt): #if any duplicate words are present the score gets SUBTRACTED from the current score
    words = prompt.lower().split()
    return (len(words) != len(set(words))) #set only allows one instance of every entry so when words == set(words), any word is not duplicate

def grammarScore():
    pass


'''
radon only works for python code
    -> write the same for a cpp code.

def Complexity(code):
    if code is None:
        return 0
    try:
        #cyclomatic complexity
        complexity = radon_complexity.cc_visit(code)
        avgComplexity = sum(c.complexity for c in complexity) / len(complexity) if complexity else 0
        # Halstead Metrics
        halsteadMetrics = radon_metrics.h_visit(code)
        
        # Raw Metrics (LOC, comments, etc.)
        rawMetrics = radon_raw.analyze(code)
        
        metrics = {
            'cyclomatic_complexity': avgComplexity,
            'halstead_volume': halsteadMetrics.total[0],
            'halstead_difficulty': halsteadMetrics.total[1],
            'halstead_effort': halsteadMetrics.total[2],
            'lines_of_code': rawMetrics.loc,
            'comment_density': rawMetrics.comments / rawMetrics.loc if rawMetrics.loc > 0 else 0
        }
        print(metrics)
        weights = {
            'cyclomatic_complexity': 0.1,
            'halstead_volume': 0.1,
            'halstead_difficulty': 0.1,
            'halstead_effort': 0.1,
            'lines_of_code': 0.1,
            'comment_density': 1
        }
        
        fitness = (
            weights['cyclomatic_complexity'] * metrics['cyclomatic_complexity'] +
            weights['halstead_volume'] * metrics['halstead_volume'] +
            weights['halstead_difficulty'] * metrics['halstead_difficulty'] +
            weights['halstead_effort'] * metrics['halstead_effort'] +
            weights['lines_of_code'] * metrics['lines_of_code'] +
            weights['comment_density'] * metrics['comment_density']
        
        )
        return fitness
    #apperantly gets a syntax error here with cpp code.
    except SyntaxError as se:
        logging.error(f"Syntax error in code: {se}")
        return 0
        
    except Exception as e:
        logging.error(f"Error analyzing code metrics: {e}")
        return 0

'''
