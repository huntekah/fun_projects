from typing import List
from pydantic import BaseModel, Field


class FetchedLeetcodeProblem(BaseModel):
    """Represents raw LeetCode problem data as fetched from the API."""
    
    slug: str = Field(..., description="Problem slug/handle (e.g., 'two-sum')")
    title: str = Field(..., description="Problem title (e.g., 'Two Sum')")
    problem_id: str = Field(..., description="Problem number (e.g., '1')")
    description: str = Field(..., description="Complete problem description with examples and constraints")
    difficulty: str = Field(..., description="Problem difficulty (Easy/Medium/Hard)")
    category: str = Field(..., description="Problem category")
    tags: List[str] = Field(..., description="List of topic tags for the problem")
    
    def get_description_url(self) -> str:
        return f"https://leetcode.com/problems/{self.slug}/description/"


class LeetCodeSolution(BaseModel):
    """Represents a solution to a LeetCode problem."""
    
    key_insight: str = Field(..., description="The main insight or approach needed to solve the problem")
    strategy: str = Field(..., description="Step-by-step strategy or algorithm description")
    complexity: str = Field(..., description="Time and space complexity analysis")
    code: str = Field(..., description="Minimal implementation code for the solution")
    solution_type: str = Field(..., description="Type of solution, which is a hint for the approach (e.g., 'brute force', 'greedy bottom up', 'dynamic programming with memoization', 'two pointers', etc.)")


class LeetcodeCard(BaseModel):
    """Represents a LeetCode problem flashcard."""
    
    problem_description: str = Field(..., description="Problem summary. Should include problem constraints and examples, using MathJax when necessary.")
    solutions: List[LeetCodeSolution] = Field(..., description="List of different solution approaches for the problem")
    
class AnkiLeetcodeCard(BaseModel):
    """Represents the Anki flashcard format for a LeetCode problem."""
    
    problem_description: str = Field(..., description="Problem summary. Should include problem constraints and examples, using MathJax when necessary.")
    key_insight: str = Field(..., description="The main insight or approach needed to solve the problem")
    strategy: str = Field(..., description="Step-by-step strategy or algorithm description")
    complexity: str = Field(..., description="Time and space complexity analysis")
    code: str = Field(..., description="Minimal implementation code for the solution")
    solution_type: str = Field(..., description="Type of solution (e.g., 'brute force', 'greedy', 'dynamic programming', 'two pointers', etc.)")
    description_url: str = Field(..., description="LeetCode problem description URL")
    problem_id: str = Field(..., description="Problem number (e.g., '1')")
    difficulty: str = Field(..., description="Problem difficulty (Easy/Medium/Hard)")
    tags: List[str] = Field(..., description="List of topic tags for the problem")
    title: str = Field(..., description="Problem title (e.g., 'Two Sum')")


def create_leetcode_anki_cards(fetched_problem: FetchedLeetcodeProblem, leetcode_card: LeetcodeCard) -> List[AnkiLeetcodeCard]:
    """
    Create AnkiLeetcodeCard objects from a FetchedLeetcodeProblem and LeetcodeCard.
    
    Args:
        fetched_problem: The original problem data from LeetCode API
        leetcode_card: The LLM-generated card with solutions
    
    Returns:
        List of AnkiLeetcodeCard objects, one for each solution approach
    """
    anki_cards = []
    
    for solution in leetcode_card.solutions:
        anki_card = AnkiLeetcodeCard(
            problem_description=leetcode_card.problem_description,
            key_insight=solution.key_insight,
            strategy=solution.strategy,
            complexity=solution.complexity,
            code=solution.code,
            solution_type=solution.solution_type,
            description_url=fetched_problem.get_description_url(),
            problem_id=fetched_problem.problem_id,
            difficulty=fetched_problem.difficulty,
            tags=fetched_problem.tags,
            title=fetched_problem.title,
        )
        anki_cards.append(anki_card)
    
    return anki_cards

    