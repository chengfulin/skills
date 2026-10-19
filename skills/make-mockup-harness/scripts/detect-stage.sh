#!/usr/bin/env bash
# 用法：detect-stage.sh <make-mockups/<slug>/.mockup-workflow.json>
# 輸出：slug、currentVersion、stage、下一步驟編號
set -euo pipefail
f="${1:?state file}"
python3 - "$f" <<'PY'
import json, sys
s = json.load(open(sys.argv[1]))
nxt = {"init":1,"storyboard":2,"brief":3,"handoff":4,"export":5,"review":"6|7","iterate":2,"handed-off":6}
stage = s.get("stage","init")
print(f"feature={s.get('feature')} version={s.get('currentVersion')} stage={stage} next_step={nxt.get(stage,'?')}")
cd = s.get("claudeDesign") or {}
print(f"claudeDesign.projectUrl={cd.get('projectUrl')}")
PY
