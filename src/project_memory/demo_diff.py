from src.project_memory.diff_engine import DiffEngine

engine = DiffEngine()

old = """
class Question:
    pass
"""

new = """
class Question:

    def summary(self):
        return "Hello"
"""

diff = engine.compare_text(
    old,
    new,
)

print("=" * 70)

print(diff)

print("=" * 70)