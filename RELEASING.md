# Releasing

1. Run `./Taskfile run-checks` and `./Taskfile run-tests` and fix any
   outstanding issues. Commit your changes as appropriate.
2. Update copyright notices of all files that have changed since the last
   release to include the current year. Commit this change as
   `Update copyright notices for year YYYY`.
3. Run `uv bump X.Y.Z` to update the version number in `pyproject.toml` and
   `uv.lock`. Update the version numbers in `docs/conf.py` by hand to match.
   Confirm this change by running `./Taskfile run-version-tests` and commit it
   as `Bump version to X.Y.Z`.
4. Move the contents of the "Next Release" section in `CHANGELOG.md` into a new
   section describing version X.Y.Z and update that section as appropriate.
   Commit this change as `Update CHANGELOG.md for version X.Y.Z`.
5. Tag the release using `git tag -a vX.Y.Z`.
6. Push the release using `git push --follow-tags`.
7. Check for any CI failures and recreate the release if necessary.
