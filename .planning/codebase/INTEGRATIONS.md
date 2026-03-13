# External Integrations

**Analysis Date:** 2026-03-13

## APIs & External Services

**GitHub API:**
- Service: GitHub REST API v2022-11-28
- What it's used for: Contributor data collection and ORCID lookups for citation file generation
  - SDK/Client: `urllib.request` (standard library)
  - Implementation: `scripts/update_citation_authors.py`
  - Auth: Optional `GITHUB_TOKEN` environment variable to avoid rate limiting
  - Endpoints:
    - `GET /orgs/{org}/repos` - List organization repositories
    - `GET /repos/{owner}/{repo}/contributors` - List repository contributors
    - `GET /users/{login}` - Get user information
    - `GET /users/{login}/social_accounts` - Get user social accounts (ORCID)

**RCSB PDB (Protein Data Bank):**
- Service: PDB HTTP API for structure data
- What it's used for: Downloading PDB structures for torch-fourier-slice testing
  - Implementation: `packages/primitives/torch-fourier-slice/tests/test_extract_central_slices_rfft_3d.py`
  - Client: `urllib3` (HTTP client library)
  - URL pattern: `https://files.rcsb.org/download/pdb_{pdb_id}.cif`
  - No authentication required, public data

**GitHub Web Scraping:**
- Service: GitHub user profiles (HTML)
- What it's used for: Extracting verified ORCID badges from GitHub profiles when not available via REST API
  - Implementation: `scripts/update_citation_authors.py` (line 71-82)
  - Client: `urllib.request` with custom User-Agent
  - Fallback method when `GET /users/{login}/social_accounts` lacks ORCID
  - Pattern extraction: `href="(https://orcid\.org/[\w-]+)"`

## Data Storage

**Databases:**
- None - This is a scientific computing library with no persistent storage requirements

**File Storage:**
- Local filesystem only
- Test data: Downloaded on-demand from RCSB PDB (not cached permanently)
- Package data: Distributed via PyPI wheels

**Caching:**
- None configured

## Authentication & Identity

**Auth Provider:**
- Custom approach - GitHub token for API rate limit avoidance
- Implementation: Scripts accept `GITHUB_TOKEN` environment variable
- Fallback: Unauthenticated requests allowed (lower rate limits)

**ORCID Integration:**
- Not a direct auth provider; used for research metadata
- Two methods:
  1. GitHub API social_accounts endpoint (REST)
  2. GitHub profile web scraping (fallback)
- Format: Full ORCID URL (`https://orcid.org/{orcid-id}`)

## Monitoring & Observability

**Error Tracking:**
- None configured - Projects handle errors locally during CI/CD

**Logs:**
- Pre-commit CI: Automatic fixes and updates via pre-commit.ci service
  - Config: `.pre-commit-config.yaml` lines 4-11
  - Autoupdate: Monthly
  - Auto-fixes enabled for ruff and pre-commit hooks

## CI/CD & Deployment

**Hosting:**
- GitHub (source repository)

**CI Pipeline:**
- GitHub Actions
  - File: `.github/workflows/ci.yml`
  - Triggers: Push to main, pull requests, weekly schedule
  - Matrix: Python 3.11, 3.12, 3.13 on ubuntu-latest
  - Steps:
    1. Checkout code
    2. Setup Python via actions/setup-python@v6
    3. Setup uv via astral-sh/setup-uv@v7 with caching
    4. Install dependencies: `uv sync --all-packages --group test`
    5. Run tests: `pytest --cov=packages/ --cov-report=xml`

**Deployment Pipeline:**
- GitHub Actions
  - File: `.github/workflows/deploy.yml`
  - Trigger: Git tags matching `*@v*` (excluding `teamtomo@v*`)
  - Steps:
    1. Verify tag is on main branch
    2. Verify CI passed for commit
    3. Extract package name from tag
    4. Install and test package
    5. Build package with `uv build`
    6. Publish to PyPI via `pypa/gh-action-pypi-publish@release/v1` (OIDC trusted publishing)
    7. Create GitHub Release with built artifacts

**Coordinated Release:**
- File: `.github/workflows/coordinated_release.yml`
- Triggered by tags matching `teamtomo@v*`
- Manages multi-package releases for the monorepo

**Dependency Updates:**
- Dependabot
  - File: `.github/dependabot.yml`
  - Package ecosystem: github-actions
  - Schedule: Weekly
  - Auto-fixes: Yes (via pre-commit.ci)
  - Commit prefix: `ci(dependabot):`

## Environment Configuration

**Required env vars:**
- `GITHUB_TOKEN` (optional) - GitHub API authentication for scripts
  - Used by: `scripts/update_citation_authors.py`
  - Purpose: Avoid rate limiting on GitHub API
  - Fallback: Script works without it (lower rate limits)

**Secrets location:**
- GitHub Actions secrets (not visible in repository)
- OIDC trusted publishing (no explicit secrets for PyPI)

## Webhooks & Callbacks

**Incoming:**
- GitHub webhooks for push, pull_request, schedule triggers
- Pre-commit CI: Automatic fix commits and autoupdate PRs

**Outgoing:**
- PyPI publishing (via GitHub Actions OIDC)
- GitHub Release creation
- No external webhook callbacks detected

## Pre-commit Service Integration

**Service:** pre-commit.ci

**Configuration:** `.pre-commit-config.yaml`

**Hooks managed:**
1. validate-pyproject - YAML/TOML validation
   - Applied to: Root and all package `pyproject.toml` files
2. typos - Spell checking
   - Runs with `--force-exclude` flag
3. ruff - Linting and formatting
   - Applied with `--fix` flag (may also use `--unsafe-fixes`)
4. mypy - Type checking
   - Runs on `src/**/*.py` and `packages/**/src/**/*.py`

**Auto-update Schedule:** Monthly
**Auto-fixes:** Enabled with commit message prefix `style(pre-commit.ci): auto fixes [...] `

---

*Integration audit: 2026-03-13*
