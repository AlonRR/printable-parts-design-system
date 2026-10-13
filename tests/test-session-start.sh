#!/usr/bin/env bash
# Positive and negative controls for .claude/hooks/session-start.sh, the hook that sets up
# a cloud session: the owner's identity, the git hooks, and optional commit signing.
#
#   bash tests/test-session-start.sh
#
# Runs the hook against a FRESH repository built from this repo's setup files, which is
# what a new cloud session starts from: no repo-local git config, so commits would get the
# platform's identity and no hooks would be wired. Works in a repo that adopted the starter
# and in the starter folder itself.
#
# Needs ssh-keygen (to make test signing keys), and uv when the repo has a
# .pre-commit-config.yaml (the hook installs pre-commit with it). Runs locally, not in CI.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$HERE/.claude/hooks/session-start.sh"
NAME=$(sed -n 's/^OWNER_NAME="\(.*\)"$/\1/p' "$HOOK")
EMAIL=$(sed -n 's/^OWNER_EMAIL="\(.*\)"$/\1/p' "$HOOK")
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
pass=0
fail=0

check() { # check <label> <command...>: the command must succeed
  local label=$1
  shift
  if "$@" > /dev/null 2>&1; then
    pass=$((pass + 1))
    printf '  ok    %s\n' "$label"
  else
    fail=$((fail + 1))
    printf '  FAIL  %s\n' "$label"
  fi
}
is() { [ "$1" = "$2" ]; }

