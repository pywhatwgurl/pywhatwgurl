#!/usr/bin/env python3
import argparse
import json
import logging
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import pathlib
from typing import Iterable, List, Mapping, MutableMapping, Sequence, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CHUNK_SIZE = 8192
DEFAULT_WPT_COMMIT = "c928b19ab04a4525807238e9299c23f3a1cca582"
BASE_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/web-platform-tests/wpt/{commit}/url/"
)
DEFAULT_RESOURCES = [
    "resources/urltestdata.json",
    "resources/setters_tests.json",
    "resources/percent-encoding.json",
    "resources/toascii.json",
    "resources/IdnaTestV2.json",
    "resources/IdnaTestV2-removed.json",
]
META_FILE_NAME = "wpt_url_test_data_meta.json"

UrlTestEntry = Union[str, Mapping[str, object]]
PercentEncodingEntry = Union[str, Mapping[str, object]]


def _cmd_download(args):
    try:
        fetch_wpt_test_data(
            dest_dir=args.dest_dir,
            commit=args.commit,
            resources=args.resources,
            base_url_template=args.base_url_template,
        )
    except Exception:
        raise
        sys.exit(1)
    else:
        sys.exit(0)


def fetch_wpt_test_data(
    dest_dir: str,
    commit: str = DEFAULT_WPT_COMMIT,
    resources: Iterable[str] = DEFAULT_RESOURCES,
    base_url_template: str = BASE_URL_TEMPLATE,
) -> None:
    """Download and validate the WPT URL JSON resources pinned to a commit."""
    dest_dir_path = pathlib.Path(dest_dir)

    if not os.path.isdir(dest_dir_path):
        try:
            os.makedirs(dest_dir_path, exist_ok=True)
            logger.debug("Created destination directory %s", dest_dir_path)
        except PermissionError:
            logger.error("Cannot create directory: %s", dest_dir_path)
            raise

    resources = list(resources)
    base_url = base_url_template.format(commit=commit)
    download_plan = {
        pathlib.Path(resource).name: _join_url(base_url, resource)
        for resource in resources
    }

    downloaded = {}
    for filename, resource_url in download_plan.items():
        downloaded[filename] = _download_and_validate(
            resource_url, dest_dir_path, filename
        )

    _write_metadata(dest_dir_path, base_url, commit, list(downloaded.keys()))


def _join_url(base: str, resource: str) -> str:
    base_with_trailing = base if base.endswith("/") else base + "/"
    return urllib.parse.urljoin(base_with_trailing, resource)


