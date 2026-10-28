.PHONY: demo demo-check demo-status

demo:
	uv run python scripts/run_demo.py

demo-check:
	uv run python scripts/run_demo.py --check-only

demo-status:
	uv run python scripts/run_demo.py --status
