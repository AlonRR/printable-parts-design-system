#!/usr/bin/env bash
# Hold .github/workflows/check.yml to the three bugs the convention kit's workflow showed on its
# first real run (5 Oct 2026), to this repo's own checks, and to actionlint.
#
#   bash tests/test-workflow.sh            # the real workflow: every check must pass
#
# Copied from repo-secret-scan tests/test-workflow.sh (its commit f190668) and pointed at this
# repo's workflow, 14 Oct 2026 (Skådis Air's A102). A workflow cannot be run here, so these are static checks;
# each names the bug it stops coming back:
#   1. the identity hook ran in CI, where it compares the RUNNER (no expected identity, so it
#      refused every run). It must be SKIPped there, and the recorded identity of the pushed
#      commits checked instead (.githooks/check-identity-range).
#   2. the secrets job downloaded releases/latest/download/..., which is a 404 - release assets
#      carry the version in their names. And `curl` without -f saved the 404 page.
#   3. pre-commit was installed with pip; the house rule is uv.
# and 4, this repo's: the tokens are rebuilt and must match, contrast, REUSE, the previews, the
# side-by-side sweep (D75) and the session hook's, the build's and the contrast check's tests run
# in CI; and 5, the previews run in Chromium, WebKit and Firefox, a job each with its own engine and
# screenshots (D40, 17 Oct 2026), the engine in PREVIEW_ENGINE and never in BROWSER, which many tools
# read as a web browser's command (D61); and 6, every job runs on ubuntu-24.04, never ubuntu-latest,
# which GitHub moves to a new image on its own date, and Linux's text widths once moved a measured
# breakpoint (D54's): a move is its own step, with the sweep run on it (D65); and 7, a job runs the fallback
# pass, in WebKit, where alone it measures the labels (D60).
#
# Copied into printable-parts-design-system from skadis-air (b55c32d), 15 Oct 2026 (D20); changed
# only in the workflow's name, in checks 4 to 7 and their controls, which are this repo's, and in
# leaving out skadis-air's checks of its Pages workflow: this repo publishes nothing.
#
# The controls: the same checks run against copies of the workflow, each with one of those
# bugs put back, and each copy must FAIL. A check that cannot fail is not a check.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REAL="$HERE/.github/workflows/check.yml"
BASE="$HERE/.pre-commit-config.yaml"

# The helpers below read the caller's `wf` and count into its `failed`.
check() { # check <label> <command...>
  label=$1
  shift
  if "$@" > /dev/null 2>&1; then
    printf '    ok    %s\n' "$label"
  else
    printf '    FAIL  %s\n' "$label"
    failed=$((failed + 1))
  fi
}
absent() { ! grep -qE "$1" "$wf"; }
present() { grep -qE "$1" "$wf"; }
# Outside comments: a comment may name what the workflow no longer does, and why.
code_absent() { ! grep -vE '^[[:space:]]*#' "$wf" | grep -qE "$1"; }

# checks <workflow> - prints one line per check, returns the number that failed
checks() {
  local wf=$1 failed=0 label
  # Command lines only: a comment explaining why -f matters mentions curl without it.
  curl_lines() { grep -vE '^[[:space:]]*#' "$wf" | grep -E '(^|[[:space:]])curl[[:space:]]'; }
  every_curl_fails() { curl_lines > /dev/null && ! curl_lines | grep -vqE 'curl[[:space:]]+-[a-zA-Z]*f'; }

  check "actionlint passes" uvx --from actionlint-py actionlint "$wf"
  check "1. the pre-commit job skips house-identity" present '^[[:space:]]+SKIP:.*house-identity'
  check "1. a job runs check-identity-range" present 'check-identity-range'
  check "1. the expected identity comes from repository variables" present 'vars\.EXPECT_EMAIL'
  check "1. ... both of them" present 'vars\.EXPECT_NAME'
  check "2. no releases/latest/download URL" absent 'releases/latest/download'
  check "2. every curl fails on an HTTP error (-f)" every_curl_fails
  check "2. the download is checked against checksums.txt" present 'sha256sum[[:space:]]+--check'
  local wf_v pc_v
  wf_v=$(sed -n 's/^[[:space:]]*BETTERLEAKS_VERSION:[[:space:]]*"\{0,1\}\([0-9.]*\)"\{0,1\}.*/\1/p' "$wf" | head -1)
  pc_v=$(grep -A1 'betterleaks/betterleaks' "$BASE" | sed -n 's/.*rev:[[:space:]]*v\{0,1\}\([0-9.]*\).*/\1/p' | head -1)
  check "2. CI's betterleaks ($wf_v) is the pre-commit hook's ($pc_v)" test -n "$wf_v" -a "$wf_v" = "$pc_v"
  check "3. no pip install" absent 'pip[[:space:]]+install'
  check "3. pre-commit runs through uvx, pinned" present 'uvx[[:space:]]+pre-commit@[0-9]'
  check "3. setup-uv is pinned to an exact release" present 'astral-sh/setup-uv@v[0-9]+\.[0-9]+\.[0-9]+'
  for script in build-tokens check-contrast; do
    check "4. it runs scripts/$script.py, locked" present "run:[[:space:]]+uv run --locked python scripts/$script\.py\$"
  done
  check "4. it runs scripts/check-previews.py, locked, in the job's engine" \
    present 'run:[[:space:]]+uv run --locked python scripts/check-previews\.py --browser "\$PREVIEW_ENGINE"$'
  check "4. tokens.css must not change" present 'run:[[:space:]]+git diff --exit-code tokens\.css$'
  check "4. every file has a licence (reuse lint)" present 'reuse lint$'
  check "4. the session hook's tests run" present 'bash tests/test-session-start\.sh$'
  check "4. the build's controls run" present 'bash tests/test-build-tokens\.sh$'
  check "4. the contrast check's controls run" present 'bash tests/test-check-contrast\.sh$'
  check "4. the preview check's controls run" present 'bash tests/test-check-previews\.sh$'
  check "4. it runs scripts/sweep-side-by-side.py, locked, in the job's engine" \
    present 'run:[[:space:]]+uv run --locked python scripts/sweep-side-by-side\.py --browser "\$PREVIEW_ENGINE"$'
  check "4. the sweep's controls run" present 'bash tests/test-sweep-side-by-side\.sh$'
  check "5. the previews run in chromium, webkit and firefox, a job each" present '^[[:space:]]+browser: \[chromium, webkit, firefox\]$'
  check "5. each job's engine is its matrix entry" present '^[[:space:]]+PREVIEW_ENGINE: \$\{\{ matrix\.browser \}\}$'
  check "5. each job installs its own engine, with its system packages" present 'playwright install --with-deps "\$PREVIEW_ENGINE"$'
  check "5. each engine keeps its own screenshots" present 'name: previews-\$\{\{ matrix\.browser \}\}$'
  check "5. nothing sets or reads BROWSER, a web browser's command to many tools (D61)" code_absent '(^|[^A-Za-z0-9_])BROWSER([^A-Za-z0-9_]|$)'
  # GitHub moves ubuntu-latest to a new image on its own date (D65)
  runners() { grep -E '^[[:space:]]*runs-on:' "$wf"; }
  every_runner_pinned() { runners > /dev/null && ! runners | grep -vqE '^[[:space:]]*runs-on:[[:space:]]+ubuntu-24\.04$'; }
  check "6. every job runs on ubuntu-24.04 (D65)" every_runner_pinned
  check "6. nothing names ubuntu-latest (D65)" code_absent 'ubuntu-latest'
  check "7. a job runs the fallback pass, locked, in WebKit (D60)" \
    present 'run:[[:space:]]+uv run --locked python scripts/check-previews\.py --fallbacks --browser webkit$'
  check "7. that job installs WebKit, with its system packages" present 'playwright install --with-deps webkit$'
  check "7. it keeps its own screenshots" present 'name: previews-fallbacks$'
  return "$failed"
}

