"""Module for pytest
"""

import csv
import os
import subprocess
from importlib import import_module

import soduco_geonetwork.cli.cli as cli

import pytest
from cli_test_helpers import ArgvContext, EnvironContext


# ===
# A basic mockup to mimic Geonetwork responses to the executions of CLI command executions
class GeonetworkMockup:
    """Tests for cli commands"""


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
    result = os.system(f'{MAIN_COMMAND} --help')
    assert result == 0


def test_cmd_parse_document_available():
    """Is parse command available ?"""
    exit_status = os.system(f'{MAIN_COMMAND} {PARSE_DOCUMENT} --help')
    assert exit_status == 0


def test_cmd_upload_records_available():
    """Is upload command available ?"""
    exit_status = os.system(f'{MAIN_COMMAND} {UPLOAD_RECORDS} --help')
    assert exit_status == 0


def test_cmd_update_records_available():
    """Is update command available ?"""    
    exit_status = os.system(f'{MAIN_COMMAND} {UPDATE_RECORDS} --help')
    assert exit_status == 0


def test_cmd_update_postponed_values_available():
    """Is update_postponed command available ?"""
    exit_status = os.system(f'{MAIN_COMMAND} {UPDATE_POSTPONED_VALUES} --help')
    assert exit_status == 0


def test_cmd_delete_records_available():
    """Is delete command available ?"""
    exit_status = os.system(f'{MAIN_COMMAND} {DELETE_RECORDS} --help')
    assert exit_status == 0


def test_fail_without_secret():
    """
    Must fail without a ``SECRET`` environment variable specified
    """
    message_regex = r".* SECRET not set. .*"

    with EnvironContext(SECRET=None):
        with pytest.raises(SystemExit, match=message_regex):
            cli.cli()
            pytest.fail("CLI doesn't abort with missing SECRET")


# ===
# Command parse_document


def test_parse_document_expect_arguments():
    """Does parse command expect arguments ?"""    
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT], check=True)


def test_parse_document_creates_nonempty_readable_tmpfile_in_current_folder():
    """Does parse command create a non empty and readable csv file in current folder ?"""
    subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT, sample_records], check=True)
    csv_file = os.getcwd() + "/yaml_list.csv"
    assert os.path.exists(csv_file)
    assert open(csv_file, "r", encoding='utf8').read()
    os.unlink(csv_file)

def test_parse_documents_creates_xml_files_at_tmp_folder():
    """Does parse command create xml files in the temp folder ?"""
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
    """Does parse command create xml files at the given output folder ?"""
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
    """Does parse command raise exception if input file is not in yaml format ?"""
    wrong_input_file = 'csv_file.csv'
    open(wrong_input_file, 'a', encoding="utf8").close()

    with pytest.raises(ValueError, match=r".*yaml file.*"):
        subprocess.run([MAIN_COMMAND, PARSE_DOCUMENT, wrong_input_file], check=True)

    os.unlink(wrong_input_file)
