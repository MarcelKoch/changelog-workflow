#! /usr/bin/env python3
import os
import shutil
import subprocess as sp
import shlex
import sys
from typing import (List,
                    Dict, )

from pkg_resources import parse_version

DELIM = "~" * 6
GIT = "git"
HEADER = "# Release Notes"
CHANGELOG_FILE = "CHANGELOG.md"
CHANGELOG_BACKUP = f"{CHANGELOG_FILE}.bak"

next_release = sys.argv[1]


def remove_empty_strings(strings: List[str]):
    return [s for s in strings if s.strip()]


def get_current_release():
    cp = sp.run(shlex.split(f'{GIT} tag -l "v*"'), stdout=sp.PIPE, universal_newlines=True)
    tag_list = cp.stdout.splitlines()
    current_release = max(tag_list, key=lambda t: parse_version(t))
    return current_release


current_release = get_current_release()


def get_merge_commit_messages():
    cp = sp.run(shlex.split(f'{GIT} log --merges --format=format:"{DELIM}%n%b" {current_release}..HEAD'),
                stdout=sp.PIPE, universal_newlines=True)
    return remove_empty_strings(cp.stdout.split(DELIM))


messages = get_merge_commit_messages()


def extract_changelog_updates(message: str):
    _, _, release_notes = message.partition(HEADER)

    update_sections = remove_empty_strings(release_notes.split("##"))
    updates = dict()
    for sec in update_sections:
        lines = remove_empty_strings(sec.splitlines())
        updates[lines[0].strip().capitalize()] = "\n".join(lines[1:])

    return updates


def new_changelog_updates(messages: List[str]):
    changelog = dict()
    for message in messages:
        updates = extract_changelog_updates(message)
        for key, value in updates.items():
            if key in changelog:
                changelog[key] += "\n" + value
            else:
                changelog[key] = value

    return changelog


changelog = new_changelog_updates(messages)


def update_current_changelog(changelog_updates: Dict[str, str], current_version: str, next_version: str):
    with open(CHANGELOG_FILE, "r") as in_file: current_changelog = in_file.read()

    intro, current_header, current_body = current_changelog.partition(f"## {current_version[1:4]}")

    next_section = ""
    for key, value in changelog_updates.items():
        next_section += f"### {key}:\n{value}\n\n"

    new_changelog = f"""{intro.strip()}
    
## {next_version.strip()}

{next_section.strip()}

{current_header}
{current_body}"""

    return new_changelog


new_content = update_current_changelog(changelog, current_release, "1.1.0")

shutil.copy(CHANGELOG_FILE, CHANGELOG_BACKUP)
try:
    with open(CHANGELOG_FILE, "w") as out_file:
        out_file.write(new_content)
    os.remove(CHANGELOG_BACKUP)
except:
    shutil.move(CHANGELOG_BACKUP, CHANGELOG_FILE)
