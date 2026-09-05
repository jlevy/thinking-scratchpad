"""The schema validator was swapped for a faster one; this is why that is safe.

`devtools.validate_schemas` moved from `jsonschema` (pure Python) to `jsonschema_rs`
(PyO3 bindings to the Rust crate) for a 560x speedup over this corpus, measured in
`D-370` and reproducible through `benchmarks/bench_schema_validation.py`.

A faster validator that accepts one artifact the old one rejected is a soundness
regression that buys six seconds, and it would be invisible in the timings that
motivated the change. So the two run side by side here, over the real corpus and over
generated mutations of it, and every verdict must match.

**Verdict and location, not message text.** The two libraries word their errors
differently -- `jsonschema` quotes with `'` and `jsonschema_rs` with `"`, so
`'a' is a required property` becomes `"a" is a required property`. The spec that
proposed this swap claimed the messages were byte-identical; they are not, and the
difference is systematic rather than incidental. Nothing in this repository parses that
text, so the equivalence that matters is: same accept/reject decision, and the same set
of instance paths flagged. `normalise_message` states the quoting difference explicitly
instead of leaving it for a reader to rediscover.

**Mutations, because the corpus is valid.** 339 artifacts that all pass prove only that
neither validator crashes. What proves equivalence is disagreement-hunting on documents
built to fail: a dropped required key, a retyped value, an emptied array, an extra
property. Those exercise the keywords a real regression would hide in.
"""

from __future__ import annotations

import copy
import functools
import pathlib
import re
from typing import Any

import jsonschema_rs
import pytest
from jsonschema import Draft202012Validator as PyValidator

from devtools.validate_schemas import corpus_paths, payload_and_meta
from sqpack.yamlio import load_yaml

RsValidator = jsonschema_rs.Draft202012Validator


def normalise_message(message: str) -> str:
    """Strip the one systematic wording difference between the two libraries.

    `jsonschema` renders quoted values with `'`, `jsonschema_rs` with `"`. Everything
    else in the message body is compared as-is, so a genuine wording divergence still
    shows up as a difference rather than being normalised away.
    """
    return message.replace('"', "'")


@functools.cache
def _schema_path_for(path: pathlib.Path) -> pathlib.Path | None:
    _payload, meta = payload_and_meta(path)
    if not meta or meta.get("status") != "enforced":
        return None
    schema_path = (path.parent / meta["schema"]).resolve()
    return schema_path if schema_path.exists() else None


@functools.cache
def _schema(schema_path: pathlib.Path) -> dict[str, Any]:
    return load_yaml(schema_path.read_text(encoding="utf-8"))


@functools.cache
def _py(schema_path: pathlib.Path) -> PyValidator:
    """One compiled Python validator per schema.

    Compiling per assertion is what made a first version of this file take minutes: the
    pure-Python compile is the expensive half, and 23 schemas were being rebuilt once
    per mutation across 339 artifacts.
    """
    return PyValidator(_schema(schema_path))


@functools.cache
def _rs(schema_path: pathlib.Path) -> Any:
    return RsValidator(_schema(schema_path))


def _verdict(schema_path: pathlib.Path, payload: Any) -> tuple[bool, list[tuple[str, ...]]]:
    """(valid, sorted instance paths) under the Python validator."""
    errors = list(_py(schema_path).iter_errors(payload))
    return not errors, sorted(tuple(str(x) for x in e.path) for e in errors)


def _verdict_rs(schema_path: pathlib.Path, payload: Any) -> tuple[bool, list[tuple[str, ...]]]:
    """(valid, sorted instance paths) under the Rust validator."""
    errors = list(_rs(schema_path).iter_errors(payload))
    return not errors, sorted(tuple(str(x) for x in e.instance_path) for e in errors)


def _corpus() -> list[pathlib.Path]:
    md, datasets = corpus_paths()
    return md + datasets


def _mutations(payload: Any, schema: dict[str, Any]) -> list[tuple[str, Any]]:
    """Documents built to fail, one broken thing at a time.

    Each is named for what it breaks so a failing assertion says which keyword the two
    validators disagreed on rather than only that they did.
    """
    out: list[tuple[str, Any]] = []
    if not isinstance(payload, dict):
        return out

    for key in schema.get("required", []) or []:
        if key in payload:
            broken = copy.deepcopy(payload)
            del broken[key]
            out.append((f"drop-required:{key}", broken))

    for key, value in list(payload.items())[:6]:
        broken = copy.deepcopy(payload)
        # Retype to something no schema in this corpus accepts for every key.
        broken[key] = ["retyped"] if not isinstance(value, list) else "retyped"
        out.append((f"retype:{key}", broken))
        if isinstance(value, list) and value:
            emptied = copy.deepcopy(payload)
            emptied[key] = []
            out.append((f"empty-array:{key}", emptied))

    extra = copy.deepcopy(payload)
    extra["--unexpected-property--"] = 1
    out.append(("extra-property", extra))
    return out


