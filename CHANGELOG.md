# Changelog

<!--next-version-placeholder-->

## v0.9.0 (2023-06-01)
### Feature

* **all:** Add `stop-after-first-failure` flag to `all` and pyproject toml ([`906678a`](https://github.com/robinvandernoord/su6-checker/commit/906678a344aa68a2ef2101f9765dc1e601d5d5dd))
* **config:** 'include' can now also specify the order of checks to run in 'all' ([`6f9123b`](https://github.com/robinvandernoord/su6-checker/commit/6f9123b1869c15342bbc7e4d7cfb39f2fbb181bb))

### Documentation

* **README:** Better example for gh actions ([`73fa545`](https://github.com/robinvandernoord/su6-checker/commit/73fa5451ec0b0c7897eaa505c931f3af991a3a5d))

## v0.8.0 (2023-05-31)
### Feature

* **su6:** Add --version and self-update ([`084cd51`](https://github.com/robinvandernoord/su6-checker/commit/084cd51b066d8d055b62556567b02e8e0a39c5fe))

## v0.7.2 (2023-05-31)
### Fix

* **mypy:** Ensure config.badge is a string/path, not a bool ([`2c29b57`](https://github.com/robinvandernoord/su6-checker/commit/2c29b57a3c0502a7377941f0b48bc569aacc5d63))

## v0.7.1 (2023-05-31)


## v0.7.0 (2023-05-30)
### Feature
* **cov:** Add support for coverage svg badge to pytest ([`ee6c29c`](https://github.com/robinvandernoord/su6-checker/commit/ee6c29c2d16d379d7d4a09f97a6c6fb29943d513))

### Fix
* **cov:** 100% coverage again (and check for it) ([`c162e0d`](https://github.com/robinvandernoord/su6-checker/commit/c162e0d8b86782dfdc8c7e540a5f73f939cc1fa2))

## v0.6.0 (2023-05-30)
### Feature
* **format:** Allow `--format json` ([`3c958e5`](https://github.com/robinvandernoord/su6-checker/commit/3c958e5bb8dbfb79f76d3614385c062286429af4))

### Fix
* **json:** Format=json did not actually output json... Also update tests ([`df5fd41`](https://github.com/robinvandernoord/su6-checker/commit/df5fd411b8336e046165c6893777ed9abf539ae0))

### Documentation
* **format:** Allow `--format json` ([`29c5d0b`](https://github.com/robinvandernoord/su6-checker/commit/29c5d0b85e7e2c2bed2f6067ae0477e91256e8fc))

## v0.5.3 (2023-05-30)
### Fix
* **mypy:** Stricter rules regarding None ( but still allow implicit in function args >:( ) ([`46ff1d4`](https://github.com/robinvandernoord/su6-checker/commit/46ff1d4850074045c20f19d7135bb95d200a835b))

## v0.5.2 (2023-05-30)
### Documentation
* **readme:** Add supported args for each checker in 'use' ([`c091d2b`](https://github.com/robinvandernoord/su6-checker/commit/c091d2b21fa90ee0f2383d9bb101c327b0fd8036))

## v0.5.1 (2023-05-30)
### Fix
* **cov:** Forgot to add pytest-cov as dependency for 'all' ([`fef9b41`](https://github.com/robinvandernoord/su6-checker/commit/fef9b41543ecce11b8f157be8e7a5c5f59d6f248))

## v0.5.0 (2023-05-30)
### Feature
* **pytest:** Add pytest with coverage options ([`979ff01`](https://github.com/robinvandernoord/su6-checker/commit/979ff01afec6ea80fbfd08d53a7002b7ec68364c))
* **pytest:** Start adding pytest with tests, but WIP ([`27c5ccd`](https://github.com/robinvandernoord/su6-checker/commit/27c5ccde03173f1bef3deebc807445aed4c8f7e3))

### Documentation
* **readme:** Updated readme to include pytest and new flag order (--verbosity and --config BEFORE subcommand) ([`5db347c`](https://github.com/robinvandernoord/su6-checker/commit/5db347c4c562ad2b11a521ee11ed15c689d497b1))

## v0.4.0 (2023-05-28)
### Feature
* **config:** Add pyproject.toml settings ([`9189844`](https://github.com/robinvandernoord/su6-checker/commit/918984467e2d5eef0db0caaa134461ce73286456))
* **cli:** Allow optional argument (directory) to all commands to overwrite default ('.') behavior ([`6a767b6`](https://github.com/robinvandernoord/su6-checker/commit/6a767b60df3a358a3a356535dbe0966e413c35fe))
* **all:** Allow running `su6 all --ignore-uninstalled` so missing checking tools don't affect the final exit code of 'all' ([`b48f3e3`](https://github.com/robinvandernoord/su6-checker/commit/b48f3e345cccfc8c006901b1e0187b7cbeebc398))

### Documentation
* Fix missing . in docstrings ([`20fa1e1`](https://github.com/robinvandernoord/su6-checker/commit/20fa1e10d39d4198dfe7af5bfee662249cb1ab2e))
* **github:** Describe github action workflow yaml ([`972e5db`](https://github.com/robinvandernoord/su6-checker/commit/972e5db4e068833624891a6baa0f287971ad5a6c))
* Add todo and intentional pydocstyle error ([`5e9e987`](https://github.com/robinvandernoord/su6-checker/commit/5e9e987de5b0c4e4647ff7789129a3f5a58b2dcc))

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
