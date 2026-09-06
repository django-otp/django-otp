set minimum-version := "1.53.0"

set unstable
set lists


[private]
default:
    @just --list --unsorted

# Run all linters and tests
[group('main')]
check:
    hatch run check

# Run the test project server
[group('main')]
runserver *args: (manage ["runserver", args])

# Run all linters
[group('test')]
lint:
    hatch run lint

# Run all fixers, repairing some lint errors
[group('test')]
fix:
    hatch run fix

# Run tests in the default environment
[group('test')]
test *args:
    hatch run test {{ quote(args) }}

# Run tests with all warnings enabled
[group('test')]
warn *args:
    hatch run warn {{ quote(args) }}

# Run tests with code coverage enabled
[group('test')]
coverage *args:
    hatch run cov {{ quote(args) }}

alias cov := coverage

# Run tests across multiple environments
[group('test')]
test-all *args:
    hatch run test:run {{ quote(args) }}

# Build the documentation
[group('docs')]
make-docs:
    hatch run docs:make

# Open the local documentation in a browser
[group('docs')]
open-docs:
    hatch run docs:open

# Run migrations in the test project
[group('django')]
migrate *args: (manage ["migrate", args])

# Run a Django management command in the test project
[group('django')]
manage *args:
    hatch run manage {{ quote(args) }}

# Release a new version (patch/minor/major)
[group('admin')]
release version *args:
    hatch run bumpversion {{ quote(version) }} {{ quote(args) }}
    hatch clean
    hatch build
    hatch publish
