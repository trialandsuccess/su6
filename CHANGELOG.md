# Changelog

<!--next-version-placeholder-->

## v0.3.0 (2023-05-28)
### Feature
* **all:** Allow running `su6 all --ignore-uninstalled` so missing checking tools don't affect the final exit code of 'all' ([`35ad498`](https://github.com/robinvandernoord/su6-checker/commit/35ad498983bd651d66bfa3e773b9a1e1e7d94e6c))
* **pydocstyle:** Added docstring checker (and docstrings) ([`4ad2c29`](https://github.com/robinvandernoord/su6-checker/commit/4ad2c29c88a840dd01640a8d9bcf4695834e37a5))

### Documentation
* **readme:** Added list of supported tools ([`02fb7a8`](https://github.com/robinvandernoord/su6-checker/commit/02fb7a86673f64e4ab937b6f5a7b45543ab86aa1))

## v0.2.1 (2023-05-27)
### Fix
* **exit codes:** They now actually work™ ([`503c69c`](https://github.com/robinvandernoord/su6-checker/commit/503c69ccf5d4d91847fd4f0580511d6a89800fd6))

## v0.2.0 (2023-05-27)
### Feature
* **shell:** Introduce @with_exit_code decorator to generate an exit code based on the return value of a command method ([`7d6d4e2`](https://github.com/robinvandernoord/su6-checker/commit/7d6d4e27c2226538b79f63b972c90045517cbe46))

### Fix
* **log:** First show status and then show any output, this works less confusing IMO ([`176966d`](https://github.com/robinvandernoord/su6-checker/commit/176966df86383887ac837c35de1d423c1ca03546))

## v0.1.3 (2023-05-27)
### Fix
* **namespace:** Moved everything to 'su6' so the hatch build succeeds (it's late...) ([`e87aed9`](https://github.com/robinvandernoord/su6-checker/commit/e87aed9660449560256e32178e730157a153bb47))

## v0.1.2 (2023-05-27)
### Documentation
* **README:** Actually fixed the badges and added link to changelog ([`aabbc39`](https://github.com/robinvandernoord/su6-checker/commit/aabbc39a5bfccf05248b8d21c105fc758befa240))

## v0.1.1 (2023-05-27)
### Documentation
* **readme:** Started on the readme, more to follow when it's not almost 2 am ([`5ccfe62`](https://github.com/robinvandernoord/su6-checker/commit/5ccfe6232a58776dcee3c1a969a07711d479f0e3))
* **changelog:** Manually added 0.1 ([`35d9b3b`](https://github.com/robinvandernoord/su6-checker/commit/35d9b3b1caedad64e4b68d40b1567fa154bad249))

## v0.1.0 (2023-05-27)
*Feature*: Initial Version 🎉
