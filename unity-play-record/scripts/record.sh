#!/bin/bash
# Records a scenario in Unity play mode and makes an mp4. Run from the Unity project root (Git Bash on Windows).
# usage:
#   bash record.sh --scene <scene.unity> --scenario <scenario.cs> --tag <name> [--arg <value>]... [--return <scene.unity>]
#                  [--compare <old tag>] [compose.py options: --part attack|idle|both --zoom x,y,w,h --labels "a|b" --loops N]
# Output: Temp/PlayRec/<tag>.mp4, Temp/PlayRec/<tag>_sheet.jpg, Temp/PlayRec/<tag>/ (frames, done.txt)
# The last line printed is "RESULT ok <mp4> (<done.txt>)" or "RESULT fail <reason>".
set -u
P="$(pwd -W 2>/dev/null || pwd)"; S="$(cd "$(dirname "$0")" && (pwd -W 2>/dev/null || pwd))"
SCENE=""; SCEN=""; TAG=""; RET=""; CMP=""; ARGS=(); REST=()
while [ $# -gt 0 ]; do
  case "$1" in
    --scene) SCENE="$2"; shift 2;; --scenario) SCEN="$2"; shift 2;; --tag) TAG="$2"; shift 2;;
    --arg) ARGS+=("$2"); shift 2;; --return) RET="$2"; shift 2;; --compare) CMP="$2"; shift 2;;
    *) REST+=("$1"); shift;;
  esac
done
fail() { echo "RESULT fail $1"; exit 1; }
[ -n "$SCENE" ] && [ -n "$SCEN" ] && [ -n "$TAG" ] || fail "need --scene, --scenario and --tag"
[ -f "$SCEN" ] || fail "scenario file not found: $SCEN"
W="$P/Temp/PlayRec"; mkdir -p "$W"
ev() { unity command --project-path "$P" eval_file --file "$1" 2>&1 | grep -o '"result":"[^"]*"\|timed out[^"]*\|Error: [^"]*' | head -1; }

{ echo "$TAG"; for a in "${ARGS[@]+"${ARGS[@]}"}"; do echo "$a"; done; } > "$W/job.txt"
printf '%s\n%s\n' "$SCENE" "$RET" > "$W/scene.txt"
st=$(ev "$S/state.cs"); echo "state: $st"
echo "$st" | grep -q "playing=True" && fail "the editor is already in play mode (someone may be playing; not stopping it)"
echo "$st" | grep -q "dirty=True" && fail "the open scene has unsaved changes"
echo "$st" | grep -q "result" || fail "editor not reachable: $st (is the Unity Editor open with the Pipeline server, and in the foreground?)"
[ -z "$RET" ] && RET=$(echo "$st" | sed -n 's/.*scene=\([^ "]*\).*/\1/p') && printf '%s\n%s\n' "$SCENE" "$RET" > "$W/scene.txt"
echo "open: $(ev "$S/open_scene.cs")"
for i in $(seq 1 40); do sleep 3; o=$(ev "$S/state.cs"); echo "$o" | grep -q "playing=True" && break; done
echo "$o" | grep -q "playing=True" || fail "play mode did not start"
sleep 4; echo "scenario: $(ev "$(cd "$(dirname "$SCEN")" && (pwd -W 2>/dev/null || pwd))/$(basename "$SCEN")")"
for i in $(seq 1 150); do [ -f "$W/$TAG/done.txt" ] && break; sleep 2; done
DONE=$(cat "$W/$TAG/done.txt" 2>/dev/null); echo "done: $DONE"
echo "stop: $(ev "$S/stop.cs")"
for i in $(seq 1 20); do sleep 2; o=$(ev "$S/state.cs"); echo "$o" | grep -q "playing=False" && break; done
echo "back: $(ev "$S/return_scene.cs")"
[ -n "$DONE" ] || fail "the scenario did not write done.txt"

PART=attack; ls "$W/$TAG"/attack_*.jpg >/dev/null 2>&1 || PART=idle
python -I "$S/compose.py" "$TAG" $CMP --part $PART "${REST[@]+"${REST[@]}"}" || fail "compose failed"
echo "$P/Temp/PlayRec/$TAG.mp4" > "$W/encode.txt"; rm -f "$W/encode_done.txt"
echo "encode: $(ev "$S/encode.cs")"
for i in $(seq 1 90); do [ -f "$W/encode_done.txt" ] && break; sleep 2; done
[ -f "$W/encode_done.txt" ] || fail "encode did not finish"
echo "RESULT ok $W/$TAG.mp4 ($DONE)"
