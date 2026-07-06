# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit tests for the MCP server tools."""

import json

import pytest

from app.mcp_server import (
    build_branching_tree,
    generate_scenario_seed,
    score_learner_path,
    simulate_learner_persona,
)


class TestGenerateScenarioSeed:
    """Tests for generate_scenario_seed tool."""

    @pytest.mark.parametrize("domain", ["corporate", "academic", "healthcare", "retail"])
    @pytest.mark.parametrize("difficulty", ["beginner", "intermediate", "advanced"])
    def test_returns_valid_json(self, domain: str, difficulty: str) -> None:
        result = generate_scenario_seed(
            topic="conflict resolution",
            difficulty=difficulty,
            domain=domain,
        )
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_required_fields_present(self) -> None:
        result = generate_scenario_seed(
            topic="customer complaint handling",
            difficulty="intermediate",
            domain="corporate",
        )
        data = json.loads(result)

        assert "scenario_id" in data
        assert data["scenario_id"].startswith("SCN-")
        assert data["topic"] == "customer complaint handling"
        assert data["difficulty"] == "intermediate"
        assert data["domain"] == "corporate"
        assert "setting" in data
        assert "characters" in data
        assert "opening_situation" in data

    def test_characters_have_name_and_role(self) -> None:
        result = generate_scenario_seed(
            topic="ethical dilemma",
            difficulty="advanced",
            domain="healthcare",
        )
        data = json.loads(result)
        assert len(data["characters"]) >= 2
        for char in data["characters"]:
            assert "name" in char
            assert "role" in char
            assert "personality" in char

    def test_default_difficulty_is_intermediate(self) -> None:
        result = generate_scenario_seed(topic="feedback conversation")
        data = json.loads(result)
        assert data["difficulty"] == "intermediate"

    def test_default_domain_is_corporate(self) -> None:
        result = generate_scenario_seed(topic="team delegation")
        data = json.loads(result)
        assert data["domain"] == "corporate"


class TestBuildBranchingTree:
    """Tests for build_branching_tree tool."""

    def test_returns_valid_json(self) -> None:
        result = build_branching_tree(
            scenario_id="SCN-1234",
            decision_point="How should the manager respond to the angry customer?",
        )
        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["scenario_id"] == "SCN-1234"
        assert data["decision_point"] == "How should the manager respond to the angry customer?"

    def test_default_num_branches_is_three(self) -> None:
        result = build_branching_tree(
            scenario_id="SCN-9999",
            decision_point="Should Alex escalate or handle directly?",
        )
        data = json.loads(result)
        assert len(data["branches"]) == 3

    @pytest.mark.parametrize("num_branches", [2, 3, 4])
    def test_respects_num_branches_bounds(self, num_branches: int) -> None:
        result = build_branching_tree(
            scenario_id="SCN-0001",
            decision_point="Test decision",
            num_branches=num_branches,
        )
        data = json.loads(result)
        assert len(data["branches"]) == num_branches

    def test_num_branches_clamped_to_max_four(self) -> None:
        result = build_branching_tree(
            scenario_id="SCN-0002",
            decision_point="Test",
            num_branches=10,  # Should be clamped to 4
        )
        data = json.loads(result)
        assert len(data["branches"]) == 4

    def test_num_branches_clamped_to_min_two(self) -> None:
        result = build_branching_tree(
            scenario_id="SCN-0003",
            decision_point="Test",
            num_branches=0,  # Should be clamped to 2
        )
        data = json.loads(result)
        assert len(data["branches"]) == 2

    def test_branch_has_required_fields(self) -> None:
        result = build_branching_tree(
            scenario_id="SCN-0004",
            decision_point="Test decision",
            num_branches=3,
        )
        data = json.loads(result)
        for branch in data["branches"]:
            assert "branch_id" in branch
            assert "option_label" in branch
            assert "dialogue_snippet" in branch
            assert "consequence_hint" in branch
            assert "score_delta" in branch
            assert "quality" in branch

    def test_branch_ids_unique(self) -> None:
        result = build_branching_tree(
            scenario_id="SCN-0005",
            decision_point="Test",
            num_branches=4,
        )
        data = json.loads(result)
        branch_ids = [b["branch_id"] for b in data["branches"]]
        assert len(branch_ids) == len(set(branch_ids))

    def test_score_deltas_differ_by_quality(self) -> None:
        result = build_branching_tree(
            scenario_id="SCN-0006",
            decision_point="Test",
            num_branches=4,
        )
        data = json.loads(result)
        deltas = [b["score_delta"] for b in data["branches"]]
        # Optimal (10) > acceptable (5) > poor (-5) > risky (-10)
        assert deltas[0] > deltas[1]  # B1 > B2
        assert deltas[2] < 0  # B3 (poor) negative


