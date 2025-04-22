.PHONY: build-env run-pipeline build-paper

build-env:
	docker build -t auto-eeg-paper-env .

run-pipeline:
	prefect deployment build pipeline/flow.py:flow \
	  --name "EEG Pipeline" \
	  --apply
	prefect deployment run "EEG Pipeline"

build-paper:
	# assumes you have a script that takes the AI draft + figures and calls Manubot
	python pipeline/manuscript_build.py
