version := `uvx --from "mddj==0.3.0" mddj read version`

build:
    uvx --from build pyproject-build .

publish: build
    uvx flit publish

tag-release:
    git tag -s "{{version}}" -m "v{{version}}"
