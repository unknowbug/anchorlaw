"""
anchorlaw — Anchorlaw Protocol full implementation (Level 2-4)

"Any claim must have a verifiable practice anchor."
"Only offense, no defense. The only allowed defense is honest ignorance."

anchorlaw is not a test framework. It is an anchoring system that elevates
tests from "optional add-ons" to "part of the type declaration."

Maturity:
  Scanner: VERIFIED (via anchorlaw-scanner dependency)
  Anchors: EXPERIMENTAL — API stable, efficacy data pending
  Noise Cards: UNVERIFIED — schema defined, no project has accumulated significant data
  AI Context: CONJECTURE — format defined, no A/B test conducted
"""

__version__ = "0.1.0"

from anchorlaw.anchors import (
    test,
    i_dont_know,
    get_anchors,
    get_all_anchored_functions,
    run_tests,
    check_module,
    health_report,
    AnchorRegistry,
    TestAnchor,
    IDontKnowAnchor,
    FunctionAnchors,
    TestResult,
)
from anchorlaw_scanner.scanner import (
    scan_file,
    scan_directory,
    summarize,
    register_anchored_function,
    DefensivePattern,
    PatternType,
)
from anchorlaw.noise import (
    NoiseCard,
    NoiseStore,
    create_noise_card,
    list_unresolved,
    list_all as list_all_noise,
    resolve_noise,
    search_noise,
    find_by_function,
    export_for_ai,
    export_curriculum,
    export_summary as noise_summary,
)

__all__ = [
    # anchors
    "test", "i_dont_know", "get_anchors", "get_all_anchored_functions",
    "run_tests", "check_module", "health_report",
    "AnchorRegistry", "TestAnchor", "IDontKnowAnchor",
    "FunctionAnchors", "TestResult",
    # scanner (re-exported from anchorlaw-scanner)
    "scan_file", "scan_directory", "summarize", "register_anchored_function",
    "DefensivePattern", "PatternType",
    # noise
    "NoiseCard", "NoiseStore", "create_noise_card", "list_unresolved",
    "list_all_noise", "resolve_noise", "search_noise", "find_by_function",
    "export_for_ai", "export_curriculum", "noise_summary",
]
