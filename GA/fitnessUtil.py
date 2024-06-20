import logging
import radon.complexity as radon_complexity
import radon.metrics as radon_metrics
import radon.raw as radon_raw
# import language_tool_python

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

def Complexity():
    return 1

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
