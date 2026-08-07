"""Anchorlaw noise cards 单元测试。

覆盖协议 v0.3 §3 Noise Card schema 的存储、解析、搜索、转化。
"""
from datetime import datetime, timedelta, timezone

import pytest

from anchorlaw.noise import (
    NoiseCard,
    NoiseStore,
    create_noise_card,
    find_by_function,
    list_unresolved,
    resolve_noise,
    search_noise,
)


def _card(nid="n1", **kw):
    defaults = dict(
        noise_id=nid,
        timestamp=datetime.now(timezone.utc).isoformat(),
        trigger="trigger",
        function_name="fn",
        anchor_violated="",
        observed="observed",
        expected="expected",
        discovery="discovery",
        curriculum="curriculum",
    )
    defaults.update(kw)
    return NoiseCard(**defaults)


class TestNoiseCard:
    def test_create_and_count(self, tmp_path):
        store = NoiseStore(str(tmp_path / "cards.json"))
        store.add(_card())
        assert store.count() == 1

    def test_persistence_roundtrip(self, tmp_path):
        path = str(tmp_path / "cards.json")
        store = NoiseStore(path)
        store.add(_card("n1", trigger="timeout"))
        store2 = NoiseStore(path)
        assert store2.count() == 1
        assert store2.get("n1").trigger == "timeout"

    def test_from_dict_backward_compat(self):
        d = {
            "noise_id": "n1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger": "t",
            "function_name": "f",
            "anchor_violated": "",
            "observed": "o",
            "expected": "e",
            "discovery": "d",
            "curriculum": "c",
        }
        card = NoiseCard.from_dict(dict(d))
        assert card.converted_to_test == ""
        assert card.resolved is False

    def test_resolve(self, tmp_path):
        store = NoiseStore(str(tmp_path / "cards.json"))
        store.add(_card("n1"))
        assert store.resolve("n1", converted_test="regression_x")
        assert store.get("n1").resolved
        assert store.get("n1").converted_to_test == "regression_x"
        assert not store.resolve("nope")

    def test_search(self, tmp_path):
        store = NoiseStore(str(tmp_path / "cards.json"))
        store.add(_card("n1", trigger="timeout"))
        store.add(_card("n2", trigger="crash"))
        hits = store.search("timeout")
        assert len(hits) == 1
        assert hits[0].noise_id == "n1"

    def test_find_by_function(self, tmp_path):
        store = NoiseStore(str(tmp_path / "cards.json"))
        store.add(_card("n1", function_name="parse_json"))
        store.add(_card("n2", function_name="render"))
        hits = store.find_by_function("parse_json")
        assert len(hits) == 1
        assert hits[0].function_name == "parse_json"

    def test_is_stale(self):
        old = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
        card = _card(timestamp=old)
        assert card.is_stale

    def test_not_stale_when_resolved(self):
        old = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
        card = _card(timestamp=old)
        card.mark_resolved()
        assert not card.is_stale

    def test_ai_context_entry(self):
        card = _card()
        entry = card.ai_context_entry
        assert "[UNRESOLVED]" in entry
        assert "fn" in entry
        card.mark_resolved("rt")
        assert "[RESOLVED]" in card.ai_context_entry
        assert "rt" in card.ai_context_entry


class TestModuleLevelAPI:
    def test_create_noise_card_module_api(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        card = create_noise_card(
            trigger="t",
            function_name="f",
            observed="o",
            expected="e",
        )
        assert card is not None
        assert len(list_unresolved()) >= 1

    def test_resolve_noise_module_api(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        create_noise_card(trigger="t", function_name="f", observed="o", expected="e")
        assert resolve_noise("missing-id") is False  # 未知 id 返回 False

    def test_search_module_api(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        create_noise_card(trigger="timeout", function_name="f", observed="o", expected="e")
        hits = search_noise("timeout")
        assert len(hits) == 1
        assert find_by_function("f")  # 按函数查得到
