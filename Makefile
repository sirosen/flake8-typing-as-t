.PHONY: build
build:
	uvx --from build pyproject-build .

.PHONY: publish
publish: build
	uvx flit publish
