def CodePromptLength(code, prompt, ka , kb):
    
    promptLength = ka*(len(prompt))
    codeLenth = kb*(len(code))
        
    return promptLength, codeLenth


    #maintainability index
    #make a levenshtein distance test
        # https://www.geeksforgeeks.org/introduction-to-levenshtein-distance/