# Lab 5: Static Code Analysis - Issues Found

File analysed: `premium_calculator.py`

Line numbers refer to the **original** file (see `reports/*_before.txt`).
Severity is shown in the Type column for security findings (Bandit's rating).

## Summary

| Tool | Before | After |
|------|--------|-------|
| Bandit | 10 issues (1 High, 5 Medium, 4 Low) | 0 issues (1 justified `# nosec B310`) |
| Flake8 | 19 findings (E302, E305, E501, E722) | 0 findings |
| Pylint | 5.73 / 10 | 9.78 / 10 |

## Issues fixed

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Unsafe `tarfile.extractall` (B202) | Security (High) | 64 | A customer-uploaded archive can contain paths like `../../x` and write files outside `claims_docs` (path traversal). | Extract with `filter="data"` and use `with tarfile.open(...)`. |
| XML parsed with `ElementTree` (B314, B405) | Security (Medium/Low) | 7, 48 | Partner XML is untrusted; the stdlib parser is vulnerable to entity-expansion attacks. | Use `defusedxml.ElementTree` instead. |
| Unverified SSL context (B323) | Security (Medium) | 58 | `ssl._create_unverified_context()` disables certificate checks, so rate tables could be tampered with by a man-in-the-middle. Also a protected-member access (Pylint W0212). | Removed the custom context so the default verified one is used. |
| `urlopen` accepts any scheme (B310) | Security (Medium) | 59 | `url` could be `file://` or a custom scheme. No timeout either. | Allow only `https`, raise `ValueError` otherwise, add `timeout=10`. `# nosec B310` documents that the scheme is checked first. |
| Server bound to all interfaces (B104) | Security (Medium) | 12 | `HOST = "0.0.0.0"` exposes the service on every network interface. | Bind to `127.0.0.1`. |
| Hardcoded `/tmp` log path (B108) | Security (Medium) | 14 | `/tmp` is world-writable and predictable. | Default to a local `premium_quotes.log`, overridable with the `PREMIUM_LOG_FILE` environment variable. |
| Hardcoded secret token (B105) | Security (Low) | 13, 73-77 | The underwriter token is in source code and git history. The `==` comparison is also not constant-time. | Read it from the `UNDERWRITER_TOKEN` environment variable; compare with `hmac.compare_digest`; reject if unset. |
| Weak random policy numbers (B311) | Security (Low) | 37 | `random.randint` is predictable, so policy numbers can be guessed. | Use `secrets.randbelow`. |
| Bare `except` that hides bad records (B112, E722, W0702) | Bug | 53 | Invalid policy records are silently dropped, and the bare `except` also catches things like `KeyboardInterrupt`. | Catch `(TypeError, ValueError)` and log a warning with the bad record. |
| Mutable default argument (W0102) | Bug | 17, 27 | `discounts=[]` is shared across calls and `discounts.append(500)` mutates it, so identical quotes returned 6000.0 then 5500.0 and a later quote lost an extra 1000. | Default to `None`, create a fresh list inside the function, remove the `append`. After the fix, Quote 2 equals Quote 1 and the non-smoker quote is 8970.0. |
| File opened without `with` or encoding (W1514, R1732) | Quality | 42-44 | The file is not closed if `write` raises, and the encoding is platform-dependent. | `with open(LOG_FILE, "a", encoding="utf-8")`. |
| `%` string formatting (C0209) | Style | 43 | Old-style formatting. | f-string. |
| `range(len(...))` loop (C0200) | Style | 85-87 | Indexing by position is clumsy. | `enumerate(quotes.items(), start=1)`. |
| Unnecessary `else` after `return` (R1705, R1703) | Style | 68-71, 74-77 | Extra nesting. | Return directly. |
| camelCase function names (C0103) | Style | 11 functions | Not PEP 8 snake_case. | Renamed (for example `calculatePremium` to `calculate_premium`) and updated all call sites. |
| Missing docstrings (C0114, C0116) | Style | module and 12 functions | No documentation of what each function does. | Added a docstring to the module and every function. |
| Demo ran on import | Quality | 107 | `main()` was called at module level. | Wrapped in `if __name__ == "__main__":`. |
| Missing blank lines (E302, E305) | Style (Flake8) | 17 to 107 | Fewer than 2 blank lines between top-level definitions. | Fixed with `autopep8 --select=E302,E305`. |
| Lines over 79 characters (E501) | Style (Flake8) | 14, 17, 52, 87, 101 | Long lines are hard to read and review. | Wrapped the signature, the `append` call, the `print` and split the long XML string. |

## Issues found but not fixed

These were found by running the program and reading its output. No tool flags
them, and they were outside the scope of the three tool-driven commits.

| Issue | Type | Line(s) | Description | Proposed fix |
|-------|------|---------|-------------|--------------|
| `smoker="no"` treated as a smoker | Bug | `main()` (p3), 21-23 | Any non-empty string is truthy, so `"no"` applies the 1.3x smoker loading. | Validate `smoker` as a bool, or parse the string explicitly. |
| Age ignores the birthday | Bug | 30-34 | Only subtracts the years, so 31-12-1990 gives 36 when the true age (on 28 Oct 2026) is 35. | Subtract 1 if `(today.month, today.day) < (born.month, born.day)`. |
| Premium can go negative | Bug | 28-30 | Stacked discounts of 9000 on a 8400 premium gave -800.0. | Floor the result at 0 (or cap discounts). |
| Instalments lose paise | Bug | 67-71 | `math.floor` means 12 instalments do not add up to the premium. | Round to 2 decimals and put the remainder in the last instalment. |
| Renewal crashes on 29 Feb | Bug | 79-81 | `date.replace(year=...)` raises `ValueError` for 29 Feb in a non-leap year. | Fall back to 28 Feb in that case. |
| Too many arguments (R0913, R0917) | Design | 22 | `calculate_premium` has 6 parameters (limit 5). | Group the inputs in a dataclass. Left as is to keep the public signature stable; costs about 0.2 points of the Pylint score. |