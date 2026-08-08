"""
噪声卡系统：运行时失败的结构化积累与 AI 上下文注入。

核心原则（来自待补充 260607）：
    "噪声即课题——每个解释不了的东西都是下一个课题的入口。"

这与传统测试框架的根本区别：
- 传统：测试失败 → 修 bug → 忘了
- anchorlaw：测试失败 → 创建噪声卡 → 积累为结构化知识 → 注入 AI 上下文

噪声卡不是 bug tracker。它是**认知边界的可操作记录**。
每张卡描述的不是"什么错了"，而是"我们在什么条件下发现了我们不知道什么"。
"""

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class NoiseCard:
    """一张噪声卡——一次结构化失败记录。

    这不是 bug report。这是"我们在这里发现了认知盲区"的实体化。
    """
    # 身份
    noise_id: str
    timestamp: str  # ISO 8601

    # 触发条件
    trigger: str          # 触发此噪声的具体操作
    function_name: str    # 涉及的函数
    anchor_violated: str  # 违反的锚点描述（如有）

    # 观察与期望的差距
    observed: str         # 实际发生了什么
    expected: str         # 期望发生什么

    # 认知收获（最关键的部分）
    discovery: str        # 这个噪声暴露了什么我们之前不知道的事？
    curriculum: str       # 可以提炼为 AI 上下文的教学要点

    # 转化
    converted_to_test: str = ""  # 为此噪声创建的回归测试（如有）
    resolved: bool = False
    resolved_at: str = ""

    # 元数据
    tags: List[str] = field(default_factory=list)
    context_snippet: str = ""  # 触发时的代码片段



    def mark_resolved(self, converted_test: str = ""):
        """标记此噪声已转化为已知知识。"""
        self.resolved = True
        self.resolved_at = datetime.now(timezone.utc).isoformat()
        if converted_test:
            self.converted_to_test = converted_test

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "NoiseCard":
        # Handle backward compatibility: older cards may lack converted_to_test
        defaults = {"converted_to_test": "", "resolved": False, "resolved_at": ""}
        for key, default_val in defaults.items():
            if key not in d:
                d[key] = default_val
        return cls(**d)

    @property
    def is_stale(self) -> bool:
        """如果超过 30 天未解决，可能该噪声已不是优先事项。"""
        if self.resolved:
            return False
        try:
            ts = datetime.fromisoformat(self.timestamp)
            delta = datetime.now(timezone.utc) - ts.replace(tzinfo=timezone.utc)
            return delta.days > 30
        except Exception:
            return False

    @property
    def ai_context_entry(self) -> str:
        """格式化为适合 AI 上下文注入的单条记录。"""
        status = "[RESOLVED]" if self.resolved else "[UNRESOLVED]"
        entry = (
            f"[{status}] Noise {self.noise_id[-8:]}\n"
            f"  Function: {self.function_name}\n"
            f"  Trigger: {self.trigger}\n"
            f"  Observed: {self.observed}\n"
            f"  Expected: {self.expected}\n"
            f"  Discovery: {self.discovery}\n"
            f"  Pattern: {self.curriculum}"
        )
        if self.converted_to_test:
            entry += f"\n  Regression test: {self.converted_to_test}"
        return entry


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

class NoiseStore:
    """噪声卡持久化存储。

    默认路径：.anchorlaw/noise_cards.json
    """

    def __init__(self, store_path: str = ".anchorlaw/noise_cards.json"):
        self._path = Path(store_path)
        self._cards: Dict[str, NoiseCard] = {}
        self._load()

    # ---- CRUD ----

    def add(self, card: NoiseCard) -> NoiseCard:
        self._cards[card.noise_id] = card
        self._save()
        return card

    def get(self, noise_id: str) -> Optional[NoiseCard]:
        return self._cards.get(noise_id)

    def resolve(self, noise_id: str, converted_test: str = "") -> bool:
        card = self._cards.get(noise_id)
        if card:
            card.mark_resolved(converted_test)
            self._save()
            return True
        return False

    def list_all(self) -> List[NoiseCard]:
        return sorted(
            self._cards.values(),
            key=lambda c: c.timestamp,
            reverse=True,
        )

    def list_unresolved(self) -> List[NoiseCard]:
        return [c for c in self._cards.values() if not c.resolved]

    def list_resolved(self) -> List[NoiseCard]:
        return [c for c in self._cards.values() if c.resolved]

    def search(self, keyword: str) -> List[NoiseCard]:
        kw = keyword.lower()
        results = []
        for card in self._cards.values():
            text = (
                f"{card.function_name} {card.trigger} "
                f"{card.observed} {card.discovery} {card.curriculum} "
                f"{' '.join(card.tags)}"
            ).lower()
            if kw in text:
                results.append(card)
        return sorted(results, key=lambda c: c.timestamp, reverse=True)

    def find_by_function(self, function_name: str) -> List[NoiseCard]:
        """查找与特定函数相关的所有噪声卡。

        用于：AI 生成该函数的新版本时，注入历史噪声上下文。
        """
        return [c for c in self._cards.values()
                if c.function_name == function_name]

    def count(self) -> int:
        return len(self._cards)

    def count_unresolved(self) -> int:
        return len(self.list_unresolved())

    # ---- I/O ----

    def _load(self):
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                for card_data in data.get("cards", []):
                    card = NoiseCard.from_dict(card_data)
                    self._cards[card.noise_id] = card
            except (json.JSONDecodeError, KeyError):
                # Corrupted file — start fresh but backup
                backup = self._path.with_suffix(".json.bak")
                self._path.rename(backup)
                self._cards = {}

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "updated": datetime.now(timezone.utc).isoformat(),
            "total": len(self._cards),
            "unresolved": self.count_unresolved(),
            "cards": [c.to_dict() for c in self.list_all()],
        }
        self._path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Global default store
