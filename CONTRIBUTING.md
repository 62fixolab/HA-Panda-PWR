# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. Make sure your code lints (using `scripts/lint.sh`).
4. Run the tests (using `scripts/test.sh`) and add tests for your change.
5. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [Ruff](https://docs.astral.sh/ruff/) to make sure the code follows the style (`scripts/lint.sh`).

## Test your code modification

This custom component is based on [panda_pwr template](https://github.com/62fixolab/panda_pwr).

It comes with development environment in a container, easy to launch
if you use Visual Studio Code. With this container you will have a stand alone
Home Assistant instance running and already configured with the included
[`configuration.yaml`](./config/configuration.yaml)
file.

The tests in [`tests/`](./tests) run Home Assistant against a simulated Panda PWR that can go offline or send broken replies.
Install their requirements with `scripts/setup.sh` and run them with `scripts/test.sh`.
CI runs them on the oldest supported Home Assistant release (`tests/requirements_min.txt`) and on the latest one (`requirements_test.txt`).

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