@pytest.mark.parametrize("path", _corpus(), ids=lambda p: p.name)
def test_validators_agree_on_the_corpus(path: pathlib.Path) -> None:
    """Both validators reach the same verdict on every enforced artifact."""
    schema_path = _schema_path_for(path)
    if schema_path is None:
        pytest.skip(f"{path.name} declares no enforced schema")
    payload, _ = payload_and_meta(path)
    assert _verdict(schema_path, payload) == _verdict_rs(schema_path, payload), (
        f"{path.name}: validators disagree on the artifact as committed"
    )


@functools.cache
def _mutation_targets() -> tuple[pathlib.Path, ...]:
    """One artifact per distinct (schema, top-level shape), cheapest first.

    Mutating every artifact is redundant work, not extra coverage. These mutations break
    structure -- a dropped required key, a retyped value, an emptied array, an extra
    property -- so what they exercise is determined by the schema and by which top-level
    keys the document has. Two frontier cases declaring the same schema with the same key
    set produce the same mutation shapes and therefore reach the same keywords.

    The values those artifacts actually carry are not skipped: every one of them is
    validated under both libraries by `test_validators_agree_on_the_corpus`. What is
    deduplicated here is only the structural half.

    It matters because the corpus is lopsided. One pass under the pure-Python validator
    costs about seven seconds and a single 5 MB witness file is 825 ms of it, so mutating
    all 339 artifacts ten times over spent minutes re-proving the same handful of facts.
    Cheapest-first makes the representative of each shape the one that costs least.
    """
    by_shape: dict[tuple[pathlib.Path, tuple[str, ...]], pathlib.Path] = {}
    for path in _corpus():
        schema_path = _schema_path_for(path)
        if schema_path is None:
            continue
        payload, _meta = payload_and_meta(path)
        if not isinstance(payload, dict):
            continue
        shape = (schema_path, tuple(sorted(payload)))
        current = by_shape.get(shape)
        if current is None or path.stat().st_size < current.stat().st_size:
            by_shape[shape] = path
    return tuple(sorted(by_shape.values()))


def test_every_schema_reaches_the_mutation_test() -> None:
    """Deduplication must not drop a schema entirely.

    The shape key starts with the schema path, so every schema in the corpus keeps at
    least one representative. This asserts that rather than trusting it, because a future
    change to the key is exactly how a schema would silently stop being mutated.
    """
    covered = {_schema_path_for(p) for p in _mutation_targets()}
    declared = {_schema_path_for(p) for p in _corpus()} - {None}
    assert covered == declared, f"schemas with no mutation target: {declared - covered}"


@pytest.mark.slow
@pytest.mark.parametrize("path", _mutation_targets(), ids=lambda p: p.name)
def test_validators_agree_on_mutations(path: pathlib.Path) -> None:
    """Both validators reach the same verdict on documents built to fail.

    The corpus is valid, so agreement on it alone would prove only that neither
    validator crashes. This is the half that can catch a keyword one of them ignores.
    """
    schema_path = _schema_path_for(path)
    if schema_path is None:
        pytest.skip(f"{path.name} declares no enforced schema")
    payload, _ = payload_and_meta(path)
    mutations = _mutations(payload, _schema(schema_path))
    if not mutations:
        pytest.skip(f"{path.name} has no mutable surface")
    for name, broken in mutations:
        assert _verdict(schema_path, broken) == _verdict_rs(schema_path, broken), (
            f"{path.name}: validators disagree under mutation {name}"
        )


@pytest.mark.slow
def test_mutations_actually_break_something() -> None:
    """The mutation generator must produce rejections, or the test above proves nothing.

    A generator that quietly produced only valid documents would let both validators
    agree on everything while checking none of the keywords a regression would hide in.
    """
    rejected = 0
    total = 0
    for path in _mutation_targets():
        schema_path = _schema_path_for(path)
        if schema_path is None:
            continue
        payload, _ = payload_and_meta(path)
        for _name, broken in _mutations(payload, _schema(schema_path)):
            total += 1
            if not _verdict(schema_path, broken)[0]:
                rejected += 1
    assert total > 40, f"only {total} mutations generated; the corpus was not covered"
    assert rejected > total // 2, (
        f"only {rejected} of {total} mutations were rejected; the generator is too gentle"
    )


def test_the_quoting_difference_is_real_and_is_the_only_one() -> None:
    """Pin the message difference, so a future divergence is not mistaken for it.

    This asserts the difference exists. If a later release of either library makes the
    messages identical, this test fails and the docstring in `_validator` that explains
    the difference should be removed with it.
    """
    schema = {"type": "object", "required": ["a"]}
    py = [e.message for e in PyValidator(schema).iter_errors({})]
    rs = [e.message for e in RsValidator(schema).iter_errors({})]
    assert py == ["'a' is a required property"]
    assert rs == ['"a" is a required property']
    assert [normalise_message(m) for m in rs] == [normalise_message(m) for m in py]


def test_quoting_normalisation_does_not_hide_a_real_difference() -> None:
    """`normalise_message` must not be a blanket equaliser.

    It rewrites quote characters and nothing else, so two genuinely different messages
    stay different after it runs.
    """
    assert normalise_message('"a" is a required property') != normalise_message(
        "'b' is a required property"
    )
    assert re.search(r"required", normalise_message('"a" is a required property'))
