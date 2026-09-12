"""Unit tests for the plain-English translator."""

from explain.translator import explain_all, explain_diff, explain_tool, extract_diff_stats

SAMPLE = """diff --git a/art/heart.py b/art/heart.py
--- a/art/heart.py
+++ b/art/heart.py
@@ -1 +1 @@
-    y = 1.0
+    y = 2.0
diff --git a/tests/unit/test_heart.py b/tests/unit/test_heart.py
new file mode 100644
--- /dev/null
+++ b/tests/unit/test_heart.py
@@ -0,0 +2 @@
+def test_a():
+    assert True
"""


def test_extract_stats() -> None:
    stats = extract_diff_stats(SAMPLE)
    assert stats.files == 2
    assert stats.added == 3
    assert stats.removed == 1
    assert stats.new_files == 1
    assert stats.touches_tests is True
    assert stats.non_python_files == 0


def test_explain_diff_bullets() -> None:
    bullets = explain_diff(SAMPLE)
    assert any("2 file" in b for b in bullets)
    assert any("test" in b.lower() for b in bullets)
    assert any("brand-new" in b for b in bullets)


def test_explain_diff_empty() -> None:
    bullets = explain_diff("")
    assert bullets
    assert "no files" in bullets[0]


def test_explain_tool_statuses() -> None:
    assert "passed" in explain_tool("ruff", "pass", "clean")
    assert "failed" in explain_tool("mypy", "fail", "3 errors")
    assert "not installed" in explain_tool("k6", "unavailable", "missing")
    assert "warning" in explain_tool("radon", "warn", "D:1")


def test_explain_all_zips_in_order() -> None:
    out = explain_all(("a", "b"), ("pass", "fail"), ("x", "y"))
    assert out[0].startswith("a")
    assert "failed" in out[1]