HAS_PC=no
[ -f "$HERE/.pre-commit-config.yaml" ] && HAS_PC=yes
fresh() { # fresh <dir>: a new repo holding this repo's setup files, and no local config
  # --template= : no hooks from the machine's init.templateDir. A cloud clone has none, and a
  # template hook here would make "no hook wired" fail for a reason the cloud never has.
  git init -q --template= "$1"
  git -C "$1" config core.autocrlf false
  for f in .claude .pre-commit-config.yaml .githooks REUSE.toml; do
    [ -e "$HERE/$f" ] && cp -r "$HERE/$f" "$1/"
  done
  chmod +x "$1"/.claude/hooks/*.sh "$1"/.githooks/* 2> /dev/null || true
}
run_hook() { # run_hook <repo> <env file> [VAR=value ...]
  local repo=$1 envfile=$2
  shift 2
  (cd "$repo" && env -u CLAUDE_CODE_REMOTE -u GIT_SIGNING_KEY_B64 "$@" CLAUDE_PROJECT_DIR="$repo" \
    CLAUDE_ENV_FILE="$envfile" bash "$repo/.claude/hooks/session-start.sh")
}
export -f run_hook
cfg() { git -C "$1" config --local --get "$2"; }
unset_in() { ! git -C "$1" config --local --get "$2"; }

check "the identity was read from the hook ($NAME <$EMAIL>)" test -n "$NAME" -a -n "$EMAIL"

C="$TMP/clone"
fresh "$C"
echo "outside a cloud session -- must change nothing:"
run_hook "$C" "$TMP/env-local" > /dev/null 2>&1
check "exits 0" is "$?" 0
check "no repo-local user.email" unset_in "$C" user.email
check "no repo-local hooks.expectEmail" unset_in "$C" hooks.expectEmail
check "no commit-msg hook wired" test ! -e "$C/.git/hooks/commit-msg"
check "nothing written to the env file" test ! -s "$TMP/env-local"

echo "in a cloud session -- must set the session up:"
run_hook "$C" "$TMP/env-cloud" CLAUDE_CODE_REMOTE=true > "$TMP/cloud.log" 2>&1
check "exits 0" is "$?" 0
check "user.name is the owner's" is "$(cfg "$C" user.name)" "$NAME"
check "user.email is the owner's" is "$(cfg "$C" user.email)" "$EMAIL"
check "hooks.expectName set" is "$(cfg "$C" hooks.expectName)" "$NAME"
check "hooks.expectEmail set" is "$(cfg "$C" hooks.expectEmail)" "$EMAIL"
check "user.useConfigOnly set" is "$(cfg "$C" user.useConfigOnly)" true
check "tools put on PATH for the session" grep -q '.local/bin' "$TMP/env-cloud"
if [ "$HAS_PC" = yes ]; then
  check "pre-commit hook wired" grep -q pre-commit "$C/.git/hooks/pre-commit"
  check "commit-msg hook wired" grep -q pre-commit "$C/.git/hooks/commit-msg"
else
  check "no .pre-commit-config.yaml: no hook wired, and no error" test ! -e "$C/.git/hooks/commit-msg"
fi

echo "end to end in the set-up repo:"
(cd "$C" && git commit -q --allow-empty -m 'test(session): a valid commit' > /dev/null 2>&1)
check "a valid commit lands" is "$(git -C "$C" log -1 --format=%s)" "test(session): a valid commit"
check "with the owner's identity, author and committer" \
  is "$(git -C "$C" log -1 --format='%an <%ae> | %cn <%ce>')" "$NAME <$EMAIL> | $NAME <$EMAIL>"
if [ "$HAS_PC" = yes ]; then
  before=$(git -C "$C" rev-list --count HEAD)
  (cd "$C" && git commit -q --allow-empty -m 'docs: no scope' > /dev/null 2>&1)
  check "a bare 'docs: no scope' is refused" is "$(git -C "$C" rev-list --count HEAD)" "$before"
fi

echo "no signing key in the environment -- signing stays the platform's:"
check "no repo-local gpg.ssh.program" unset_in "$C" gpg.ssh.program
check "no repo-local user.signingkey" unset_in "$C" user.signingkey
check "no key file written" test ! -e "$C/.git/signing-key"

echo "run again -- must be safe to repeat:"
run_hook "$C" "$TMP/env-cloud-2" CLAUDE_CODE_REMOTE=true > /dev/null 2>&1
check "exits 0 the second time" is "$?" 0
check "identity unchanged" is "$(cfg "$C" user.email)" "$EMAIL"

echo "with the owner's signing key -- commits are signed with it:"
ssh-keygen -q -t ed25519 -N '' -C 'test signing key' -f "$TMP/test-key"
K="$TMP/signed"
fresh "$K"
run_hook "$K" "$TMP/env-signed" CLAUDE_CODE_REMOTE=true \
  GIT_SIGNING_KEY_B64="$(base64 -w0 "$TMP/test-key")" > "$TMP/signed.log" 2>&1
check "exits 0" is "$?" 0
check "gpg.format is ssh" is "$(cfg "$K" gpg.format)" ssh
check "signs with ssh-keygen, not the platform's helper" is "$(cfg "$K" gpg.ssh.program)" ssh-keygen
check "commit.gpgsign set" is "$(cfg "$K" commit.gpgsign)" true
# -ef, not string equality: git may spell the path its own way (C:/... under Git for Windows).
check "the key sits in .git, not the work tree" test "$(cfg "$K" user.signingkey)" -ef "$K/.git/signing-key"
check "the key file is the given key" cmp -s "$TMP/test-key" "$K/.git/signing-key"
check "the key is never printed" sh -c "! grep -q 'PRIVATE KEY' '$TMP/signed.log'"
(cd "$K" && git commit -q --allow-empty -m 'test(session): a signed commit' > /dev/null 2>&1)
check "a commit lands" is "$(git -C "$K" log -1 --format=%s)" "test(session): a signed commit"
check "and verifies as signed by that key (G)" is "$(git -C "$K" log -1 --format=%G?)" G

echo "with a broken key -- warns, keeps the platform's signing, sets the rest up:"
B="$TMP/broken"
fresh "$B"
run_hook "$B" "$TMP/env-broken" CLAUDE_CODE_REMOTE=true \
  GIT_SIGNING_KEY_B64="$(printf 'not a key' | base64)" > "$TMP/broken.log" 2>&1
check "exits 0" is "$?" 0
check "says the key is unusable" grep -q 'GIT_SIGNING_KEY_B64' "$TMP/broken.log"
check "no repo-local user.signingkey" unset_in "$B" user.signingkey
check "no key file left behind" test ! -e "$B/.git/signing-key"
check "the identity is still set" is "$(cfg "$B" user.email)" "$EMAIL"

echo "with a key that needs a passphrase -- refused at once, never waits for one:"
ssh-keygen -q -t ed25519 -N 'secret' -C 'test key with a passphrase' -f "$TMP/locked-key"
L="$TMP/locked"
fresh "$L"
timeout 120 bash -c 'run_hook "$@"' _ "$L" "$TMP/env-locked" CLAUDE_CODE_REMOTE=true \
  GIT_SIGNING_KEY_B64="$(base64 -w0 "$TMP/locked-key")" < /dev/null > "$TMP/locked.log" 2>&1
check "exits 0 (not killed by the timeout)" is "$?" 0
check "says the key is unusable" grep -q 'GIT_SIGNING_KEY_B64' "$TMP/locked.log"
check "no key file left behind" test ! -e "$L/.git/signing-key"

printf '\n%s\n' "$pass passed, $fail failed"
if [ $((pass + fail)) -eq 0 ]; then
  echo "no checks ran -- that is a failure, not a pass" >&2
  exit 1
fi
[ "$fail" -eq 0 ]