echo "the workflow:"
out="$(checks "$REAL")"
printf '%s\n' "$out"
pass=$(grep -c '^    ok ' <<< "$out")
fail=$(grep -c '^    FAIL ' <<< "$out")
controls=0
refused=0

# The controls: one bug put back per copy; the checks must fail on each.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
control() { # control <label> <workflow> <checks function> <sed expression>
  local copy="$tmp/control.yml"
  sed -e "$4" "$2" > "$copy"
  controls=$((controls + 1))
  if cmp -s "$copy" "$2"; then
    printf '    FAIL  control "%s" changed nothing in the workflow\n' "$1"
  elif "$3" "$copy" > /dev/null; then
    printf '    FAIL  control "%s": the checks passed a broken workflow\n' "$1"
  else
    printf '    ok    control "%s": refused\n' "$1"
    refused=$((refused + 1))
  fi
}
echo "the controls, each a broken copy that must be refused:"
control "the identity hook not skipped" "$REAL" checks '/SKIP: house-identity/d'
control "an unversioned betterleaks download" "$REAL" checks 's|releases/download/v\${BETTERLEAKS_VERSION}|releases/latest/download|'
control "curl without -f" "$REAL" checks 's/curl -fsSLO/curl -sSLO/'
control "pre-commit through pip" "$REAL" checks 's|run: uvx pre-commit@4.6.2 run|run: pip install pre-commit \&\& pre-commit run|'
control "no preview check" "$REAL" checks '/run: uv run --locked python scripts\/check-previews.py/d'
control "no preview controls" "$REAL" checks '/bash tests\/test-check-previews.sh/d'
control "no side-by-side sweep" "$REAL" checks '/run: uv run --locked python scripts\/sweep-side-by-side.py/d'
control "no sweep controls" "$REAL" checks '/bash tests\/test-sweep-side-by-side.sh/d'
control "an engine dropped from the matrix" "$REAL" checks 's/browser: \[chromium, webkit, firefox\]/browser: [chromium, webkit]/'
control "the previews in Chromium whatever the job" "$REAL" checks 's/check-previews\.py --browser "\$PREVIEW_ENGINE"/check-previews.py/'
control "every job installing Chromium" "$REAL" checks 's/install --with-deps "\$PREVIEW_ENGINE"/install --with-deps chromium/'
control "one screenshot artifact for every engine" "$REAL" checks 's/name: previews-\${{ matrix\.browser }}/name: previews/'
control "BROWSER set beside PREVIEW_ENGINE again" "$REAL" checks 's/^\([[:space:]]*\)PREVIEW_ENGINE: \(.*\)$/&\n\1BROWSER: \2/'
control "one job back on ubuntu-latest" "$REAL" checks '0,/runs-on: ubuntu-24\.04/s//runs-on: ubuntu-latest/'
control "no fallback pass" "$REAL" checks '/check-previews\.py --fallbacks/d'
control "the fallback pass in Chromium" "$REAL" checks 's/--fallbacks --browser webkit/--fallbacks/'

printf '\n%s checks passed, %s failed; %s of %s controls refused\n' "$pass" "$fail" "$refused" "$controls"
[ "$fail" -eq 0 ] && [ "$pass" -gt 0 ] && [ "$refused" -eq "$controls" ]
