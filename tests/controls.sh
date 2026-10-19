# shellcheck shell=bash
# shellcheck disable=SC2154  # HERE, tmp, INPUTS and WHAT are the sourcing test's
# The helpers of the tests that hold a script to its controls, sourced by test-check-previews.sh,
# test-sweep-side-by-side.sh and test-build-tokens.sh. Each test sets, before its first control:
#   HERE, tmp                 the repository, and a scratch folder for the copies
#   INPUTS                    the files and folders the script reads, relative to the repository
#   WHAT                      what a run is called in a message: check, sweep or build
# and defines the runner:
#   run <dir> [arguments...]  the script on the copy in <dir>, its output in <dir>/out.txt
# A control is a fresh copy of INPUTS with one mistake put in. It counts as refused only if the run
# fails AND its output matches the control's pattern: a run that fails for another reason proves
# nothing. The test reads `controls` and `refused` at the end. A test may define its own `wanted`
# after sourcing this file, to run only some controls (ONLY in test-check-previews.sh).
controls=0
refused=0

wanted() { true; } # wanted <label>: whether the control runs

copy() { # copy <dir>: the script's inputs, as they are in the working tree, to <dir>, a full path
  # One cp (GNU's --parents keeps each input's path): three processes per input cost most of a
  # second a control in Git Bash on Windows, where starting one is slow (measured)
  mkdir -p "$1" && (cd "$HERE" && cp -r --parents "${INPUTS[@]}" "$1/")
}

fresh() { # fresh: a new copy for the next control, in $dir
  dir="$tmp/c$controls"
  controls=$((controls + 1))
  copy "$dir"
}

judge() { # judge <dir> <label> <pattern> [arguments...]: the run on the mutated copy must fail, saying /pattern/
  local dir="$1" label="$2" pattern="$3"
  shift 3
  if run "$dir" "$@"; then
    printf '    FAIL  control "%s": the %s passed it\n' "$label" "$WHAT"
  elif grep -qE -- "$pattern" "$dir/out.txt"; then
    printf '    ok    control "%s": refused\n' "$label"
    refused=$((refused + 1))
  else
    printf '    FAIL  control "%s": failed, but not with /%s/:\n' "$label" "$pattern"
    grep -E '^FAIL|Error|error:' "$dir/out.txt" | sed 's/^/          /' | head -5
  fi
}

replace() { # replace <file> <old> <new>: every <old> in the file made <new>; fails if there is none
  python3 -I - "$1" "$2" "$3" << 'EOF'
import sys
path, old, new = sys.argv[1:]
text = open(path, encoding="utf-8", newline="").read()
if old not in text:
    sys.exit(1)
open(path, "w", encoding="utf-8", newline="").write(text.replace(old, new))
EOF
}

query() { # query <side-by-side|side-h>: the side-by-side media query bundle.css must have, or its least height H, from the build
  local q
  q="$(uv run -q --project "$HERE" --locked python "$HERE/scripts/build-tokens.py" --query "$1")" && [ -n "$q" ] || return 1
  printf '%s' "$q"
}

css() { # css <label> <pattern> <arguments> <css>: a rule added at the end of bundle.css
  wanted "$1" || return 0
  fresh
  printf '%s\n' "$4" >> "$dir/components/bundle.css"
  # shellcheck disable=SC2086  # the arguments are words
  judge "$dir" "$1" "$2" $3
}

sub() { # sub <label> <pattern> <arguments> <file> <old> <new>: one text replaced in a copied file
  wanted "$1" || return 0
  fresh
  if ! replace "$dir/$4" "$5" "$6"; then
    printf '    FAIL  control "%s": its text is not in %s; the control no longer tests anything\n' "$1" "$4"
    return
  fi
  # shellcheck disable=SC2086
  judge "$dir" "$1" "$2" $3
}

gone() { # gone <label> <pattern> <arguments> <path>: a copied file or folder deleted
  wanted "$1" || return 0
  fresh
  rm -r "${dir:?}/$4"
  # shellcheck disable=SC2086
  judge "$dir" "$1" "$2" $3
}
