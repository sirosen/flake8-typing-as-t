.PHONY: build
build:
	hatch build

.PHONY: publish-from-pypirc
publish-from-pypirc: build
	@echo "making some assumptions about your ~/.pypirc..."
	hatch publish -u '__token__' -a "$$(cat ~/.pypirc| grep '^password' | head -n1 | cut -d'=' -f2 | tr -d ' ')"
