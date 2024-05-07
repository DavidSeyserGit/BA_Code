#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

struct PromptOutput {
    std::string prompt;
    std::string output;
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
    for (auto& entry : po) {
        int distance = levenshtein_distance(target, entry.output);
        entry.fitness = 1.0 - static_cast<double>(distance) / std::max(target.length(), entry.output.length());
    }
}

int main() {
    std::string target = "Hello, World, tonight we party!";
    std::vector<PromptOutput> po{
        {"Hey, create a message to the world", "Greetings, Universe, tonight we party!"},
        {"Generate me a message that we party", "Heere, World, toniht weparty!"},
        {"do me a favor and make this", "Hello, onight we party!"},
    };

    fitness(target, po);

    std::vector<PromptOutput> po_and_fitness;

    // Create a vector with the prompts and the fitness values
    for (auto& entry : po) {
        po_and_fitness.push_back({entry.prompt, entry.output, entry.fitness});
    }

    std::sort(po_and_fitness.begin(), po_and_fitness.end(),
          [](const PromptOutput& a, const PromptOutput& b) {
              return a.fitness > b.fitness;
          });

    // Print all fitness values (now sorted)
    for (auto& entry : po_and_fitness) {
    std::cout << "Fitness: " << entry.fitness << ", Prompt: " << entry.prompt << std::endl;
    }

    //cut the string in half of po_and_fitness.at(0).output
    std::string max_half = po_and_fitness.at(0).output.substr(0, po_and_fitness.at(0).output.size() / 2);
    //change it so that the second half is used from po_and_fitness.at(1).output
    std::string max2_half = po_and_fitness.at(1).output.substr(po_and_fitness.at(1).output.size() / 2, po_and_fitness.at(1).output.size() / 2);

    std::cout << "Max half: " << max_half << std::endl;
    std::cout << "Max2 half: " << max2_half << std::endl;

    std::string new_string = max_half + max2_half;

    std::cout << "New string: " << new_string << std::endl;

    return 0;
}