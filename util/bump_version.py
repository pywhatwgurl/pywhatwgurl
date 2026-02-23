import argparse
import subprocess
import re

def get_latest_tag():
    """Retrieve the latest semver tag from the git repository."""
    try:
        # Get all tags sorted by creation date
        tags = subprocess.check_output(["git", "tag", "--sort=-creatordate"], text=True).splitlines()  # noqa: S607
        for tag in tags:
            # Look for tags like v0.1.0 or 0.1.0
            if re.match(r"^v?\d+\.\d+\.\d+$", tag):
                return tag
    except subprocess.CalledProcessError:
        pass
    return None

def bump_version(current_version, rule):
    """Bump a semver version string according to the given rule."""
    # Normalize version (remove v if present)
    version_str = current_version.lstrip("v")
    major, minor, patch = map(int, version_str.split("."))

    if rule == "major":
        major += 1
        minor = 0
        patch = 0
    elif rule == "minor":
        minor += 1
        patch = 0
    elif rule == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump rule: {rule}")

    return f"v{major}.{minor}.{patch}"

def main():
    """CLI entrypoint for bumping the project version based on the latest git tag."""
    parser = argparse.ArgumentParser(description="Bump version based on latest git tag")
    parser.add_argument("rule", choices=["major", "minor", "patch"], help="Bump rule")
    args = parser.parse_args()

    latest_tag = get_latest_tag()
    if not latest_tag:
        # Default starting version if no tags
        new_version = "v0.1.0"
        print(f"No existing tags found. Starting with {new_version}")
    else:
        new_version = bump_version(latest_tag, args.rule)
        print(f"Bumping {latest_tag} -> {new_version}")

    # Set output for GitHub Actions
    print(f"NEW_TAG={new_version}")
    # Write to GITHUB_OUTPUT if available
    if "GITHUB_OUTPUT" in subprocess.os.environ:
        with open(subprocess.os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"new_tag={new_version}\n")

if __name__ == "__main__":
    main()
