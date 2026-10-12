set lazy
version := `uvx mddj read version`

# show help (default)
default:
    @just --list

# run tests
test:
    nox -j auto
# run linters
lint:
    nox -t lint
# run all verification jobs
verify:
    nox -j auto -t verify

# build the package
build:
    uv build

# publish the package to pypi
publish: build
    uvx flit publish

# tag a release
tag-release:
    git tag -s "{{version}}" -m "v{{version}}"

# remove ephemeral files
clean:
	rm -rf dist build *.egg-info .tox .venv
	find . -type d -name '__pycache__' -exec rm -r {} +
