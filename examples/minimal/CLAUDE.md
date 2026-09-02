# minimal — Operating Instructions

Built under Hyperion (vendored at `hyperion/`, version pinned in `.hyperion/version`).
Project state lives in `trace/`; never restate it here.

## Declaration
    SESSION: <GATE | CONTRACT | CONFORMANCE | IMPLEMENT | REVIEW | INTEGRATE | LESSON | BASELINE | QUERY>
    SLICE: <SL-nn>
    SCOPE: <one thing>
    MAY MODIFY: <globs from the session table>

<!-- The three blocks below are placeholders. The operating-layer generator that fills
     them from core does not exist yet; until it does, copy the corresponding sections
     from templates/project-CLAUDE.md. -->
<!-- generated:session-table --> ... <!-- /generated -->
<!-- generated:imperatives --> ... <!-- /generated -->
<!-- generated:loadout --> ... <!-- /generated -->

## Commands
    pytest -q                                    # full suite, writes trace/results.xml
    ATMOSPHERE_IMPL=null pytest modules/atmosphere/conformance   # must FAIL (null double)
    python hyperion/tooling/check_traces.py
    python hyperion/tooling/check_traces.py --report > trace/matrix.md
