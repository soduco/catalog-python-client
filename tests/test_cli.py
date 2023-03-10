"""Module for pytest
"""

import csv
import os
import subprocess
from importlib import import_module
from unittest.mock import patch

import soduco_geonetwork

import pytest
from cli_test_helpers import ArgvContext, EnvironContext


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

# Doesn't build like this here, see next function
# def test_main_module():
#     """
#     Exercise (most of) the code in the ``__main__`` module.
#     """
#     import_module('soduco_geonetwork.__main__')


def test_main_module():
    """
    Exercise (most of) the code in the ``__main__`` module.
    """
    import_module('soduco_geonetwork.cli')


def test_runas_module():
    """Can this package be run as a Python module?"""
    result = os.system('python -m soduco_geonetwork.cli.cli --help')
    assert result == 0


def test_entrypoint():
    """Is entrypoint script installed with poetry? """
    result = os.system('soduco_geonetwork_cli --help')
    assert result == 0


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


@patch('soduco_geonetwork.cli.cli.cli')
def test_cli_command(mock_command):
    """
    Is the correct code called when invoked via the CLI?
    """
    with ArgvContext('soduco_geonetwork', 'parse'), pytest.raises(SystemExit):
        soduco_geonetwork.cli.cli.cli()

    assert mock_command.called


def test_fail_without_secret():
    """
    Must fail without a ``SECRET`` environment variable specified
    """
    message_regex = "Environment value SECRET not set."

    with EnvironContext(SECRET=None):
        with pytest.raises(SystemExit, match=message_regex):
            soduco_geonetwork.cli.cli.cli()
            pytest.fail("CLI doesn't abort with missing SECRET")


# ===
# Command parse_document


def test_parse_document_expect_arguments():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT], check=True)


def test_parse_document_creates_nonempty_readable_tmpfile_in_current_folder():
    subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT, sample_records], check=True)
    csv_file = os.getcwd() + "/yaml_list.csv"
    assert os.path.exists(csv_file)
    assert open(csv_file, "r", encoding='utf8').read()
    os.unlink(csv_file)

def test_parse_documents_creates_xml_files_at_tmp_folder():
    current_folder = os.getcwd()
    subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT, sample_records], check=True)
    csv_file = f"{current_folder}/yaml_list.csv"
    assert os.path.exists(csv_file)

    main_file = open(csv_file, "r", encoding='utf8')
    reader = csv.DictReader(main_file)

    for row in reader:
        xml_file = row["xml_file_path"]
        assert open(xml_file, "r", encoding='utf8').read()

    os.unlink(csv_file)

def test_parse_documents_creates_xml_files_at_output_folder():
    current_folder = os.getcwd()
    output_folder = f"{current_folder}/tmp"
    subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT, sample_records,
                    "--output_folder", output_folder], check=True)
    csv_file = f"{current_folder}/yaml_list.csv"
    assert os.path.exists(csv_file)

    main_file = open(csv_file, "r", encoding='utf8')
    reader = csv.DictReader(main_file)

    for row in reader:
        xml_file = row["xml_file_path"]
        assert open(xml_file, "r", encoding='utf8').read()
        os.unlink(xml_file)

    os.rmdir(output_folder)
    os.unlink(csv_file)

def test_parse_documents_raise_exception_on_bad_file_format():
    wrong_input_file = 'csv_file.csv'
    open(wrong_input_file, 'a', encoding="utf8").close()

    with pytest.raises(ValueError, match=r".*yaml file.*"):
        subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT, wrong_input_file], check=True)

    os.unlink(wrong_input_file)
