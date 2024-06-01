def CodePromptLength(code, prompt, ka , kb):
    if type(code) != str:
        codeLenth = 100000
    promptLength = ka*(len(prompt))
    codeLenth = kb*(len(code))
        
    return promptLength, codeLenth


    #maintainability index
    #make a levenshtein distance test
        # https://www.geeksforgeeks.org/introduction-to-levenshtein-distance/