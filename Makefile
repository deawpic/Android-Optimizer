# ==============================================================================
# Android Optimizer Production Harness - Automation Makefile
# ==============================================================================

PYTHON ?= python

.PHONY: help ping bench perf export journey optimize debloat restore kernel rollback lint tv-detect tv-clean tv-restore

help:
	@echo "Android Optimizer Production Harness Targets:"
	@echo "  make ping       - Probes active ADB device and battery telemetry"
	@echo "  make bench      - Runs Ground Truth 12-case evaluation suite"
	@echo "  make perf       - Runs Tier-0 cache latency & token benchmark"
	@echo "  make journey    - Runs automated QA Journey Test for emulators"
	@echo "  make export     - Exports clean UTF-8 markdown report to ./output/"
	@echo "  make optimize   - Runs rootless performance optimizer (scripts/run_optimizer.sh)"
	@echo "  make debloat    - Runs safe User-0 debloater for connected OEM (scripts/debloat.sh)"
	@echo "  make restore    - Reinstates debloated packages (scripts/restore_apps.sh)"
	@echo "  make kernel     - Runs root kernel, GPU, and memory tuner (scripts/root_kernel_tweak.sh)"
	@echo "  make rollback   - Restores all parameters and apps to factory defaults (scripts/rollback.sh)"
	@echo "  make tv-detect  - Detects Android TV / Google TV profile & launchers"
	@echo "  make tv-clean   - Runs CleanYourTV debloat over Wi-Fi (scripts/tv_optimizer.py)"
	@echo "  make tv-restore - Re-enables all disabled TV packages and restores stock launcher"
	@echo "  make lint       - Runs document and formatting audits"

ping:
	$(PYTHON) scripts/ping_device.py

bench:
	$(PYTHON) evals/eval_benchmarks.py

perf:
	$(PYTHON) evals/run_performance_bench.py

journey:
	$(PYTHON) scripts/run_emulator_journey.py --mock

export:
	$(PYTHON) scripts/export_report.py

optimize:
	bash scripts/run_optimizer.sh

debloat:
	bash scripts/debloat.sh

restore:
	bash scripts/restore_apps.sh

kernel:
	bash scripts/root_kernel_tweak.sh

rollback:
	bash scripts/rollback.sh

tv-detect:
	$(PYTHON) scripts/tv_optimizer.py --detect

tv-clean:
	$(PYTHON) scripts/tv_optimizer.py --clean

tv-restore:
	$(PYTHON) scripts/tv_optimizer.py --restore

lint:
	$(PYTHON) -c "from harness.document import audit_document_formatting; from pathlib import Path; [print(f.name, audit_document_formatting(f.read_text(encoding='utf-8'))['is_valid']) for f in list(Path('.').glob('*.md')) + list(Path('output').glob('*.md'))]"
