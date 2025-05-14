"""
Copyright (c) Cutleast

Script to convert a plugin translation to a DSD file.
"""

from copy import copy

import json
import logging
import sys
from pathlib import Path

from plugin_interface import Plugin
from plugin_interface.plugin_string import PluginString as String


def merge_plugin_strings(
    translation_plugin: Path, original_plugin: Path
) -> list[String]:
    """
    Extracts strings from translation and original plugin and merges them.
    """

    plugin = Plugin(translation_plugin)
    translation_strings = plugin.extract_strings()

    plugin = Plugin(original_plugin)
    original_strings = {
        f"{string.form_id.lower()}###{string.editor_id}###{string.type}###{string.index}": string
        for string in plugin.extract_strings()
    }

    log.debug(
        f"Merging {len(original_strings)} original String(s) to {len(translation_strings)} translated String(s)..."
    )

    merged_strings: list[String] = []

    skipped_strings = 0

    for translation_string in translation_strings:
        original_string = original_strings.get(
            f"{translation_string.form_id.lower()}###{translation_string.editor_id}###{translation_string.type}###{translation_string.index}"
        )

        if original_string is None:
            log.warning(f"Not found in Original: {translation_string}")
            continue
        elif original_string.original_string == translation_string.original_string:
            skipped_strings += 1
            continue

        translation_string = copy(translation_string)
        translation_string.translated_string = translation_string.original_string
        translation_string.original_string = original_string.original_string
        translation_string.status = String.Status.TranslationComplete
        merged_strings.append(translation_string)

    log.warning(f"Skipped {skipped_strings} duplicate/untranslated String(s)!")
    log.debug(f"Merged {len(merged_strings)} String(s).")

    return merged_strings


# Init logger
log_fmt = "[%(asctime)s.%(msecs)03d][%(levelname)s][%(name)s.%(funcName)s]: %(message)s"
root_logger = logging.getLogger()
root_logger.setLevel("DEBUG")
formatter = logging.Formatter(log_fmt, datefmt="%d.%m.%Y %H:%M:%S")
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(formatter)
root_logger.addHandler(log_handler)

log = logging.getLogger("Converter")

sys.argv.pop(0)  # Remove script itself from commandline arguments

if len(sys.argv) != 2:
    print(
        "Wrong syntax! Syntax: esp2dsd.exe <path to original plugin> <path to translated/edited plugin>\n"
        + "Or alternatively: esp2dsd.exe <path to folder with original plugins> <path to folder with translated plugins>"
    )
    sys.exit(1)

original_path = Path(sys.argv[0])
translation_path = Path(sys.argv[1])

if original_path.is_file() and translation_path.is_file():
    original_plugins = [original_path]
    translation_path = translation_path.parent
elif original_path.is_dir() and translation_path.is_dir():
    original_plugins = [
        file
        for suffix in ["*.esl", "*.esm", "*.esp"]
        for file in original_path.glob(suffix)
    ]

for p, original_plugin in enumerate(original_plugins):
    translation_plugin = translation_path / original_plugin.name

    if not translation_plugin.is_file():
        log.error(
            f"Failed to convert {original_plugin.name!r}: No matching plugin found in {str(translation_path)!r}!"
        )
        continue

    log.info(f"Processing {original_plugin.name!r} ({p+1}/{len(original_plugins)})...")

    strings = merge_plugin_strings(translation_plugin, original_plugin)

    output_path = (
        Path("Output") / f"{original_plugin.stem}_output{original_plugin.suffix}.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    log.info(f"Writing to {str(output_path)!r}...")

    string_data = [string.to_string_data() for string in strings]

    with output_path.open("w", encoding="utf8") as output_file:
        json.dump(string_data, output_file, ensure_ascii=False, indent=4)

    log.info(f"Written {len(strings)} string(s) to {str(output_path)!r}.")

sys.exit(0)
