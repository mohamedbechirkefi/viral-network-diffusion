<!-- SPDX-License-Identifier: LicenseRef-VIRAL-NC-Research-1.0 -->
# Reproducibility report checklist

Status at M5 (2026-11-25): confirmatory and exploratory results exist (M3, M4) and the demo builds offline in the working tree (`progress.md`, M5). To complete at M6 in a clean clone, with actual command outputs.

- [ ] Clean clone into a separate directory.
- [ ] `uv sync --locked` succeeds.
- [ ] Test suite runs; actual count and result recorded.
- [ ] Smoke reproduction matches stored results within the documented tolerance.
- [ ] Demo builds offline.
- [ ] Data manifest and links verified.
- [ ] Secret and licence scan.
- [ ] Hardware, OS, package versions and git revision recorded.
