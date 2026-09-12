"""Property-based tests for the k6 compiler: every valid spec compiles soundly."""

from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st

from loadtest.generate import GENERATED_HEADER, compile_js, validate_structure
from loadtest.spec import LoadSpec

SPEC_PART: st.SearchStrategy[tuple[str, Any]] = st.one_of(
    st.integers(min_value=1, max_value=64).map(lambda v: ("vus", v)),
    st.integers(min_value=0, max_value=5).map(lambda v: ("ramp_up_s", v)),
    st.integers(min_value=0, max_value=10).map(lambda v: ("hold_s", v)),
    st.integers(min_value=0, max_value=5).map(lambda v: ("ramp_down_s", v)),
    st.integers(min_value=10, max_value=2000).map(lambda v: ("p95_ms", v)),
    st.floats(min_value=0.01, max_value=0.9, allow_nan=False).map(
        lambda v: ("error_rate", round(v, 3))
    ),
)


def valid_spec(parts: list[tuple[str, Any]]) -> LoadSpec:
    """Merge random parts onto the defaults, guaranteeing a legal spec."""
    kwargs: dict[str, Any] = vars(LoadSpec())
    for key, value in parts:
        kwargs[key] = value
    # A load test must actually apply load for a positive duration.
    if kwargs["ramp_up_s"] + kwargs["hold_s"] <= 0:
        kwargs["hold_s"] = 1
    return LoadSpec(**kwargs)


@settings(max_examples=60)
@given(parts=st.lists(SPEC_PART, min_size=1, max_size=4))
def test_valid_specs_always_compile_soundly(parts: list[tuple[str, Any]]) -> None:
    spec = valid_spec(parts)
    js = compile_js(spec)
    assert js.startswith(GENERATED_HEADER)
    assert validate_structure(js, spec) == []
    assert js.count("{") == js.count("}")
    assert js.count("(") == js.count(")")


@settings(max_examples=20)
@given(
    parts=st.lists(SPEC_PART, min_size=1, max_size=3),
    mutation=st.sampled_from(("strip_header", "strip_import", "strip_handler")),
)
def test_mutated_scripts_are_caught(parts: list[tuple[str, Any]], mutation: str) -> None:
    """Small mutations of the compiled output must be detectable."""
    spec = valid_spec(parts)
    js = compile_js(spec)
    if mutation == "strip_header":
        js = js.removeprefix(GENERATED_HEADER)
    elif mutation == "strip_import":
        js = js.replace("import http from 'k6/http';", "")
    else:
        js = js.replace("export default function", "function")
    problems = validate_structure(js, spec)
    assert problems, f"mutation {mutation} should be detected"
