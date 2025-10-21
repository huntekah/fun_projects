"""
LeetCode Card Creation Module

This module processes LeetCode problem descriptions and generates structured
flashcards using LLM analysis. The cards are designed for effective spaced
repetition learning with multiple solution approaches.
"""

from typing import Dict, List
from tqdm import tqdm
from src.models.leetcode_cards import LeetcodeCard, FetchedLeetcodeProblem
from connectors.llm.structured_gemini import LLMClient

LEETCODE_CARD_PROMPT = r"""
Persona
You are an expert programmer and computer science educator with deep knowledge of algorithms, data structures, and competitive programming. Your primary skill is breaking down complex problems into their core concepts and explaining them with clarity and precision. You are creating content for educational flashcards aimed at helping users learn and internalize algorithmic patterns.

Task
Your task is to analyze a given LeetCode problem description and generate a concise summary and one or more distinct solutions. Each solution must be a self-contained, structured object that distills the essence of the approach.

Context
The generated output is for educational "flashcards." The most crucial element is the key_insight, which should capture the "aha!" moment or the core idea required to unlock the solution. The strategy should be a clear, step-by-step algorithm that is easy to follow. The code must be a minimal, clean implementation of the strategy in Python; it should be unadorned with comments unless they clarify a point not obvious from the strategy itself.

Always provide multiple solutions if they represent fundamentally different or common approaches (e.g., brute-force vs. optimized, greedy vs. dynamic programming).
Use \(\) for inline math (e.g., \(E=mc^2\)) and \[\] for display/block math.

EXAMPLES
Here are two high-quality examples of the desired output for two different LeetCode problems.

Example 1: Reorganize String
[Problem Input]
767. Reorganize String
Medium
Topics: Hash Table, String, Greedy, Sorting, Heap (Priority Queue)

Given a string `s`, rearrange the characters of `s` so that any two adjacent characters are not the same.
If possible, return any such rearrangement. Otherwise, return an empty string `""`.

Example 1:
Input: s = "aab"
Output: "aba"

Example 2:
Input: s = "aaab"
Output: ""

[Expected Output]
{
  "problem_description": "Given a string `s`, rearrange its characters so that no two adjacent characters are the same. Return the rearranged string or an empty string if impossible. 
  Constraints: `1 <= s.length <= 500`, `s` consists of lowercase English letters.",
  "solutions": [
    {
      "key_insight": "The rearrangement is impossible if any single character appears more than \\((n + 1) // 2\\) times. If the most frequent char `c` has $freq(c) > (n + 1) // 2$, there aren't enough 'other' characters to place between its occurrences. If it's possible, a greedy approach of placing characters at alternating indices (first all even, then all odd) will guarantee separation.",
      "strategy": "1. Count character frequencies and sort them from most to least frequent.\\n2. Check the impossibility condition: if the count of the most frequent character is greater than \\((n + 1) // 2\\), return `\\\"\\\"`.\\n3. Create an empty result array `res` of size `n`.\\n4. Iterate through the sorted characters. For each character, place its occurrences into the `res` array, starting at index 0 and skipping every other position (0, 2, 4, ...).\\n5. If the end of the array is reached, wrap around to the first odd index (1, 3, 5, ...) and continue placing characters.\\n6. Join and return the `res` array.",
      "complexity": "Time: \\(O(n + k \\log k)\\) where $n$ is the length of the string and $k$ is the number of unique characters (for counting and sorting frequencies). Space: \\(O(n)\\) for the result array.",
      "code": "import collections\\nclass Solution:\\n    def reorganizeString(self, s: str) -> str:\\n        n = len(s)\\n        counts = collections.Counter(s)\\n        most_common = counts.most_common()\\n        \\n        max_freq = most_common[0][1]\\n        if 2 * max_freq > n + 1:\\n            return \\\"\\\"\\n\\n        res = [\\\"\\\"]*n\\n        idx = 0\\n        \\n        for char, count in most_common:\\n            for _ in range(count):\\n                if idx >= n:\\n                    idx = 1\\n                \\n                res[idx] = char\\n                idx += 2\\n                \\n        return \\\"\\\".join(res)",
      "solution_type": "greedy"
    }
  ]
}

Example 2: Two Sum
[Problem Input]
1. Two Sum
Easy
Topics: Array, Hash Table

Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.
You may assume that each input would have exactly one solution, and you may not use the same element twice.
You can return the answer in any order.

Example:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

[Expected Output]
{
  "problem_description": "Given an array of integers `nums` and an integer `target`, find the indices of two numbers in the array that sum up to the `target`. Each input has exactly one solution, and the same element cannot be used twice.",
  "solutions": [
    {
      "key_insight": "The most straightforward approach is to check every possible pair of numbers in the array to see if they sum to the target.",
      "strategy": "1. Iterate through each element at index `i` in the array.\\n2. For each element at `i`, iterate through the rest of the array starting from index `j = i + 1`.\\n3. Check if `nums[i] + nums[j] == target`.\\n4. If they sum to the target, return the indices `[i, j]`.",
      "complexity": "Time: \\(O(n^2)\\) because the nested loops check every pair of elements. Space: \\(O(1)\\) as no extra space proportional to the input size is used.",
      "code": "class Solution:\\n    def twoSum(self, nums, target):\\n        n = len(nums)\\n        for i in range(n):\\n            for j in range(i + 1, n):\\n                if nums[i] + nums[j] == target:\\n                    return [i, j]",
      "solution_type": "brute force"
    },
    {
      "key_insight": "To find a complement (`target - current_num`) in constant time, we can use a hash map. By storing numbers we've already seen and their indices, we can check for the complement's existence in \\(O(1)\\) time as we iterate through the array.",
      "strategy": "1. Initialize an empty hash map `seen_map` to store `{value: index}` pairs.\\n2. Iterate through the `nums` array, getting both the index `i` and value `num`.\\n3. For each number, calculate its required `complement = target - num`.\\n4. Check if this `complement` already exists as a key in `seen_map`.\\n5. If it exists, we have found our pair. Return its stored index and the current index: `[seen_map[complement], i]`.\\n6. If it does not exist, add the current `num` and its index `i` to the `seen_map` for future checks.",
      "complexity": "Time: \\(O(n)\\) because we iterate through the list of $n$ elements only once. Each hash map operation (lookup and insertion) is \\(O(1)\\) on average. Space: \\(O(n)\\) to store up to $n$ elements in the hash map in the worst case.",
      "code": "class Solution:\\n    def twoSum(self, nums, target):\\n        seen = {}\\n        for i, num in enumerate(nums):\\n            complement = target - num\\n            if complement in seen:\\n                return [seen[complement], i]\\n            seen[num] = i",
      "solution_type": "hash map"
    }
  ]
}

Now analyze the following LeetCode problem and provide the structured output:

"""


