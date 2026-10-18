#!/usr/bin/env bash
# Decide whether this CI run publishes a release (used by the release job).
# Outputs (to $GITHUB_OUTPUT, or stdout when unset): version, publish, create.
#   tag push      -> publish the tag, which must equal the pyproject.toml version
#   master push   -> publish and create the tag/release when the version has
#                    .github/release-notes/<version>.md and no tag yet
#   anything else -> nothing to publish
set -euo pipefail
out="${GITHUB_OUTPUT:-/dev/stdout}"
version=$(sed -n 's/^version = "\(.*\)"$/\1/p' pyproject.toml | head -n 1)
publish=false
create=false
case "${GITHUB_REF:-}" in
  refs/tags/*)
    if [ "${GITHUB_REF_NAME}" != "$version" ]; then
      echo "::error::tag ${GITHUB_REF_NAME} does not match pyproject.toml version $version"
      exit 1
    fi
    publish=true
    ;;
  refs/heads/master)
    if [ ! -f ".github/release-notes/$version.md" ]; then
      echo "No .github/release-notes/$version.md: nothing to release."
    elif gh api "repos/${GITHUB_REPOSITORY}/git/ref/tags/$version" >/dev/null 2>&1; then
      echo "Tag $version already exists: nothing to release."
    else
      publish=true
      create=true
    fi
    ;;
esac
echo "Release plan: version=$version publish=$publish create=$create"
{ echo "version=$version"; echo "publish=$publish"; echo "create=$create"; } >> "$out"
