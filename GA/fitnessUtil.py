import logging

def CodePromptLength(code, prompt, ka, kb):
    if not isinstance(code, str) or code is None:
        code_length = float('inf')  #penalize for no code
    else:
        code_length = kb * len(code)
        
    prompt_length = ka * len(prompt)
    
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
                
    logging.debug(f"Levenshtein distance: {dp[m][n]}")
    # Return the Levenshtein distance
    return kc / ((dp[m][n])+1)