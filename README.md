# DevOps README Automation

[![Build-Test-Release](https://github.com/mona618/devops-readme-automation/actions/workflows/deployment-pipeline.yml/badge.svg?branch=main)](https://github.com/mona618/devops-readme-automation/actions/workflows/deployment-pipeline.yml)

This repository demonstrates a DevOps workflow that updates repository activity in the README with GitHub Actions.

## Recent Repository Activity

<!-- ACTIVITY:START -->
## Latest Commits

- `c16d597` test(ci): add opt-in failing assertion for release gate demo — **HO TSAI-NI** (2026-10-13)
- `9165f7f` fix(ci): configure pip cache dependency path — **HO TSAI-NI** (2026-10-13)
- `d61b708` feat(ci): gate multi-environment releases on tests — **HO TSAI-NI** (2026-10-13)
- `a56ded3` fix: use Copilot Auto model for free plan — **mona618** (2026-10-06)
- `f3bfbc1` fix: use supported Copilot model for release notes agent — **mona618** (2026-10-06)
<!-- ACTIVITY:END -->

## Build, Test, and Release

The deployment workflow builds one ZIP artifact, runs unit and integration tests on Python 3.11 and 3.12, and publishes the tested artifact to dev and staging. A production smoke test runs with `TEST_ENV=prod`. Production release uses the protected `production` GitHub environment and waits for an authorized reviewer.

The unit stage publishes JUnit XML and coverage XML reports. Releases are blocked unless both staging test stages pass; the production release also depends on the production smoke test.

