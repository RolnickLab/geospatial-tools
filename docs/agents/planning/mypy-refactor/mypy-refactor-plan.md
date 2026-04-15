# 🎯 Objective & Context

The objective is to resolve 51 static type checking errors flagged by `mypy` across the `geospatial_tools` codebase. These errors primarily consist of implicit `Optional` types, incorrect path handling (mixing `str` and `pathlib.Path`), invariant list types (e.g., `list[Path]` instead of `Sequence[Path]`), and missing type annotations for dictionaries/lists. Addressing these issues will enforce strict typing, improving the reliability and maintainability of the project.

# 🏗️ Architectural Approach

The solution will strictly adhere to modern Python typing standards as outlined in the project's Python skill instructions:

- **Explicit Optionals:** Convert implicit `= None` defaults to explicit `T | None`.
- **Path Handling:** Ensure consistent use of `pathlib.Path` for all file system operations. Where functions accept both `str` and `Path`, standardize types or ensure safe casting.
- **Covariant Sequences:** Replace `list[T]` with `Sequence[T]` (from `typing` or `collections.abc`) in function arguments where variance causes type checking failures.
- **Precise Annotations:** Add exact type annotations for class attributes and local variables that Mypy cannot infer.

This approach aligns with the principle of "Easier To Change" by clearly documenting interfaces through types without altering runtime behavior.

# 🧪 Verification & Failure Modes

- **Verification:** The primary verification method is running `make mypy`. The task is complete when `make mypy` exits with code 0 (no errors found). Additionally, `make test`, `make precommit` and `make pylint` must pass to ensure type changes did not introduce runtime regressions.
- **Failure Modes:**
    - Overly broad type annotations (`Any`) masking true issues.
    - Incorrectly handling `None` checks, leading to runtime `AttributeError`s.
    - Breaking external scripts that depend on functions previously accepting less strict types. This will be mitigated by ensuring changes are backward-compatible (e.g., keeping union types where necessary).

# 📋 Implementation Steps

1. **Fix Implicit Optionals:** Update all function signatures across `raster.py`, `vector.py`, and `nimrod.py` to explicitly type parameters defaulting to `None` as `T | None`.
2. **Resolve Path vs String Mismatches:** Update variable types and division operators in `resample_tiff_raster.py`, `product_search.py`, `download_and_process.py`, and `planetary_computer/sentinel_2.py` to properly handle `pathlib.Path`.
3. **Fix Sequence and List Variance:** Update function arguments in `stac.py`, `utils.py`, and `planetary_computer/sentinel_2.py` to use `Sequence` instead of `list` where covariant types are expected.
4. **Add Missing Annotations and Fix Dictionary/List Initialization:** Add explicit types to class variables in `planetary_computer/sentinel_2.py` and local variables in `utils.py` and `raster.py`.
5. **Address Specific Edge Cases:** Fix the `logging_level` type assignment in `utils.py`, the `zip` argument in `raster.py`, the return statement in `planetary_computer/sentinel_2.py`, and the `sortby` parameter type in `stac.py`.
6. **Fix Missed Errors:** Address type and annotation issues in `download.py`, `vector.py` (lines 113, 141, 338), and `test_copernicus.py` (line 144) not covered by initial tasks.

# 🤝 Next Step

Do you approve Step 1 of the implementation plan to fix the implicit optionals?
