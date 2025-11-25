build:
    uvx --from build pyproject-build .

publish: build
    uvx flit publish