class TestSimulateLearerPersona:
    """Tests for simulate_learner_persona tool."""

    @pytest.mark.parametrize("level", ["novice", "intermediate", "expert"])
    @pytest.mark.parametrize("style", ["visual", "auditory", "reading", "kinesthetic"])
    def test_returns_valid_json(self, level: str, style: str) -> None:
        result = simulate_learner_persona(
            experience_level=level,
            learning_style=style,
        )
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_required_fields_present(self) -> None:
        result = simulate_learner_persona(
            experience_level="novice",
            learning_style="visual",
        )
        data = json.loads(result)

        assert "name" in data
        assert "background" in data
        assert "likely_mistakes" in data
        assert "preferred_feedback_style" in data
        assert "learning_style" in data

    def test_novice_persona_more_mistakes(self) -> None:
        result = simulate_learner_persona(experience_level="novice")
        data = json.loads(result)
        # Novice has at least 3 likely mistakes
        assert len(data["likely_mistakes"]) >= 2

    def test_expert_persona_prefers_concise_feedback(self) -> None:
        result = simulate_learner_persona(experience_level="expert")
        data = json.loads(result)
        assert "concise" in data["preferred_feedback_style"].lower()

    def test_unrecognized_level_falls_back_to_novice(self) -> None:
        result = simulate_learner_persona(experience_level="superstar")
        data = json.loads(result)
        assert data["name"] == "Taylor (Novice Learner)"


class TestScoreLearerPath:
    """Tests for score_learner_path tool."""

    def test_returns_valid_json(self) -> None:
        result = score_learner_path(
            scenario_id="SCN-1234",
            chosen_branches=["SCN-1234-B1", "SCN-1234-B2", "SCN-1234-B1"],
        )
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_required_fields_present(self) -> None:
        result = score_learner_path(
            scenario_id="SCN-5678",
            chosen_branches=["SCN-5678-B1"],
        )
        data = json.loads(result)

        assert "scenario_id" in data
        assert "total_score" in data
        assert "max_possible" in data
        assert "percentage" in data
        assert "rating" in data
        assert "per_choice_feedback" in data

    def test_b1_optimal_gives_ten_points(self) -> None:
        result = score_learner_path(
            scenario_id="SCN-1000",
            chosen_branches=["SCN-1000-B1"],
        )
        data = json.loads(result)
        assert data["total_score"] == 10
        assert data["max_possible"] == 10
        assert data["percentage"] == 100.0
        assert data["rating"] == "Mastery"

    def test_b2_acceptable_gives_five_points(self) -> None:
        result = score_learner_path(
            scenario_id="SCN-1001",
            chosen_branches=["SCN-1001-B2"],
        )
        data = json.loads(result)
        assert data["total_score"] == 5

    def test_b3_poor_gives_negative_five(self) -> None:
        result = score_learner_path(
            scenario_id="SCN-1002",
            chosen_branches=["SCN-1002-B3"],
        )
        data = json.loads(result)
        assert data["total_score"] == -5

    def test_mixed_branches_accumulate_score(self) -> None:
        result = score_learner_path(
            scenario_id="SCN-2000",
            chosen_branches=[
                "SCN-2000-B1",  # +10
                "SCN-2000-B2",  # +5
                "SCN-2000-B3",  # -5
                "SCN-2000-B4",  # -10
            ],
        )
        data = json.loads(result)
        assert data["total_score"] == 0  # 10+5-5-10=0
        assert data["max_possible"] == 40
        assert data["percentage"] == 0.0

    def test_rating_thresholds(self) -> None:
        # Mastery: >= 80%
        result = score_learner_path(
            scenario_id="SCN-3000",
            chosen_branches=["SCN-3000-B1"] * 4,  # all optimal = 40/40 = 100%
        )
        assert json.loads(result)["rating"] == "Mastery"

        # Proficient: 50-79%
        result = score_learner_path(
            scenario_id="SCN-3001",
            chosen_branches=["SCN-3001-B2"] * 4,  # 20/40 = 50%
        )
        assert json.loads(result)["rating"] == "Proficient"

        # Developing: 0-49%
        result = score_learner_path(
            scenario_id="SCN-3002",
            chosen_branches=["SCN-3002-B2", "SCN-3002-B3"],  # 5-5=0/20=0%
        )
        assert json.loads(result)["rating"] == "Developing"

        # Needs Improvement: negative
        result = score_learner_path(
            scenario_id="SCN-3003",
            chosen_branches=["SCN-3003-B4"],  # -10/10 = -100%
        )
        assert json.loads(result)["rating"] == "Needs Improvement"

    def test_empty_branches_returns_zero(self) -> None:
        result = score_learner_path(
            scenario_id="SCN-9999",
            chosen_branches=[],
        )
        data = json.loads(result)
        assert data["total_score"] == 0
        assert data["max_possible"] == 0
        assert data["percentage"] == 0.0

    def test_per_choice_feedback_count_matches_branches(self) -> None:
        branches = ["SCN-A-B1", "SCN-A-B2", "SCN-A-B3"]
        result = score_learner_path(scenario_id="SCN-A", chosen_branches=branches)
        data = json.loads(result)
        assert len(data["per_choice_feedback"]) == 3

    def test_unknown_branch_defaults_to_risky(self) -> None:
        result = score_learner_path(
            scenario_id="SCN-BOGUS",
            chosen_branches=["SCN-BOGUS-B99"],  # Unknown branch → risky (-10)
        )
        data = json.loads(result)
        assert data["total_score"] == -10