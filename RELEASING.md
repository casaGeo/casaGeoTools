# Releasing

1. Run `./Taskfile run-checks` and `./Taskfile run-tests` and fix any
   outstanding issues. Commit your changes as appropriate.
2. Run `./Taskfile build` and `./Taskfile build-docs` and fix any
   outstanding issues. Commit your changes as appropriate.
3. Update copyright notices of all files that have changed since the last
   release to include the current year. Commit this change as
   `Update copyright notices for year YYYY`.
4. Move the contents of the "Next Release" section in `CHANGELOG.md` into a new
   section describing version X.Y.Z and update that section as appropriate.
   Commit this change as `Update CHANGELOG.md for version X.Y.Z`.
5. Run `uv version X.Y.Z` to update the version number in `pyproject.toml` and
   `uv.lock`. Update the version numbers in `docs/conf.py` by hand to match.
   Confirm this change by running `./Taskfile run-version-tests` and commit it
   as `Bump version to X.Y.Z`.
6. Push the commits using `git push` and check for any CI failures. Fix any
   issues and commit your changes as appropriate, then redo this step.
7. Tag the release using `git tag -a vX.Y.Z`.
8. Push the release using `git push --follow-tags`.
9. Check for any CI failures and recreate the release if necessary.
