"""
Example 3: Self-Correcting Agent
==================================
An agent that monitors its own performance, detects errors,
and adjusts its strategy automatically.

Run: python examples/03_self_correcting_agent.py
"""

import random
from collections import deque


class PerformanceMonitor:
    """Tracks agent performance metrics over a sliding window."""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.success_history = deque(maxlen=window_size)
        self.error_history = deque(maxlen=window_size)
        self.latency_history = deque(maxlen=window_size)

    def record(self, success: bool, error: str = "", latency: float = 0.0):
        self.success_history.append(success)
        if error:
            self.error_history.append(error)
        self.latency_history.append(latency)

    @property
    def success_rate(self) -> float:
        if not self.success_history:
            return 1.0
        return sum(self.success_history) / len(self.success_history)

    @property
    def avg_latency(self) -> float:
        if not self.latency_history:
            return 0.0
        return sum(self.latency_history) / len(self.latency_history)

    @property
    def recent_errors(self) -> list:
        return list(self.error_history)


class Strategy:
    """Represents an execution strategy with parameters."""

    def __init__(self, name: str, params: dict):
        self.name = name
        self.params = params.copy()

    def __repr__(self):
        return f"Strategy({self.name}, {self.params})"


class SelfCorrectingAgent:
    """Agent that detects failures and adapts its strategy."""

    def __init__(self, name: str):
        self.name = name
        self.monitor = PerformanceMonitor(window_size=10)
        self.strategy = Strategy("default", {
            "retry_count": 1,
            "timeout": 5.0,
            "batch_size": 10,
            "confidence_threshold": 0.5,
        })
        self.correction_log = []
        self.total_tasks = 0
        self.total_corrections = 0

    def execute_task(self, task: dict) -> dict:
        """Execute a task with current strategy, with self-monitoring."""
        self.total_tasks += 1

        # Simulate task execution with variable difficulty
        difficulty = task.get("difficulty", 0.5)
        noise = random.uniform(-0.2, 0.2)
        effective_threshold = self.strategy.params["confidence_threshold"]

        # Higher batch size and retries help with harder tasks
        retry_bonus = self.strategy.params["retry_count"] * 0.05
        batch_penalty = max(0, (self.strategy.params["batch_size"] - 5) * 0.02)

        success_prob = (1.0 - difficulty) + retry_bonus - batch_penalty + noise
        success = random.random() < max(0.1, min(0.95, success_prob))

        latency = random.uniform(0.1, 1.0) * self.strategy.params["timeout"] / 5.0
        error = "" if success else random.choice([
            "timeout_error", "validation_error", "resource_error", "data_error"
        ])

        self.monitor.record(success, error, latency)

        result = {
            "task": task.get("name", "unknown"),
            "success": success,
            "error": error,
            "latency": round(latency, 3),
        }

        # Self-correction check after every task
        correction = self._check_and_correct()
        if correction:
            result["correction_applied"] = correction

        return result

    def _check_and_correct(self) -> str:
        """Analyze performance and apply corrections if needed."""
        corrections = []

        # Check 1: Success rate dropping
        if self.monitor.success_rate < 0.6 and len(self.monitor.success_history) >= 5:
            corrections.append(self._correct_low_success_rate())

        # Check 2: High latency
        if self.monitor.avg_latency > 0.8:
            corrections.append(self._correct_high_latency())

        # Check 3: Repeated error patterns
        errors = self.monitor.recent_errors
        if len(errors) >= 3:
            error_counts = {}
            for e in errors:
                error_counts[e] = error_counts.get(e, 0) + 1
            dominant_error = max(error_counts, key=error_counts.get)
            if error_counts[dominant_error] >= 3:
                corrections.append(self._correct_repeated_error(dominant_error))

        corrections = [c for c in corrections if c]
        if corrections:
            combined = "; ".join(corrections)
            self.correction_log.append(combined)
            self.total_corrections += 1
            return combined
        return ""

    def _correct_low_success_rate(self) -> str:
        """Increase retries and lower confidence threshold."""
        old_retries = self.strategy.params["retry_count"]
        old_threshold = self.strategy.params["confidence_threshold"]

        self.strategy.params["retry_count"] = min(5, old_retries + 1)
        self.strategy.params["confidence_threshold"] = max(0.3, old_threshold - 0.1)

        msg = (f"Low success rate ({self.monitor.success_rate:.0%}): "
               f"retries {old_retries}->{self.strategy.params['retry_count']}, "
               f"threshold {old_threshold:.1f}->{self.strategy.params['confidence_threshold']:.1f}")
        print(f"    [CORRECT] {msg}")
        return msg

    def _correct_high_latency(self) -> str:
        """Reduce batch size to lower processing time."""
        old_batch = self.strategy.params["batch_size"]
        self.strategy.params["batch_size"] = max(1, old_batch - 2)

        msg = f"High latency ({self.monitor.avg_latency:.2f}s): batch {old_batch}->{self.strategy.params['batch_size']}"
        print(f"    [CORRECT] {msg}")
        return msg

    def _correct_repeated_error(self, error_type: str) -> str:
        """Apply targeted fix for specific error patterns."""
        fixes = {
            "timeout_error": lambda: self.strategy.params.update({"timeout": min(30, self.strategy.params["timeout"] * 1.5)}),
            "validation_error": lambda: self.strategy.params.update({"confidence_threshold": min(0.9, self.strategy.params["confidence_threshold"] + 0.1)}),
            "resource_error": lambda: self.strategy.params.update({"batch_size": max(1, self.strategy.params["batch_size"] // 2)}),
            "data_error": lambda: self.strategy.params.update({"retry_count": min(5, self.strategy.params["retry_count"] + 1)}),
        }
        if error_type in fixes:
            fixes[error_type]()
            msg = f"Repeated '{error_type}': adjusted {self.strategy}"
            print(f"    [CORRECT] {msg}")
            return msg
        return ""

    def report(self):
        """Print performance summary."""
        print(f"\n{'='*60}")
        print(f"  Agent '{self.name}' Performance Report")
        print(f"{'='*60}")
        print(f"  Total tasks:       {self.total_tasks}")
        print(f"  Success rate:      {self.monitor.success_rate:.0%}")
        print(f"  Avg latency:       {self.monitor.avg_latency:.3f}s")
        print(f"  Total corrections: {self.total_corrections}")
        print(f"  Final strategy:    {self.strategy}")
        if self.correction_log:
            print(f"\n  Correction History:")
            for i, c in enumerate(self.correction_log[-5:], 1):
                print(f"    {i}. {c}")


if __name__ == "__main__":
    print("=== Self-Correcting Agent Demo ===")

    agent = SelfCorrectingAgent("AdaptiveBot")

    # Phase 1: Easy tasks
    print("\n--- Phase 1: Easy Tasks ---")
    for i in range(10):
        result = agent.execute_task({"name": f"easy_{i}", "difficulty": 0.3})
        status = "OK" if result["success"] else f"FAIL ({result['error']})"
        print(f"  Task {i}: {status}")

    # Phase 2: Hard tasks (agent should adapt)
    print("\n--- Phase 2: Hard Tasks (agent adapts) ---")
    for i in range(15):
        result = agent.execute_task({"name": f"hard_{i}", "difficulty": 0.8})
        status = "OK" if result["success"] else f"FAIL ({result['error']})"
        correction = result.get("correction_applied", "")
        suffix = f" -> {correction}" if correction else ""
        print(f"  Task {i}: {status}{suffix}")

    # Phase 3: Mixed tasks
    print("\n--- Phase 3: Mixed Tasks ---")
    for i in range(10):
        difficulty = random.choice([0.2, 0.5, 0.9])
        result = agent.execute_task({"name": f"mixed_{i}", "difficulty": difficulty})
        status = "OK" if result["success"] else f"FAIL ({result['error']})"
        print(f"  Task {i} (d={difficulty}): {status}")

    agent.report()
