"""MCP Server for Scenario Learner Bot.

Provides tools for scenario generation, branching logic,
and learner persona simulation via stdio transport.
"""

import json
import random
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("scenario-learner-tools")


# ── Tool 1: Generate scenario seed ──────────────────────────────────────────

@mcp.tool()
def generate_scenario_seed(
    topic: str,
    difficulty: str = "intermediate",
    domain: str = "corporate",
) -> str:
    """Create an initial scenario seed with context, characters, and a dilemma.

    Args:
        topic: The training topic (e.g. 'conflict resolution', 'customer complaint').
        difficulty: beginner | intermediate | advanced.
        domain: corporate | academic | healthcare | retail.

    Returns:
        JSON string with scenario_id, setting, characters[], and opening_situation.
    """
    scenario_id = f"SCN-{random.randint(1000, 9999)}"
    templates = {
        "corporate": {
            "setting": f"A busy open-plan office during Q4 deadline week",
            "characters": [
                {"name": "Alex", "role": "Team Lead", "personality": "direct, impatient"},
                {"name": "Jordan", "role": "New Hire", "personality": "eager, uncertain"},
            ],
        },
        "academic": {
            "setting": "A university lecture hall after a graded group presentation",
            "characters": [
                {"name": "Prof. Chen", "role": "Instructor", "personality": "fair, structured"},
                {"name": "Sam", "role": "Student", "personality": "anxious, hard-working"},
            ],
        },
        "healthcare": {
            "setting": "A hospital ward during shift handover",
            "characters": [
                {"name": "Dr. Patel", "role": "Attending Physician", "personality": "calm, thorough"},
                {"name": "Nurse Kim", "role": "Charge Nurse", "personality": "efficient, protective"},
            ],
        },
        "retail": {
            "setting": "A flagship store on Black Friday morning",
            "characters": [
                {"name": "Morgan", "role": "Store Manager", "personality": "upbeat, stretched thin"},
                {"name": "Casey", "role": "Customer", "personality": "frustrated, vocal"},
            ],
        },
    }
    base = templates.get(domain, templates["corporate"])
    return json.dumps({
        "scenario_id": scenario_id,
        "topic": topic,
        "difficulty": difficulty,
        "domain": domain,
        "setting": base["setting"],
        "characters": base["characters"],
        "opening_situation": (
            f"A situation about '{topic}' has arisen. "
            f"The learner must navigate this {difficulty}-level challenge."
        ),
    }, indent=2)


# ── Tool 2: Build branching dialogue tree ───────────────────────────────────

@mcp.tool()
def build_branching_tree(
    scenario_id: str,
    decision_point: str,
    num_branches: int = 3,
) -> str:
    """Generate a branching dialogue tree from a decision point.

    Args:
        scenario_id: The ID of the parent scenario.
        decision_point: Description of the choice the learner faces.
        num_branches: Number of response options to generate (2-4).

    Returns:
        JSON with the decision_point, branches[] each containing
        option_label, dialogue_snippet, consequence_hint, and score_delta.
    """
    num_branches = max(2, min(num_branches, 4))
    quality_labels = ["optimal", "acceptable", "poor", "risky"]
    branches = []
    for i in range(num_branches):
        quality = quality_labels[i % len(quality_labels)]
        score = {"optimal": 10, "acceptable": 5, "poor": -5, "risky": -10}[quality]
        branches.append({
            "branch_id": f"{scenario_id}-B{i + 1}",
            "option_label": f"Option {i + 1} ({quality})",
            "dialogue_snippet": f"[Placeholder dialogue for {quality} response to: {decision_point}]",
            "consequence_hint": f"This {quality} choice leads to a {'positive' if score > 0 else 'negative'} outcome.",
            "score_delta": score,
            "quality": quality,
        })
    return json.dumps({
        "scenario_id": scenario_id,
        "decision_point": decision_point,
        "branches": branches,
    }, indent=2)


# ── Tool 3: Simulate learner persona ────────────────────────────────────────

@mcp.tool()
def simulate_learner_persona(
    experience_level: str = "novice",
    learning_style: str = "visual",
) -> str:
    """Generate a realistic learner persona for scenario testing.

    Args:
        experience_level: novice | intermediate | expert.
        learning_style: visual | auditory | reading | kinesthetic.

    Returns:
        JSON with persona name, background, likely_mistakes[], and preferred_feedback_style.
    """
    personas = {
        "novice": {
            "name": "Taylor (Novice Learner)",
            "background": "Recently hired, 0-6 months in role. Unfamiliar with company norms.",
            "likely_mistakes": [
                "Avoids confrontation entirely",
                "Over-escalates to management",
                "Misreads social cues in the scenario",
            ],
            "preferred_feedback_style": "encouraging, step-by-step explanations",
        },
        "intermediate": {
            "name": "Riley (Mid-Level Learner)",
            "background": "1-3 years experience. Knows basics but struggles with nuance.",
            "likely_mistakes": [
                "Applies a one-size-fits-all approach",
                "Misses subtle power dynamics",
            ],
            "preferred_feedback_style": "comparative (show why one option is better than another)",
        },
        "expert": {
            "name": "Drew (Expert Learner)",
            "background": "5+ years experience. Looking for edge cases and advanced strategy.",
            "likely_mistakes": [
                "Over-complicates simple situations",
                "Assumes too much context",
            ],
            "preferred_feedback_style": "concise, data-driven, challenge-oriented",
        },
    }
    persona = personas.get(experience_level, personas["novice"])
    persona["learning_style"] = learning_style
    return json.dumps(persona, indent=2)


# ── Tool 4: Score learner path ──────────────────────────────────────────────

@mcp.tool()
def score_learner_path(
    scenario_id: str,
    chosen_branches: list[str],
) -> str:
    """Calculate a score and feedback summary for the branches a learner chose.

    Args:
        scenario_id: The scenario that was played.
        chosen_branches: List of branch_ids the learner selected in order.

    Returns:
        JSON with total_score, max_possible, percentage, rating, and per-choice feedback.
    """
    per_choice = []
    total = 0
    for i, branch_id in enumerate(chosen_branches):
        # Simulate scoring based on branch suffix
        if "B1" in branch_id:
            delta, note = 10, "Excellent choice — empathetic and effective."
        elif "B2" in branch_id:
            delta, note = 5, "Acceptable — gets the job done but misses nuance."
        elif "B3" in branch_id:
            delta, note = -5, "Poor choice — may escalate the situation."
        else:
            delta, note = -10, "Risky — could cause significant harm."
        total += delta
        per_choice.append({
            "step": i + 1,
            "branch_id": branch_id,
            "score_delta": delta,
            "feedback": note,
        })
    max_possible = len(chosen_branches) * 10
    pct = round((total / max_possible) * 100, 1) if max_possible else 0
    if pct >= 80:
        rating = "Mastery"
    elif pct >= 50:
        rating = "Proficient"
    elif pct >= 0:
        rating = "Developing"
    else:
        rating = "Needs Improvement"
    return json.dumps({
        "scenario_id": scenario_id,
        "total_score": total,
        "max_possible": max_possible,
        "percentage": pct,
        "rating": rating,
        "per_choice_feedback": per_choice,
    }, indent=2)


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
