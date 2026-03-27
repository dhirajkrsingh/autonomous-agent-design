"""
Example 2: Goal-Oriented Agent
================================
An agent that decomposes high-level goals into sub-goals and pursues them
using a priority queue. Simulates a research assistant agent.

Run: python examples/02_goal_oriented_agent.py
"""

import heapq
import time
from dataclasses import dataclass, field
from enum import Enum


class GoalStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(order=True)
class Goal:
    priority: int
    name: str = field(compare=False)
    description: str = field(compare=False)
    sub_goals: list = field(default_factory=list, compare=False)
    status: GoalStatus = field(default=GoalStatus.PENDING, compare=False)
    preconditions: list = field(default_factory=list, compare=False)
    result: str = field(default="", compare=False)


class GoalOrientedAgent:
    """Agent that pursues goals through decomposition and prioritization."""

    def __init__(self, name: str):
        self.name = name
        self.goal_queue = []
        self.completed_goals = []
        self.world_state = set()
        self.capabilities = {
            "search_web": self._search_web,
            "summarize": self._summarize,
            "analyze": self._analyze,
            "write_report": self._write_report,
            "validate": self._validate,
        }

    def add_goal(self, goal: Goal):
        heapq.heappush(self.goal_queue, goal)
        print(f"  [GOAL] Added: '{goal.name}' (priority={goal.priority})")

    def decompose_goal(self, goal: Goal) -> list:
        """Break a high-level goal into actionable sub-goals."""
        decompositions = {
            "research_topic": [
                Goal(1, "search_sources", "Find relevant sources", preconditions=[]),
                Goal(2, "read_papers", "Read and extract key info", preconditions=["search_sources"]),
                Goal(3, "synthesize", "Combine findings", preconditions=["read_papers"]),
            ],
            "write_report": [
                Goal(1, "create_outline", "Create report structure", preconditions=[]),
                Goal(2, "write_sections", "Write each section", preconditions=["create_outline"]),
                Goal(3, "review_edit", "Review and polish", preconditions=["write_sections"]),
            ],
            "validate_results": [
                Goal(1, "cross_reference", "Cross-check with sources", preconditions=[]),
                Goal(2, "fact_check", "Verify key claims", preconditions=["cross_reference"]),
            ],
        }
        sub_goals = decompositions.get(goal.name, [])
        if sub_goals:
            print(f"  [DECOMPOSE] '{goal.name}' -> {len(sub_goals)} sub-goals")
            for sg in sub_goals:
                print(f"    - {sg.name} (preconditions: {sg.preconditions})")
        return sub_goals

    def can_pursue(self, goal: Goal) -> bool:
        """Check if all preconditions are met."""
        return all(pre in self.world_state for pre in goal.preconditions)

    def pursue_goal(self, goal: Goal) -> bool:
        """Attempt to achieve a goal."""
        if not self.can_pursue(goal):
            print(f"  [BLOCKED] '{goal.name}' - waiting for: {[p for p in goal.preconditions if p not in self.world_state]}")
            goal.status = GoalStatus.BLOCKED
            return False

        goal.status = GoalStatus.ACTIVE
        print(f"  [PURSUING] '{goal.name}': {goal.description}")

        # Simulate work
        time.sleep(0.1)

        # Try decomposition first
        sub_goals = self.decompose_goal(goal)
        if sub_goals:
            for sg in sub_goals:
                self.add_goal(sg)
            goal.status = GoalStatus.PENDING
            return True

        # Execute atomic goal
        success = self._execute(goal)
        if success:
            goal.status = GoalStatus.COMPLETED
            goal.result = f"Completed: {goal.description}"
            self.world_state.add(goal.name)
            self.completed_goals.append(goal)
            print(f"  [DONE] '{goal.name}' -> world state updated")
        else:
            goal.status = GoalStatus.FAILED
            print(f"  [FAILED] '{goal.name}'")
        return success

    def _execute(self, goal: Goal) -> bool:
        """Execute an atomic (non-decomposable) goal."""
        for cap_name, cap_fn in self.capabilities.items():
            if cap_name in goal.name or cap_name in goal.description.lower():
                return cap_fn(goal)
        # Default execution for simple goals
        print(f"  [EXEC] Performing: {goal.description}")
        return True

    def _search_web(self, goal):
        print(f"  [SEARCH] Searching for: {goal.description}")
        return True

    def _summarize(self, goal):
        print(f"  [SUMMARIZE] Creating summary for: {goal.description}")
        return True

    def _analyze(self, goal):
        print(f"  [ANALYZE] Analyzing: {goal.description}")
        return True

    def _write_report(self, goal):
        print(f"  [WRITE] Drafting: {goal.description}")
        return True

    def _validate(self, goal):
        print(f"  [VALIDATE] Checking: {goal.description}")
        return True

    def run(self, max_iterations: int = 20):
        """Main loop: pick highest-priority achievable goal and pursue it."""
        print(f"\n{'='*60}")
        print(f"  Agent '{self.name}' starting goal pursuit")
        print(f"{'='*60}")

        iteration = 0
        while self.goal_queue and iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} (queue size: {len(self.goal_queue)}) ---")

            # Find first achievable goal
            temp = []
            goal = None
            while self.goal_queue:
                candidate = heapq.heappop(self.goal_queue)
                if self.can_pursue(candidate):
                    goal = candidate
                    break
                else:
                    temp.append(candidate)
            for t in temp:
                heapq.heappush(self.goal_queue, t)

            if goal is None:
                print("  [STUCK] No achievable goals. Checking for blocked goals...")
                if temp:
                    # Force the first blocked goal (break deadlock)
                    goal = heapq.heappop(self.goal_queue)
                    print(f"  [FORCE] Attempting blocked goal: '{goal.name}'")
                    for pre in goal.preconditions:
                        self.world_state.add(pre)
                else:
                    break

            self.pursue_goal(goal)

        print(f"\n{'='*60}")
        print(f"  Completed {len(self.completed_goals)} goals in {iteration} iterations")
        for g in self.completed_goals:
            print(f"    [OK] {g.name}: {g.result}")


if __name__ == "__main__":
    print("=== Goal-Oriented Research Agent ===")

    agent = GoalOrientedAgent("ResearchBot")

    # High-level mission
    agent.add_goal(Goal(1, "research_topic", "Research multi-agent systems"))
    agent.add_goal(Goal(5, "write_report", "Write a summary report"))
    agent.add_goal(Goal(8, "validate_results", "Validate research findings"))

    agent.run()
