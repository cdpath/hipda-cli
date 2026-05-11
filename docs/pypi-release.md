# PyPI Release

This project publishes with GitHub Actions trusted publishing. No PyPI token is stored in GitHub secrets.

## One-time PyPI setup

Create trusted publishers for repository `cdpath/hipda-cli`.

If the project already exists on the index, add the publisher from that project's publishing settings. If the project does not exist yet, create a pending trusted publisher from the account publishing page; the first successful workflow run will create the project.

TestPyPI:

- Project: `hipda-cli`
- Owner: `cdpath`
- Repository name: `hipda-cli`
- Workflow name: `python-publish.yml`
- Environment name: `testpypi`

PyPI:

- Project: `hipda-cli`
- Owner: `cdpath`
- Repository name: `hipda-cli`
- Workflow name: `python-publish.yml`
- Environment name: `pypi`

The workflow uses GitHub environments named `testpypi` and `pypi`. Configure environment protection rules in GitHub if releases should require manual approval.

## TestPyPI rehearsal

1. Bump `version` in `pyproject.toml`.
2. Push the branch to GitHub.
3. Open Actions -> `Publish Python Package`.
4. Run the workflow manually. This publishes to TestPyPI only.
5. Verify the package:

```bash
uvx --refresh \
  --index https://test.pypi.org/simple/ \
  --default-index https://pypi.org/simple/ \
  --index-strategy unsafe-best-match \
  --from hipda-cli==<version> \
  hipda --help
```

`unsafe-best-match` is only for this TestPyPI smoke test. It lets dependencies resolve from real PyPI when TestPyPI has incomplete dependency metadata.

## PyPI release

1. Confirm the same version was tested on TestPyPI.
2. Create and publish a GitHub release.
3. The release event publishes the same package version to PyPI.
4. Verify the package:

```bash
uvx --refresh --from hipda-cli==<version> hipda --help
```

Package versions are immutable on PyPI and TestPyPI. If a publish partially succeeds, bump the version before retrying.
