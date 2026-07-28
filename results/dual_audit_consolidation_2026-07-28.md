# Dual external audit consolidation — 2026-07-28 (WIB)

Sources:
- ChatGPT Work audit (Spark-disk seat; read-only)
- Claude Cowork audit (GitHub + live HF seat; Spark disk unread)

Manwë live verify on this timeline: Mac local trees, Synology mount, Spark SSH, HF HEAD probes.
No writes to GH/HF. No inference. Authority: advisory only.

## Joint verdict (bind)

| Gate | Result | Notes |
|---|---|---|
| S freeze remediation continue | **YES** | Integrity work only — not freeze-declared |
| XS measure clearance | **NO** | Storage SHA ≠ runtime |
| Paste-safe as full advisory | **YES** | Keep caveats + verdict strip; no isolated yes/all_go |
| Combined S+XS performance story | **NO** | Never |

## Manwë live corroboration (higher-severity)

Confirmed ChatGPT + Claude both right, or one seat right with physical proof:

1. **Q4 symlink + SHA on Spark** — realpath → `/home/hizrianraz/models/laguna-s-2.1/laguna-s-2.1-Q4_K_M.gguf`; sha `a8b55c…` matches SHA256SUMS Q4 line. Identity only.
2. **Smoke timeline vs IQ3** — agent_smoke 40/40 mtime 19:13; hermes 27/27 mtime 19:47; IQ3 meta 20:10–20:19; q4_restore.log ends 20:18. So Q4 **process restore after both headline smokes**. ChatGPT High finding stands: no post-restore Q4 smoke bound to restored process.
3. **SPARK.md hermes row still "pending live run"** while JSON + README claim 27/27 and **HF serves** `results/hermes_agent_smoke.json` (307 resolve hit). Public contradiction confirmed by both seats.
4. **hf_publish.json stale** — `hermes_v2_results_on_hf: false` while HF has the file; local_git_head/receipt lag behind origin tip noise.
5. **SHA256SUMS is 3-column** (`sha size name`); `pull_official_gguf.sh` tees sha256 but does **not** fail closed on mismatch against pack file. ChatGPT High stands.
6. **`.gitignore` deny `results/*.json`** with limited whitelist — placement receipts `three_jury_post_placement_2026-07-28.json` + `weight_placement_2026-07-28.json` exist on Mac + Synology + Spark **local only**, blocked from origin. Claude High on pushability stands.
7. **Dirty S tree** @ 3ba4160: modified `.gitignore`, prompts; untracked `docs/WEIGHTS_LOCAL.md`, `prompts/_mirror/`, `results/hermes_agent_smoke.log`.
8. **engine_sha.txt** says `#include <cmath>`; MEASURED + SPARK say `math.h` + `::isfinite`. Low but freeze-irrelevant only if canonical patch file is committed.
9. **serve_spark.sh** defaults `0.0.0.0`; public JSONs paste `http://100.98.213.2:8000/v1`. Intentional vs scrub = founder call.
10. **XS measured.json** honestly `unmeasured` / nulls. GREEN honesty (Claude).
11. **XS hermes README** still has **"Measured (live Spark) 27/27"** block — S bleed. ChatGPT High stands.
12. **Fixtures** carry Spark/S strings + "~21 tok/s" / "this host has ~21 tok/s" inside XS cases.json (byte-shared suite).
13. **serve_mac.sh** has no `--jinja` (S serve does). Claude MED stands.
14. **XS row inside S README "Quant guide (what to pull)"** — wording honest, table framing wrong (Claude MED-LOW).

## Severity merged (actionable, pre 2026-08-02 18:00 WIB freeze)

### S — do before freeze claim

| # | Item | Sev | Do |
|---|---|---|---|
| S1 | Post-restore final Q4 agent_smoke (+ hermes if 27/27 stays current) bound to process/engine/SHA/harness | High | Rerun on frozen Q4 process; write run manifest |
| S2 | Checksum enforce | High | Fix pull helper fail-closed; standard verify path against pack digest |
| S3 | Provenance in smoke JSON | High | host, realpath+SHA, engine SHA+patch, flags, harness hashes, timestamps |
| S4 | Doc contradiction erase | High | SPARK.md hermes row; one freeze run ID everywhere |
| S5 | Fresh hf_publish + HF/GH sync last | High | After docs/results settle |
| S6 | Clean tree + S-only freeze manifest + canonical Git SHA | High | Reconcile dirty; decide public vs local receipts |
| S7 | Placement receipts policy | High | Whitelist+push **or** intentional local-only; stop citing as public |
| S8 | IQ3 wording | High/Med | Not "same-harness" vs Q4 runner silently; explicit older-runner or rerun |
| S9 | Protocol-smoke labels | Med | "one-response protocol; tools validated not executed" |
| S10 | Wording cuts | Med | Laguna Mac = client→Spark; no XS story on S scoreboard; freeze SP leakage |

### XS — prep only (no measure authority)

| # | Item | Sev | Do |
|---|---|---|---|
| X1 | Kill Spark 27/27 block in XS hermes README | High | "XS/Mac unmeasured" |
| X2 | "stand-behind SKU" → disk candidate | High | README/locks |
| X3 | Fixture / suite policy | High | Founder: synthetic-label vs neutral suite + dual rerun |
| X4 | Pin Mac-good engine SHA + Metal empty-out gate | High | Before any load |
| X5 | serve_mac.sh `--jinja` + explicit binary | Med/High | Before measure |
| X6 | Canonical B lock | Med | prep published; Q4 NAS only; no Mac load |
| X7 | Preregister pass bar | Med | before first run |

## Must-not (both audits agree)

- Full S local on founder ≤32G Mac
- XS renamed as S-lite / S quant / S-on-Mac
- Transfer 40/40, 27/27, ~21 t/s to XS
- Disk/SHA/startup = smoke
- Merge metrics / one headline
- Jury/all_go as technical authority
- XS demand stealing S freeze attention (`xs_may_delay_s_freeze: false`)

## Seat gaps (do not re-litigate)

| Gap | Owner |
|---|---|
| Dirty WT / on-disk only files | Spark seat (ChatGPT covered) ✓ |
| Live HF / PR #25165 merged / poolside sizes | GH seat (Claude covered) ✓ |
| Engine commit for XS Metal | **Founder** |
| Suite neutrality | **Founder** |
| Placement receipts public? | **Founder** |
| Stranger path: stock pin vs poolside fork required | **Founder** |
| Tailnet IP + 0.0.0.0 + prompts on HF | **Founder** (hygiene) |
| Mac RAM policy ≤32G if other machine exists | **Founder** |

## Freeze clock vs this note

- Freeze soft gate: **2026-08-02 18:00 WIB**
- HF launch surface: **2026-08-03 12:00 WIB**
- This note does **not** clear freeze, measure, or promote.
