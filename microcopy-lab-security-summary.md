# Microcopy Lab security scan summary

Date: 2026-10-18. Scope: app.py, ui/, src/, scripts/, tests/, config, git history (1 commit, a83bf7b), requirements-verified.txt. Checklist source: security-tests.md.

## Tools run (throwaway venv outside the project, Python 3.13.16; project .venv and pyproject untouched)
| Tool | Version | Command scope |
|---|---|---|
| Bandit | 1.9.4 | app.py src ui scripts (2,996 LOC); tests/ run separately for information |
| Semgrep | 1.181.0 | rulesets p/python, p/security-audit, p/secrets; 238 rules, 81 git-tracked files |
| pip-audit | 2.10.1 | requirements-verified.txt (pinned, 68 packages) |
| Safety | 3.8.1 | `safety check -r requirements-verified.txt` (deprecated command; open-source DB) |
| gitleaks | 8.30.1 (preinstalled) | git history and working-tree (--no-git) scans |
| TruffleHog / git-secrets | not installed | gitleaks used as the secret scanner instead |
| Dependabot / Snyk | n/a | GitHub-side services; not runnable locally (see Owner items) |

## Findings
| Severity | Location | Tool | Status |
|---|---|---|---|
| None | app.py, src/, ui/, scripts/ | Bandit | 0 issues (0 low/medium/high) |
| None | all tracked files | Semgrep | 0 findings |
| None | requirements-verified.txt | pip-audit, Safety | No known vulnerabilities |
| None | git history | gitleaks | No leaks |
| Info (FP) | .venv/share/jupyter/nbextensions/pydeck/index.js.map | gitleaks working-tree scan | False positive, see below |
| Info (FP) | tests/ (363x B101 assert, B105, B404/B603) | Bandit on tests | False positives, see below |

## Streamlit-specific manual checks
- unsafe_allow_html: no occurrences in app.py, ui/, src/. Preview uses st.html with fixed templates and html.escape(text, quote=True) on the untrusted string (ui/preview_panel.py:55). Pass.
- Pickle / deserialization: no pickle, shelve, marshal, st.cache_data, or st.cache_resource used. YAML is read only via yaml.safe_load with size bounds. session_state holds only in-process app objects. Pass.
- Secrets: no st.secrets or env-var credential use; no hardcoded credentials; .env and .env.* are gitignored. Pass.
- Network/exec: no eval/exec/subprocess/os.system in app code. The only network code is the Ollama adapter (http.client), restricted to numeric loopback endpoints via ip_address(...).is_loopback in ai_config.py, no redirects, no proxies. Pass.
- Authentication: none. Documented in docs/security.md as a local-only prototype. Server binds to 127.0.0.1 (.streamlit/config.toml), telemetry off, upload cap 5 MB, error details hidden, default XSRF/CORS retained. Accepted risk while local only.

## Fixes made
None required. No source, dependency, or config files were changed.

## False positives / accepted risks
- gitleaks working-tree hits (2, same file): high-entropy source-map data in third-party pydeck inside the gitignored .venv. Not project content and not in git.
- Bandit on tests: B101 asserts are normal pytest usage; B105 is the deliberate fixture string "SECRET-SOURCE-CONTENT" in tests/test_foundation.py (a no-logging test); B404/B603 is a test-only subprocess call with a fixed argument list. tests/ is not shipped.
- No authentication: accepted for localhost use.

## Remaining / owner items
- Do not expose the app beyond 127.0.0.1 without an authenticating proxy (e.g. OAuth2-Proxy) or streamlit-authenticator.
- Consider enabling Dependabot and secret scanning on the GitHub repo once pushed (not testable locally). Optionally install TruffleHog for a second secret-scan opinion.
- requirements-verified.txt pins are exact but unhashed (pip-audit warning only); optional hardening.
- Semgrep with the registry rulesets needs network at run time; results reflect rules fetched on 2026-10-18.

## Test results
pytest (project .venv, Python 3.12.14): 283 passed in 12.44 s. No code changed, so no re-scan was needed beyond the initial run.

## Repo state
Pre-existing untracked security-tests.md left alone. New untracked file: this report. Nothing committed or pushed.
