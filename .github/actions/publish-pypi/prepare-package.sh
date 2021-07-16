#!/bin/bash -ex

if [ "$1" = "--help" ] ; then
  echo "Usage: $0 <path-to-repo-folder> <main-module-name> <release-version-dotted>"
  exit 0
fi

repo="$1"
module_name="$2"
version_dotted="$3"

BUMP_SH_SCRIPT="bump_version.sh"
GENERATE_MANIFEST_SCRIPT="generate_manifest.sh"

pushd $repo

echo -e "\nSetting version to $version_dotted"
bash -ex $BUMP_SH_SCRIPT $version_dotted
cat $module_name/__version__.json

echo -e "\nGenerating manifest"
bash -ex $GENERATE_MANIFEST_SCRIPT
cat $module_name/__manifest__.json

popd

echo -e "\nFinished preparing $repo for publishing\n"