# ---------------------------------------------------------------------------

_default_store: Optional[NoiseStore] = None


def _get_store() -> NoiseStore:
    global _default_store
    if _default_store is None:
        _default_store = NoiseStore()
    return _default_store


# ---------------------------------------------------------------------------
# Convenience API
# ---------------------------------------------------------------------------

def create_noise_card(
    trigger: str,
    function_name: str,
    observed: str,
    expected: str,
    discovery: str = "",
    curriculum: str = "",
    anchor_violated: str = "",
    tags: Optional[List[str]] = None,
    context_snippet: str = "",
) -> NoiseCard:
    """创建一张新的噪声卡并持久化。

    使用方法（在 except 块或测试失败处理中）：
        import anchorlaw
        try:
            result = my_function(bad_input)
        except Exception as e:
            anchorlaw.create_noise_card(
                trigger=f"my_function({bad_input!r})",
                function_name="my_function",
                observed=f"抛出 {type(e).__name__}: {e}",
                expected="应该返回默认值而非崩溃",
                discovery=f"函数未处理 {type(bad_input).__name__} 类型的输入",
                curriculum="在处理外部输入时，总是校验类型并处理不匹配的情况",
            )
            raise
    """
    card = NoiseCard(
        noise_id=f"noise-{uuid.uuid4().hex[:12]}",
        timestamp=datetime.now(timezone.utc).isoformat(),
        trigger=trigger,
        function_name=function_name,
        anchor_violated=anchor_violated,
        observed=observed,
        expected=expected,
        discovery=discovery or f"函数 {function_name} 在 {trigger} 条件下行为未定义",
        curriculum=curriculum or f"在类似场景下，确保处理 {trigger} 条件",
        tags=tags or [],
        context_snippet=context_snippet,
    )
    return _get_store().add(card)


def list_unresolved() -> List[NoiseCard]:
    """列出所有未解决的噪声卡。"""
    return _get_store().list_unresolved()


def list_all() -> List[NoiseCard]:
    """列出所有噪声卡。"""
    return _get_store().list_all()


def resolve_noise(noise_id: str, converted_test: str = "") -> bool:
    """标记噪声卡为已解决。"""
    return _get_store().resolve(noise_id, converted_test)


def find_by_function(function_name: str) -> List[NoiseCard]:
    """查找与特定函数相关的噪声卡。"""
    return _get_store().find_by_function(function_name)


def search_noise(keyword: str) -> List[NoiseCard]:
    """搜索噪声卡。"""
    return _get_store().search(keyword)


# ---------------------------------------------------------------------------
# AI context export
# ---------------------------------------------------------------------------

def export_for_ai(
    function_names: Optional[List[str]] = None,
    limit: int = 20,
    unresolved_only: bool = True,
) -> str:
    """导出噪声卡为 AI 上下文注入用的结构化文本。

    当 AI 需要生成或修改代码时，此输出应被注入到系统提示词中。

    Args:
        function_names: 仅导出这些函数相关的噪声卡。None = 全部。
        limit: 最多导出多少张卡
        unresolved_only: 是否仅导出未解决的噪声

    Returns:
        适合直接注入 AI 系统提示词的格式化文本。
    """
    store = _get_store()

    if unresolved_only:
        candidates = store.list_unresolved()
    else:
        candidates = store.list_all()

    # Filter by function names
    if function_names:
        name_set = set(function_names)
        candidates = [c for c in candidates if c.function_name in name_set]

    # Take most recent
    candidates = candidates[:limit]

    if not candidates:
        return "(No relevant noise cards)"

    resolved_count = sum(1 for c in candidates if c.resolved)
    unresolved_count = len(candidates) - resolved_count

    header = (
        f"# Historical Noise Cards (Practice Knowledge Base)\n"
        f"## Stats: {len(candidates)} cards ({unresolved_count} unresolved, {resolved_count} resolved)\n"
        f"## Note: These are cognitive boundaries discovered through past practice failures.\n"
        f"When generating code, actively avoid known problem patterns.\n\n"
    )

    entries = []
    for i, card in enumerate(candidates, 1):
        entries.append(f"### Noise #{i}\n{card.ai_context_entry}")

    return header + "\n---\n".join(entries)


def export_curriculum() -> str:
    """从所有已解决的噪声卡中提取'课程'摘要。

    这是从实践中提炼的、可注入 AI 系统提示的通用编码纪律。
    """
    store = _get_store()
    resolved = store.list_resolved()

    if not resolved:
        return "(No curriculum extracted yet)"

    curricula = []
    for card in resolved:
        if card.curriculum and card.curriculum not in curricula:
            curricula.append(card.curriculum)

    lines = ["# Coding Patterns Extracted from Practice Noise\n"]
    for i, c in enumerate(curricula, 1):
        lines.append(f"{i}. {c}")

    return "\n".join(lines)


def export_summary() -> Dict:
    """导出噪声卡系统的统计摘要。"""
    store = _get_store()
    all_cards = store.list_all()
    unresolved = store.list_unresolved()

    by_function: Dict[str, int] = {}
    by_tag: Dict[str, int] = {}

    for card in all_cards:
        by_function[card.function_name] = by_function.get(card.function_name, 0) + 1
        for tag in card.tags:
            by_tag[tag] = by_tag.get(tag, 0) + 1

    return {
        "total": len(all_cards),
        "unresolved": len(unresolved),
        "resolved": len(all_cards) - len(unresolved),
        "top_functions": sorted(by_function.items(), key=lambda x: -x[1])[:10],
        "top_tags": sorted(by_tag.items(), key=lambda x: -x[1])[:10],
    }