def create_leetcode_card(problem_text: str) -> LeetcodeCard:
    """
    Generate a LeetcodeCard from a problem description using LLM analysis.
    
    Args:
        problem_text: The complete LeetCode problem description including
                     title, difficulty, topics, statement, examples, etc.
    
    Returns:
        LeetcodeCard: Structured flashcard with problem summary and solution approaches
    """
    # Initialize the LLM client
    llm_client = LLMClient()
    
    # Format the prompt with the problem text
    formatted_prompt = LEETCODE_CARD_PROMPT + problem_text
    
    # Generate structured response
    try:
        result: LeetcodeCard = llm_client.generate(formatted_prompt, LeetcodeCard)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Failed to generate LeetCode card: {e}")
    
    return result


def process_leetcode_problems(problems_data: List[FetchedLeetcodeProblem]) -> Dict[str, LeetcodeCard]:
    """
    Process multiple LeetCode problems and generate cards for each.
    
    Args:
        problems_data: List of validated FetchedLeetcodeProblem objects
    
    Returns:
        Dictionary mapping problem slugs to their generated LeetcodeCard objects
    """
    cards = {}
    
    # Use tqdm for progress bar
    for problem in tqdm(problems_data, desc="Generating cards", unit="problem"):
        # Format problem text for the prompt
        problem_text = f"""
{problem.problem_id}. {problem.title}
Difficulty: {problem.difficulty}
Topics: {', '.join(problem.tags)}

{problem.description}
"""
        
        try:
            card = create_leetcode_card(problem_text)
            cards[problem.slug] = card
            tqdm.write(f"✅ Generated card for: {problem.title}")
        except Exception as e:
            tqdm.write(f"❌ Failed to generate card for {problem.slug}: {e}")
            continue
    
    return cards


def load_and_validate_problems(json_file_path: str) -> List[FetchedLeetcodeProblem]:
    """
    Load problems from JSON file and validate them against the schema.
    
    Args:
        json_file_path: Path to the JSON file containing problem data
    
    Returns:
        List of validated FetchedLeetcodeProblem objects
    
    Raises:
        ValidationError: If any problem data doesn't match the expected schema
    """
    import json
    from pathlib import Path
    
    file_path = Path(json_file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Problems file not found: {json_file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # Validate each problem against the schema
    validated_problems = []
    for i, problem_dict in enumerate(raw_data):
        try:
            problem = FetchedLeetcodeProblem(**problem_dict)
            validated_problems.append(problem)
        except Exception as e:
            print(f"❌ Failed to validate problem at index {i}: {e}")
            print(f"   Problem data: {problem_dict}")
            continue
    
    print(f"✅ Successfully validated {len(validated_problems)} out of {len(raw_data)} problems")
    return validated_problems