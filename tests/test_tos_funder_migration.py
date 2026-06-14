from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_AGENTS = ROOT / "Reference" / "ai-hedge-fund" / "src" / "agents"
SKILL_ROOT = Path("/Users/mac/Projects/POS/00-System/Skills/skills-tos-funder")
MIGRATION_DOCS = ROOT / "docs" / "tos-funder"
COMMANDS = SKILL_ROOT / "tos-funder" / "commands"
REFERENCES = SKILL_ROOT / "tos-funder" / "references"
EXECUTION_BINDING = MIGRATION_DOCS / "18-hoxit-execution-binding.md"


AGENT_COMMANDS = {
    "aswath_damodaran.py": "tos-funder-quant-valuation-damodaran.md",
    "ben_graham.py": "tos-funder-value-graham.md",
    "bill_ackman.py": "tos-funder-tactical-ackman.md",
    "cathie_wood.py": "tos-funder-growth-cathie-wood.md",
    "charlie_munger.py": "tos-funder-value-munger.md",
    "fundamentals.py": "tos-funder-quant-fundamentals.md",
    "growth_agent.py": "tos-funder-growth.md",
    "michael_burry.py": "tos-funder-value-burry.md",
    "mohnish_pabrai.py": "tos-funder-value-pabrai.md",
    "nassim_taleb.py": "tos-funder-tactical-taleb.md",
    "news_sentiment.py": "tos-funder-news-sentiment.md",
    "peter_lynch.py": "tos-funder-growth-lynch.md",
    "phil_fisher.py": "tos-funder-growth-fisher.md",
    "portfolio_manager.py": "tos-funder-portfolio.md",
    "rakesh_jhunjhunwala.py": "tos-funder-macro-jhunjhunwala.md",
    "risk_manager.py": "tos-funder-risk-manager.md",
    "sentiment.py": "tos-funder-quant-sentiment.md",
    "stanley_druckenmiller.py": "tos-funder-macro-druckenmiller.md",
    "technicals.py": "tos-funder-quant-technicals.md",
    "valuation.py": "tos-funder-quant-valuation.md",
    "warren_buffett.py": "tos-funder-value-buffett.md",
}


CORE_COMMANDS = {
    "tos-funder-analyze.md",
    "tos-funder-preflight.md",
    "tos-funder-stock-research.md",
    "tos-funder-quant-price-series.md",
    "tos-funder-tactical-catalyst.md",
    "tos-funder-tactical-tail-risk.md",
    "tos-funder-tactical.md",
    "tos-funder-macro-topdown.md",
}


REQUIRED_REFERENCES = {
    "agent-taxonomy.md",
    "value-investors.md",
    "growth-investors.md",
    "valuation-models.md",
    "tactical-personas.md",
    "sentiment-event-proxy.md",
    "portfolio-synthesis.md",
}


