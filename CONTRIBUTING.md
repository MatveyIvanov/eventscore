# Contributing to Eventscore

Welcome! Eventscore is an open source project that aims to help
building modular monolithic applications using power of event-driven design.

## Code of Conduct

Everyone participating in the Eventscore community, and in particular in our
issue tracker, pull requests, and chat, is expected to treat
other people with respect and more generally to follow the guidelines
articulated in the [Python Community Code of Conduct](https://policies.python.org/python.org/code-of-conduct/).

## Getting started with development

### Setup

#### (1) Fork the Eventscore repository

Within GitHub, navigate to <https://github.com/MatveyIvanov/Eventscore> and fork the repository.

#### (2) Clone the Eventscore repository and enter into it

```bash
git clone git@github.com:<your_username>/Eventscore.git
cd Eventscore
```

#### (3) Install dependencies (poetry required)

```bash
poetry install
```

> **Note**
> You'll need Python 3.11 or higher to install all requirements listed in
> pyproject.toml

### Running tests

Running the full test suite can take a while, and usually isn't necessary when
preparing a PR. Once you file a PR, the full test suite will run on GitHub.
You'll then be able to see any test failures, and make any necessary changes to
your PR.

However, if you wish to do so, you can run the full test suite
like this:

```bash
make test
```

or some specific types of tests

```bash
make test-unit
make test-integration
make test-e2e
```

> **Note**
> You'll need Docker to run e2e and some integration tests.
> Make script supports both docker-compose and docker compose commands.
> If you use Podman or similar that is compatible with docker-compose specifications,
> make sure to add a symbolic link for your binary so it could be executed as docker-compose.

Some other useful make commands:

```bash
# Use flake8 and ruff for linting
make lint

# Check formatting with black
make formatcheck
# Format with black
make format

# Check sorting with isort
make sortcheck
# Format with Black
make sort

# Run static type-checkers (mypy and pyright)
make analyze
```

#### Using `tox`

You can also use [`tox`](https://tox.wiki/en/latest/) to run tests and other commands.
`tox` handles setting up test environments for you.

```bash
# Run tests
make tox

# Or
poetry run tox
```

## Submitting changes

Even more excellent than a good bug report is a fix for a bug, or the
implementation of a much-needed new feature. We'd love to have
your contributions.

We use the usual GitHub pull-request flow, which may be familiar to
you if you've contributed to other projects on GitHub.

Anyone interested in Eventscore may review your code. One of the Eventscore core
developers will merge your pull request when they think it's ready.

If your change will be a significant amount of work
to write, we highly recommend starting by opening an issue laying out
what you want to do. That lets a conversation happen early in case
other contributors disagree with what you'd like to do or have ideas
that will help you do it.

The best pull requests are focused, clearly describe what they're for
and why they're correct, and contain tests for whatever changes they
make to the code's behavior.

Also, do not squash your commits after you have submitted a pull request, as this
erases context during review. We will squash commits when the pull request is merged.

## Core developer guidelines

Core developers should follow these rules when processing pull requests:

- Always wait for tests to pass before merging PRs.
- Use "[Squash and merge](https://github.com/blog/2141-squash-your-commits)"
  to merge PRs.
- Delete branches for merged PRs (by core devs pushing to the main repo).
- Edit the final commit message before merging to conform to the following
  style (we wish to have a clean `git log` output):
    - When merging a multi-commit PR make sure that the commit message doesn't
      contain the local history from the committer and the review history from
      the PR. Edit the message to only describe the end state of the PR.
    - Make sure there is a *single* newline at the end of the commit message.
      This way there is a single empty line between commits in `git log`
      output.
    - Split lines as needed so that the maximum line length of the commit
      message is under 80 characters, including the subject line.
    - Capitalize the subject and each paragraph.
    - Make sure that the subject of the commit message has no trailing dot.
    - Use the imperative mood in the subject line (e.g. "Fix typo in README").
    - If the PR fixes an issue, make sure something like "Fixes #xxx." occurs
      in the body of the message (not in the subject).
    - Use Markdown for formatting.
