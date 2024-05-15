#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

/*
    1. calculate fitness of the prompts
    2. find 2 best prompts
    3. crossover 2 best prompts to generate a child prompt that is better then the parent prompts
    4. mutate the child prompt to make a better prompt
    5. repeat steps 1-4 until the target is reached
*/

struct PromptOutput {
    std::string prompt;
    std::string output;
    bool compiles;
    double halsteadVolume;
    double fitness; // Change int to double for fitness
};

// Function to calculate the Levenshtein distance between two strings
int levenshtein_distance(const std::string& s1, const std::string& s2) {
    int m = s1.length();
    int n = s2.length();
    
    std::vector<std::vector<int>> dp(m + 1, std::vector<int>(n + 1, 0));
    
    for (int i = 0; i <= m; ++i) {
        dp[i][0] = i;
    }
    for (int j = 0; j <= n; ++j) {
        dp[0][j] = j;
    }
    
    for (int i = 1; i <= m; ++i) {
        for (int j = 1; j <= n; ++j) {
            if (s1[i - 1] == s2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = 1 + std::min({dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]});
            }
        }
    }
    
    return dp[m][n];
}

void fitness(const std::string& target, std::vector<PromptOutput>& po) {

    /*
    need a better heuristic to find similarities LLM output and existing code
    ideally something similar like the metrics in spreadsheets

    Better code is:
        compiles
        low Halsted volume
        low Levenshtein distance
        low Lines of Code
        low amount of errors
    */

    for (auto& entry : po) {
        int distance = levenshtein_distance(target, entry.output);
        entry.fitness = 1.0 - static_cast<double>(distance) / std::max(target.length(), entry.output.length());
    }
}

//calling the bashscript that will compile the output of the LLM, when the code compiles 1 is returned otherwise 0
int executeBashScript{
    return 0;
}

int main() {
    std::string target = "Hello, World, tonight we party!";
    std::vector<PromptOutput> po{
        {"Hey, create a message to the world", "Greetings, Universe, tonight we party!", false},
        {"Generate me a message that we party", "Heere, World, toniht weparty!"},
        {"do me a favor and make this", "Hello, onight we party!"},
    };

    fitness(target, po);

    //Sorting and outputing the best candidate

    std::vector<std::pair<std::string, double>> promptAndString;
    for(auto& entry : po) {
        promptAndString.push_back({entry.prompt, entry.fitness});
    }
    std::sort(promptAndString.begin(), promptAndString.end(), [](const std::pair<std::string, double>& a, const std::pair<std::string, double>& b) {
        return a.second > b.second;
    });

    //first sorted -> prompt is the first item in the entry
    std::cout << "Best prompt: " << promptAndString[0].first << " " << promptAndString[0].second << std::endl;
    std::cout << promptAndString[1].first << std::endl;

    return 0;
}