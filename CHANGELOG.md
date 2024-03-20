# Changelog

<!--next-version-placeholder-->

## v1.8.3 (2024-03-20)

### Fix

* Try to find executables via `python -m` as a fallback, e.g. when installed via pipx ([`5174ac0`](https://github.com/robinvandernoord/su6-checker/commit/5174ac0b46c26e7db0f1f29194e71603195234ce))

## v1.8.2 (2024-03-04)

### Fix

* `su6 list` now also shows yellow circles for uninstalled tools ([`518ed84`](https://github.com/robinvandernoord/su6-checker/commit/518ed84583936ea8875b75df74e0c9bcca3389c2))

## v1.8.1 (2024-02-28)

### Fix

* Pytest --convention option (also via config) ([`b1669ac`](https://github.com/robinvandernoord/su6-checker/commit/b1669ac40448ce93707025daeea3a41f1a3e2522))

## v1.8.0 (2023-10-09)

### Feature

* **config:** You can now add [tool.su6.default-flags] for each tool ([`d8c8034`](https://github.com/robinvandernoord/su6-checker/commit/d8c8034ccd39d572843f532b4b97ae8e48562dd7))

### Documentation

* **readme:** Fixed toc ([`28ca2b4`](https://github.com/robinvandernoord/su6-checker/commit/28ca2b466e16de68d3a312a7290572583668fa05))

## v1.7.0 (2023-09-28)

### Feature

* Allow --exclude for `all` and `fix` to skip specific checkers ([`27dd5b3`](https://github.com/robinvandernoord/su6-checker/commit/27dd5b3bffe8553c986a1dc574a8f72ca57233f1))

## v1.6.4 (2023-07-21)

### Refactor

* refactor: moved pyproject logic to configuraptor and bumped dependency version

## v1.6.3 (2023-07-17)

### Documentation

* **plugins:** Added `prettier`
  extra ([`f1f0d34`](https://github.com/robinvandernoord/su6-checker/commit/f1f0d3402bc5b8eb5ffc6eceedce6ef83ba30141))

## v1.6.2 (2023-07-17)

### Feature

* Add su6[svelte-check] as
  extra ([`558a2be`](https://github.com/robinvandernoord/su6-checker/commit/558a2bee214f5294e8193765d5a4566a85afdc6f))

## v1.6.1 (2023-07-17)

### Fix

* **tool:** Don't show full executable path in output, only tool
  name ([`2ec226f`](https://github.com/robinvandernoord/su6-checker/commit/2ec226f62349c048221a056d2b504e38048c5706))

## v1.6.0 (2023-07-17)

### Feature

* Allow `add_to_all` and `add_to_fix` to plugin
  registration ([`f0c501b`](https://github.com/robinvandernoord/su6-checker/commit/f0c501b76c9e8baad37178f45ec83fd23f91d446))

### Documentation

* **plugins:** Added more info about `add_to_*` and the svelte-check
  plugin ([`3e0051c`](https://github.com/robinvandernoord/su6-checker/commit/3e0051c968f97883ef7dc7859bdf5b3138753c73))
* **pypi:** Indicate 3.10
  support ([`a547da0`](https://github.com/robinvandernoord/su6-checker/commit/a547da0783cfccfa058b780bcdbe8130e9cf3e62))

## v1.5.2 (2023-06-21)

## v1.5.1 (2023-06-20)

### Documentation

* **logo:** Use png instead of svg because that was being
  funky ([`89d71a5`](https://github.com/robinvandernoord/su6-checker/commit/89d71a59a74f046f5daa5da2180505676b273318))
* **changelog:** Manually added change for
  1.5.0 ([`3713a6b`](https://github.com/robinvandernoord/su6-checker/commit/3713a6bc61ef2eaa930721f7a7e6caa9cbbefe22))

## v1.5.0 (2023-06-20)

### Feature

* Support Python 3.10

## v1.4.3 (2023-06-19)

### Documentation

* Moved to
  trialandsuccess/su6 ([`d34de14`](https://github.com/robinvandernoord/su6-checker/commit/d34de14100ee2b52f986488179fc37e5f40ec839))

## v1.4.2 (2023-06-19)

### Documentation

* **readme:** Fix icon to master
  branch ([`d2e3a7c`](https://github.com/trialandsuccess/su6/commit/d2e3a7c7dfa87236ad42e00074b46f5e4a30378f))
* **readme:** Add
  icon ([`640c383`](https://github.com/trialandsuccess/su6/commit/640c38318e579222a1ce641bf46c8c541a421bad))

## v1.4.1 (2023-06-19)

### Fix

* **config:** Use .update functionality
  from `configuraptor`. ([`aa09931`](https://github.com/trialandsuccess/su6/commit/aa0993167e42d878689723a9d337bdc244082914))

## v1.4.0 (2023-06-15)

### Feature

* **json:** Allow json-indent via tool
  config ([`f4f353c`](https://github.com/trialandsuccess/su6/commit/f4f353cab028cdc37707051f4be829d4f1426fb0))

## v1.3.2 (2023-06-15)

### Fix

* **json:** Indent for easier
  reading ([`077f900`](https://github.com/trialandsuccess/su6/commit/077f9005b1bf922ed69843b91f87106f4839bca4))

## v1.3.1 (2023-06-15)

### Fix

* **dep:** Bump configuraptor required
  version ([`fc39b57`](https://github.com/trialandsuccess/su6/commit/fc39b573a35d3cd96c423139fcc73b27559eb18d))

## v1.3.0 (2023-06-15)

### Feature

* **config:** Started
  using `configuraptor` ([`533dfa2`](https://github.com/trialandsuccess/su6/commit/533dfa2cc5702c5c9740ac32c04db9c1ea3804b1))

## v1.2.1 (2023-06-13)

### Fix

* **pytest:** Test doesn't depend on demo plugin
  anymore ([`0051514`](https://github.com/trialandsuccess/su6/commit/005151456203915085200f530153f191eb7f8608))

### Documentation

* **plugins:** Link to template and demo
  repo. ([`40088ca`](https://github.com/trialandsuccess/su6/commit/40088cac73c5c6417188283604f074d74fc399b1))

## v1.2.0 (2023-06-08)

### Feature

* **config:** `allow_none` in Config.update and @register(strict=False) for Plugin
  Config ([`3ef40ae`](https://github.com/trialandsuccess/su6/commit/3ef40ae6d4ed2cb88ef36863f9b6a1a98d63deb1))

### Documentation

* **plugins:** Started describing plugin
  config ([`500a525`](https://github.com/trialandsuccess/su6/commit/500a525143fc51332454826431c6c69f641cff18))

## v1.1.0 (2023-06-06)

### Feature

* **plugin:** Change command registration system and allow config; coverage is still
  low ([`1124a9c`](https://github.com/trialandsuccess/su6/commit/1124a9cbf5a2deb5b451b06bed8169874560f162))
* **plugin:** WIP to add plugin-specific
  config ([`24c2456`](https://github.com/trialandsuccess/su6/commit/24c2456bf2fc2bd5aeb7602467aadfb0d9241b92))

### Documentation

* **badge:** Pinned su6 checks gh action badge to specific branch instead of latest
  check ([`a4e525b`](https://github.com/trialandsuccess/su6/commit/a4e525be4477319c2bfad7eb9864241fadfdf7f9))

## v1.0.0 (2023-06-05)

### Feature

* **plugins:** Allow third party
  plugins ([`5ba672a`](https://github.com/trialandsuccess/su6/commit/5ba672a40b893488dd593c88ed5ea9245cc66d95))

### Fix

* **plugins:** Expose run_tool externally for use in
  plugins ([`9c05af0`](https://github.com/trialandsuccess/su6/commit/9c05af035a309a9205d96b7038f203d40f500097))
* **plugins:** Proper mypy return
  types ([`a3f2f2e`](https://github.com/trialandsuccess/su6/commit/a3f2f2ecb0a5cdb717582d7dd28b2c64b9f3e913))

### Documentation

* **plugins:** Show usage example of making a
  checker ([`b02e981`](https://github.com/trialandsuccess/su6/commit/b02e981fc112795e90a59d5ee6dc7ddfa6f63ed5))

## v0.9.0 (2023-06-01)

### Feature

* **all:** Add `stop-after-first-failure` flag to `all` and pyproject
  toml ([`906678a`](https://github.com/trialandsuccess/su6/commit/906678a344aa68a2ef2101f9765dc1e601d5d5dd))
* **config:** 'include' can now also specify the order of checks to run in '
  all' ([`6f9123b`](https://github.com/trialandsuccess/su6/commit/6f9123b1869c15342bbc7e4d7cfb39f2fbb181bb))

### Documentation

* **README:** Better example for gh
  actions ([`73fa545`](https://github.com/trialandsuccess/su6/commit/73fa5451ec0b0c7897eaa505c931f3af991a3a5d))

## v0.8.0 (2023-05-31)

### Feature

* **su6:** Add --version and
  self-update ([`084cd51`](https://github.com/trialandsuccess/su6/commit/084cd51b066d8d055b62556567b02e8e0a39c5fe))

## v0.7.2 (2023-05-31)

### Fix

* **mypy:** Ensure config.badge is a string/path, not a
  bool ([`2c29b57`](https://github.com/trialandsuccess/su6/commit/2c29b57a3c0502a7377941f0b48bc569aacc5d63))

## v0.7.1 (2023-05-31)

## v0.7.0 (2023-05-30)

### Feature

* **cov:** Add support for coverage svg badge to
  pytest ([`ee6c29c`](https://github.com/trialandsuccess/su6/commit/ee6c29c2d16d379d7d4a09f97a6c6fb29943d513))

### Fix

* **cov:** 100% coverage again (and check for
  it) ([`c162e0d`](https://github.com/trialandsuccess/su6/commit/c162e0d8b86782dfdc8c7e540a5f73f939cc1fa2))

## v0.6.0 (2023-05-30)

### Feature

* **format:**
  Allow `--format json` ([`3c958e5`](https://github.com/trialandsuccess/su6/commit/3c958e5bb8dbfb79f76d3614385c062286429af4))

### Fix

* **json:** Format=json did not actually output json... Also update
  tests ([`df5fd41`](https://github.com/trialandsuccess/su6/commit/df5fd411b8336e046165c6893777ed9abf539ae0))

### Documentation

* **format:**
  Allow `--format json` ([`29c5d0b`](https://github.com/trialandsuccess/su6/commit/29c5d0b85e7e2c2bed2f6067ae0477e91256e8fc))

## v0.5.3 (2023-05-30)

### Fix

* **mypy:** Stricter rules regarding None ( but still allow implicit in function
  args >:( ) ([`46ff1d4`](https://github.com/trialandsuccess/su6/commit/46ff1d4850074045c20f19d7135bb95d200a835b))

## v0.5.2 (2023-05-30)

### Documentation

* **readme:** Add supported args for each checker in '
  use' ([`c091d2b`](https://github.com/trialandsuccess/su6/commit/c091d2b21fa90ee0f2383d9bb101c327b0fd8036))

## v0.5.1 (2023-05-30)

### Fix

* **cov:** Forgot to add pytest-cov as dependency for '
  all' ([`fef9b41`](https://github.com/trialandsuccess/su6/commit/fef9b41543ecce11b8f157be8e7a5c5f59d6f248))

## v0.5.0 (2023-05-30)

### Feature

* **pytest:** Add pytest with coverage
  options ([`979ff01`](https://github.com/trialandsuccess/su6/commit/979ff01afec6ea80fbfd08d53a7002b7ec68364c))
* **pytest:** Start adding pytest with tests, but
  WIP ([`27c5ccd`](https://github.com/trialandsuccess/su6/commit/27c5ccde03173f1bef3deebc807445aed4c8f7e3))

### Documentation

* **readme:** Updated readme to include pytest and new flag order (--verbosity and --config BEFORE
  subcommand) ([`5db347c`](https://github.com/trialandsuccess/su6/commit/5db347c4c562ad2b11a521ee11ed15c689d497b1))

## v0.4.0 (2023-05-28)

### Feature

* **config:** Add pyproject.toml
  settings ([`9189844`](https://github.com/trialandsuccess/su6/commit/918984467e2d5eef0db0caaa134461ce73286456))
* **cli:** Allow optional argument (directory) to all commands to overwrite default ('.')
  behavior ([`6a767b6`](https://github.com/trialandsuccess/su6/commit/6a767b60df3a358a3a356535dbe0966e413c35fe))
* **all:** Allow running `su6 all --ignore-uninstalled` so missing checking tools don't affect the final exit code of '
  all' ([`b48f3e3`](https://github.com/trialandsuccess/su6/commit/b48f3e345cccfc8c006901b1e0187b7cbeebc398))

### Documentation

* Fix missing . in
  docstrings ([`20fa1e1`](https://github.com/trialandsuccess/su6/commit/20fa1e10d39d4198dfe7af5bfee662249cb1ab2e))
* **github:** Describe github action workflow
  yaml ([`972e5db`](https://github.com/trialandsuccess/su6/commit/972e5db4e068833624891a6baa0f287971ad5a6c))
* Add todo and intentional pydocstyle
  error ([`5e9e987`](https://github.com/trialandsuccess/su6/commit/5e9e987de5b0c4e4647ff7789129a3f5a58b2dcc))

## v0.3.0 (2023-05-28)

### Feature

* **all:** Allow running `su6 all --ignore-uninstalled` so missing checking tools don't affect the final exit code of '
  all' ([`35ad498`](https://github.com/trialandsuccess/su6/commit/35ad498983bd651d66bfa3e773b9a1e1e7d94e6c))
* **pydocstyle:** Added docstring checker (and
  docstrings) ([`4ad2c29`](https://github.com/trialandsuccess/su6/commit/4ad2c29c88a840dd01640a8d9bcf4695834e37a5))

### Documentation

* **readme:** Added list of supported
  tools ([`02fb7a8`](https://github.com/trialandsuccess/su6/commit/02fb7a86673f64e4ab937b6f5a7b45543ab86aa1))

## v0.2.1 (2023-05-27)

### Fix

* **exit codes:** They now actually
  work™ ([`503c69c`](https://github.com/trialandsuccess/su6/commit/503c69ccf5d4d91847fd4f0580511d6a89800fd6))

## v0.2.0 (2023-05-27)

### Feature

* **shell:** Introduce @with_exit_code decorator to generate an exit code based on the return value of a command
  method ([`7d6d4e2`](https://github.com/trialandsuccess/su6/commit/7d6d4e27c2226538b79f63b972c90045517cbe46))

### Fix

* **log:** First show status and then show any output, this works less confusing
  IMO ([`176966d`](https://github.com/trialandsuccess/su6/commit/176966df86383887ac837c35de1d423c1ca03546))

## v0.1.3 (2023-05-27)

### Fix

* **namespace:** Moved everything to 'su6' so the hatch build succeeds (it's
  late...) ([`e87aed9`](https://github.com/trialandsuccess/su6/commit/e87aed9660449560256e32178e730157a153bb47))

## v0.1.2 (2023-05-27)

### Documentation

* **README:** Actually fixed the badges and added link to
  changelog ([`aabbc39`](https://github.com/trialandsuccess/su6/commit/aabbc39a5bfccf05248b8d21c105fc758befa240))

## v0.1.1 (2023-05-27)

### Documentation

* **readme:** Started on the readme, more to follow when it's not almost 2
  am ([`5ccfe62`](https://github.com/trialandsuccess/su6/commit/5ccfe6232a58776dcee3c1a969a07711d479f0e3))
* **changelog:** Manually added
  0.1 ([`35d9b3b`](https://github.com/trialandsuccess/su6/commit/35d9b3b1caedad64e4b68d40b1567fa154bad249))

## v0.1.0 (2023-05-27)

*Feature*: Initial Version 🎉