METHODOLOGY_KEYWORDS = {
    "tos-funder-value-munger.md": [
        "moat",
        "management",
        "predictability",
        "valuation",
        "0.35",
        "0.25",
    ],
    "tos-funder-value-burry.md": [
        "FCF yield",
        "EV/EBIT",
        "balance-sheet",
        "insider",
        "contrarian",
    ],
    "tos-funder-value-pabrai.md": [
        "downside protection",
        "FCF yield",
        "double",
        "0.45",
        "0.35",
        "0.20",
    ],
    "tos-funder-growth-cathie-wood.md": [
        "disruptive",
        "R&D",
        "accelerating growth",
        "operating leverage",
        "high-growth scenario",
    ],
    "tos-funder-quant-valuation-damodaran.md": [
        "CAPM",
        "FCFF",
        "DCF",
        "reinvestment",
        "relative valuation",
        "margin_of_safety",
    ],
    "tos-funder-quant-valuation.md": [
        "owner earnings",
        "DCF",
        "EV/EBITDA",
        "residual income",
        "scenario",
    ],
    "tos-funder-tactical-ackman.md": [
        "business quality",
        "financial discipline",
        "activism potential",
        "intrinsic value",
    ],
    "tos-funder-tactical-taleb.md": [
        "fragility",
        "barbell",
        "convexity",
        "tail-risk",
        "via negativa",
    ],
    "tos-funder-macro-druckenmiller.md": [
        "growth and momentum",
        "insider",
        "sentiment",
        "risk-reward",
        "position sizing",
    ],
    "tos-funder-macro-jhunjhunwala.md": [
        "growth",
        "profitability",
        "balance sheet",
        "cash flow",
        "management actions",
        "30%",
    ],
    "tos-funder-news-sentiment.md": [
        "bullish_articles",
        "bearish_articles",
        "neutral_articles",
        "70%",
        "30%",
    ],
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_all_reference_agents_are_mapped():
    source_agents = {
        path.name
        for path in REFERENCE_AGENTS.glob("*.py")
        if path.name != "__init__.py"
    }
    assert source_agents == set(AGENT_COMMANDS)


def test_all_mapped_agent_commands_exist():
    missing = [
        command
        for command in AGENT_COMMANDS.values()
        if not (COMMANDS / command).exists()
    ]
    assert missing == []


def test_agent_commands_are_structured_for_downstream_consumption():
    required_fragments = [
        "consumed_schema:",
        "produced_schema:",
        "## Data Collection",
        "## Scoring",
        "## Output",
        "data_quality_warnings",
        "action_constraints",
    ]
    failures = {}
    for command in AGENT_COMMANDS.values():
        text = read(COMMANDS / command)
        missing = [fragment for fragment in required_fragments if fragment not in text]
        if missing:
            failures[command] = missing
    assert failures == {}


def test_skill_routing_lists_all_agent_commands():
    skill = read(SKILL_ROOT / "tos-funder" / "SKILL.md")
    readme = read(SKILL_ROOT / "README.md")
    failures = {}
    for command in AGENT_COMMANDS.values():
        command_name = command.removesuffix(".md")
        token = f"/{command_name}"
        missing = []
        if token not in skill:
            missing.append("SKILL.md")
        if token not in readme:
            missing.append("README.md")
        if missing:
            failures[token] = missing
    assert failures == {}


def test_required_strategy_references_exist():
    missing = [
        reference
        for reference in sorted(REQUIRED_REFERENCES)
        if not (REFERENCES / reference).exists()
    ]
    assert missing == []


def test_status_board_marks_all_agent_commands_covered_or_proxy():
    board = read(MIGRATION_DOCS / "16-migration-status-board.md")
    failures = {}
    for command in AGENT_COMMANDS.values():
        command_name = command.removesuffix(".md")
        token = f"/{command_name}"
        line = next((line for line in board.splitlines() if token in line), "")
        if not line:
            failures[token] = "missing from status board"
        elif "| covered |" not in line and "| proxy |" not in line:
            failures[token] = line
    assert failures == {}


def test_new_commands_preserve_source_agent_methodology():
    failures = {}
    for command, keywords in METHODOLOGY_KEYWORDS.items():
        text = read(COMMANDS / command)
        missing = [keyword for keyword in keywords if keyword not in text]
        if missing:
            failures[command] = missing
    assert failures == {}


def _hoxit_cli_routes() -> set[str]:
    from hoxit.cli import build_parser

    parser = build_parser()
    routes = set()
    layer_subparsers = next(
        action
        for action in parser._actions
        if getattr(action, "dest", None) == "layer"
    )
    for layer, layer_parser in layer_subparsers.choices.items():
        action_subparsers = next(
            (
                action
                for action in layer_parser._actions
                if getattr(action, "choices", None)
            ),
            None,
        )
        if action_subparsers is None:
            continue
        for action in action_subparsers.choices:
            routes.add(f"hoxit {layer} {action}")
    return routes


def test_execution_binding_lists_every_pos_command():
    binding = read(EXECUTION_BINDING)
    expected = {
        path.name.removesuffix(".md")
        for path in COMMANDS.glob("tos-funder-*.md")
    }
    expected.update(command.removesuffix(".md") for command in AGENT_COMMANDS.values())
    expected.update(command.removesuffix(".md") for command in CORE_COMMANDS)

    missing = [
        f"/{command}"
        for command in sorted(expected)
        if f"/{command}" not in binding
    ]
    assert missing == []


def test_execution_binding_uses_existing_hoxit_routes():
    binding = read(EXECUTION_BINDING)
    valid_routes = _hoxit_cli_routes()
    valid_routes.update({"hoxit iwc query", "hoxit iwc search"})

    referenced = {
        token
        for line in binding.splitlines()
        for token in valid_routes
        if token in line
    }
    assert referenced

    unknown = []
    for line in binding.splitlines():
        if not line.startswith("| /tos-funder-"):
            continue
        route_cell = line.split("|")[3]
        for fragment in route_cell.split(","):
            route = fragment.strip().strip("`")
            if route and route not in valid_routes:
                unknown.append(route)
    assert unknown == []


def test_execution_binding_has_no_false_complete_language():
    binding = read(EXECUTION_BINDING)
    status_board = read(MIGRATION_DOCS / "16-migration-status-board.md")

    assert "`covered` means POS skill parity, not standalone executable parity" in status_board
    assert "Do not mark a command as execution-complete" in binding


def test_stock_research_full_run_includes_expanded_migrated_layers():
    command = read(COMMANDS / "tos-funder-stock-research.md")
    required_fragments = [
        "CORE_SPINE",
        "EXPANDED_MIGRATED_LAYERS",
        "ALL_LAYERS = CORE_SPINE + EXPANDED_MIGRATED_LAYERS",
        "/tos-funder-value-munger",
        "/tos-funder-value-burry",
        "/tos-funder-value-pabrai",
        "/tos-funder-growth-cathie-wood",
        "/tos-funder-quant-valuation",
        "/tos-funder-quant-valuation-damodaran",
        "/tos-funder-tactical-ackman",
        "/tos-funder-tactical-taleb",
        "/tos-funder-macro-druckenmiller",
        "/tos-funder-macro-jhunjhunwala",
        "/tos-funder-news-sentiment",
        "### Completion Gate",
        "Expanded dimensions",
        "core_spine_only",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in command]
    assert missing == []
