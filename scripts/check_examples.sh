#!/usr/bin/env bash
# Run every cross-language example whose toolchain is installed and diff it against expected_output.txt.
set -uo pipefail
cd "$(dirname "$0")/../examples"
exp=expected_output.txt
status=0
check() { # name, command...
  local name=$1; shift
  if out=$("$@" 2>&1) && diff -q <(printf '%s\n' "$out") "$exp" >/dev/null; then
    printf '  %-10s ok\n' "$name"
  else
    printf '  %-10s FAILED\n' "$name"; printf '%s\n' "$out" | head -5; status=1
  fi
}
skip() { printf '  %-10s skipped (%s not installed)\n' "$1" "$2"; }

check shell bash shell/kurdish.sh
check python python3 python/kurdish.py
command -v node  >/dev/null && check typescript node typescript/kurdish.ts || skip typescript node
command -v java  >/dev/null && check java bash -c 'cd java && java Kurdish.java' || skip java java
command -v cargo >/dev/null && check rust bash -c 'cd rust && cargo run -q --offline' || skip rust cargo
command -v go    >/dev/null && check go bash -c 'cd go && go run .' || skip go go
command -v dotnet >/dev/null && check csharp bash -c 'cd csharp && dotnet run' || skip csharp dotnet
command -v dotnet >/dev/null && check fsharp bash -c 'cd fsharp && dotnet run' || skip fsharp dotnet
exit $status