def _download_and_validate(url: str, dest_dir: pathlib.Path, filename: str) -> str:
    dest_dir = pathlib.Path(dest_dir)

    try:
        raw_fd, raw_path = tempfile.mkstemp(dir=dest_dir, suffix=".raw")
        os.close(raw_fd)
        logger.info("Downloading %s to temporary file", url)
        with urllib.request.urlopen(url) as response, open(raw_path, "wb") as out_file:  # noqa: S310
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                out_file.write(chunk)
    except urllib.error.HTTPError as e:
        if os.path.exists(raw_path):
            os.remove(raw_path)
        logger.error("HTTP error %s when downloading %s", e.code, url)
        raise
    except urllib.error.URLError as e:
        if os.path.exists(raw_path):
            os.remove(raw_path)
        logger.error("URL error when downloading %s: %s", url, e)
        raise
    except Exception:
        if os.path.exists(raw_path):
            os.remove(raw_path)
        logger.exception("Failed to download %s", url)
        raise

    try:
        with open(raw_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug(
            "Loaded raw JSON for %s, %d entries",
            filename,
            len(data) if isinstance(data, list) else 0,
        )
    except json.JSONDecodeError as e:
        os.remove(raw_path)
        logger.error("Failed to decode JSON from %s: %s", url, e)
        raise
    except Exception:
        os.remove(raw_path)
        logger.exception("Could not read downloaded file %s", raw_path)
        raise

    _validate_resource(filename, data)

    try:
        san_fd, san_path = tempfile.mkstemp(dir=dest_dir, suffix=".json")
        os.close(san_fd)
    except Exception as e:
        os.remove(raw_path)
        logger.error("Could not create temp file for sanitized JSON: %s", e)
        raise

    try:
        with open(san_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=True)
        logger.debug("Wrote validated JSON for %s to temporary file", filename)
    except Exception as e:
        os.remove(raw_path)
        os.remove(san_path)
        logger.error("Could not write validated JSON: %s", e)
        raise

    os.remove(raw_path)
    logger.debug("Removed raw temporary file")

    final_path = dest_dir / filename
    try:
        os.replace(san_path, final_path)
        logger.info("Downloaded, validated, and saved to: %s", final_path)
    except Exception as e:
        os.remove(san_path)
        logger.error("Could not rename sanitized file to '%s': %s", final_path, e)
        raise

    return str(final_path)


def _validate_resource(filename: str, data: object) -> None:
    if filename in ("urltestdata.json", "urltestdata-javascript-only.json"):
        _validate_urltestdata(data, filename)
    elif filename == "percent-encoding.json":
        _validate_percent_encoding(data)
    elif filename == "toascii.json":
        _validate_toascii(data)
    elif filename == "setters_tests.json":
        _validate_setters_tests(data)
    elif filename in ("IdnaTestV2.json", "IdnaTestV2-removed.json"):
        _validate_idna(data, filename)
    else:
        logger.warning("No validator registered for %s; skipping validation", filename)


def _validate_urltestdata(data: object, filename: str) -> None:
    if not isinstance(data, list):
        raise ValueError(f"{filename} should be a list; got {type(data).__name__}")

    allowed_keys = {
        "input",
        "base",
        "href",
        "origin",
        "protocol",
        "username",
        "password",
        "host",
        "hostname",
        "port",
        "pathname",
        "search",
        "hash",
        "searchParams",
        "failure",
        "relativeTo",
        "comment",
    }
    for entry in data:
        if isinstance(entry, str):
            continue
        if not isinstance(entry, MutableMapping):
            raise ValueError(f"Unexpected entry type in {filename}: {type(entry)}")
        missing = {"input", "base"} - entry.keys()
        if missing:
            raise ValueError(f"Missing required keys {missing} in {filename}")
        extra_keys = set(entry.keys()) - allowed_keys
        if extra_keys:
            raise ValueError(f"Unknown keys {extra_keys} in {filename}")
        if "failure" in entry and entry["failure"] not in (True, False):
            raise ValueError(f"'failure' must be boolean in {filename}")
        if "relativeTo" in entry and entry["relativeTo"] not in (
            "non-opaque-path-base",
            "any-base",
        ):
            raise ValueError(f"Unexpected relativeTo value in {filename}")
        if "href" not in entry and not entry.get("failure") and "relativeTo" not in entry:
            logger.warning(
                "Entry without href/failure/relativeTo found in %s; schema may have changed",
                filename,
            )


def _validate_percent_encoding(data: object) -> None:
    if not isinstance(data, list):
        raise ValueError("percent-encoding.json should be a list")
    for entry in data:
        if isinstance(entry, str):
            continue
        if not isinstance(entry, MutableMapping):
            raise ValueError("Invalid entry type in percent-encoding.json")
        if "input" not in entry or "output" not in entry:
            raise ValueError("Missing keys in percent-encoding.json entry")


def _validate_toascii(data: object) -> None:
    if not isinstance(data, list):
        raise ValueError("toascii.json should be a list")
    for entry in data:
        if isinstance(entry, str):
            continue
        if not isinstance(entry, MutableMapping):
            raise ValueError("Invalid entry type in toascii.json")
        if "input" not in entry or "output" not in entry:
            raise ValueError("Missing keys in toascii.json entry")


def _validate_setters_tests(data: object) -> None:
    if not isinstance(data, MutableMapping):
        raise ValueError("setters_tests.json should be an object at the top level")
    for key, value in data.items():
        if key == "comment":
            continue
        if not isinstance(value, Sequence):
            raise ValueError(f"Expected list of cases for {key} in setters_tests.json")


def _validate_idna(data: object, filename: str) -> None:
    if not isinstance(data, list):
        raise ValueError(f"{filename} should be a list")
    for entry in data:
        if isinstance(entry, str):
            continue
        if not isinstance(entry, MutableMapping):
            raise ValueError(f"Invalid entry type in {filename}")
        if "input" not in entry or "output" not in entry:
            raise ValueError(f"Missing keys in {filename} entry")


def _write_metadata(dest_dir: pathlib.Path, base_url: str, commit: str, filenames: List[str]) -> None:
    meta_path = dest_dir / META_FILE_NAME
    data = {
        "wpt_base_url": base_url,
        "wpt_commit": commit,
        "resources": sorted(filenames),
    }
    meta_tmp_fd, meta_tmp_path = tempfile.mkstemp(dir=dest_dir, suffix=".meta")
    os.close(meta_tmp_fd)
    try:
        with open(meta_tmp_path, "w", encoding="utf-8") as meta_file:
            json.dump(data, meta_file, indent=2, ensure_ascii=False)
        os.replace(meta_tmp_path, meta_path)
        logger.info("Wrote metadata to %s", meta_path)
    finally:
        if os.path.exists(meta_tmp_path):
            os.remove(meta_tmp_path)


def main():
    parser = argparse.ArgumentParser(
        description="Utility for downloading wpt url test data."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_download = subparsers.add_parser(
        "download", help="Download and validate WPT URL test data."
    )
    parser_download.add_argument(
        "--dest_dir", type=str, required=True, help="Directory in which to save the files"
    )
    parser_download.add_argument(
        "--commit",
        type=str,
        default=DEFAULT_WPT_COMMIT,
        help="WPT commit hash to fetch from",
    )
    parser_download.add_argument(
        "--resources",
        nargs="+",
        default=DEFAULT_RESOURCES,
        help="List of URL resource paths (relative to /url/) to download",
    )
    parser_download.add_argument(
        "--base_url_template",
        type=str,
        default=BASE_URL_TEMPLATE,
        help="Template URL used to build download URLs (must include {commit})",
    )
    parser_download.set_defaults(func=_cmd_download)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()


__all__ = ["fetch_wpt_test_data"]
