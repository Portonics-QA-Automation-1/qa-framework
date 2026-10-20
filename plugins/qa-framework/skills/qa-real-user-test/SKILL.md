---
name: qa-real-user-test
description: Start a real-user exploratory testing session for a feature, reacting to screenshots like a first-time customer. Usage - /qa-real-user-test <feature name>
---

Delegate to the `qa-framework:qa-real-user` subagent for the feature named in the
argument. Tell the QA member you're ready for the first screenshot and will
react as a first-time user with no system knowledge, flagging friction as
you go and logging findings to `./qa_findings/`.

At the end of the session (when the QA member says they're done, or asks
for a summary), list the findings written during this session grouped by
kind (usability / bug / test_idea) with short titles — don't re-paste full
file contents.
