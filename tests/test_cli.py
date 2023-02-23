"""Module for pytest
"""

import os
import subprocess
import tempfile

import pytest


# ===
# A basic mockup to mimic Geonetwork responses to the executions of CLI command executions
class GeonetworkMockup:
    ...


# ===
# Resources
sample_records = os.path.dirname(__file__) + "/fixtures/instance.yaml"

# ===
# CLI commands to test
MAIN_COMMAND = "soduco_geonetwork_cli"
PARSE_DOCUMENT = "parse"
UPLOAD_RECORDS = "upload"
UPDATE_RECORDS = "update"
UPDATE_POSTPONED_VALUES = "update-postponed-values"
DELETE_RECORDS = "delete"

# ===
# Test commands availability


def test_cmd_parse_document_available():
    exit_status = os.system(f'{MAIN_COMMAND} {PARSE_DOCUMENT} --help')
    assert exit_status == 0


def test_cmd_upload_records_available():
    exit_status = os.system(f'{MAIN_COMMAND} {UPLOAD_RECORDS} --help')
    assert exit_status == 0


def test_cmd_update_records_available():
    exit_status = os.system(f'{MAIN_COMMAND} {UPDATE_RECORDS} --help')
    assert exit_status == 0


def test_cmd_update_postponed_values_available():
    exit_status = os.system(f'{MAIN_COMMAND} {UPDATE_POSTPONED_VALUES} --help')
    assert exit_status == 0


def test_cmd_delete_records_available():
    exit_status = os.system(f'{MAIN_COMMAND} {DELETE_RECORDS} --help')
    assert exit_status == 0

# ===
# Command parse_document


def test_parse_document_expect_arguments():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT], check=True)


def test_parse_document_creates_nonempty_readable_tmpfile():
    odir = tempfile.gettempdir()
    subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT, sample_records,
                   "--output_folder", odir], check=True)
    yaml_file = os.getcwd() + "/yaml_list.csv"
    assert os.path.exists(yaml_file)
    assert open(yaml_file, "r", encoding='utf8').read()
