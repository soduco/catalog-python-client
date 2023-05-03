"""Module for pytest
"""

import csv
import os
import subprocess
from importlib import import_module

from click.testing import CliRunner

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
# Test commands availability
def test_main_module():
    """
    Exercise (most of) the code in the ``__main__`` module.
    """
    import_module("soduco_geonetwork.cli")


def test_runas_module():
    """Can this package be run as a Python module?"""
    result = os.system("python -m soduco_geonetwork.cli.cli --help")
    assert result == 0


def test_entrypoint():
    """Is entrypoint script installed with poetry?"""
    runner = CliRunner()
    result = runner.invoke(cli.cli, "--help")
    assert result.exit_code == 0


def test_cmd_parse_document_available():
    """Is parse command available ?"""
    runner = CliRunner()
    result = runner.invoke(cli.parse, "--help")
    assert result.exit_code == 0


def test_cmd_upload_records_available():
    """Is upload command available ?"""
    runner = CliRunner()
    result = runner.invoke(cli.upload, "--help")
    assert result.exit_code == 0


def test_cmd_update_records_available():
    """Is update command available ?"""
    runner = CliRunner()
    result = runner.invoke(cli.update, "--help")
    assert result.exit_code == 0


def test_cmd_update_postponed_values_available():
    """Is update_postponed command available ?"""
    runner = CliRunner()
    result = runner.invoke(cli.update_postponed_values, "--help")
    assert result.exit_code == 0


def test_cmd_delete_records_available():
    """Is delete command available ?"""
    runner = CliRunner()
    result = runner.invoke(cli.delete, "--help")
    assert result.exit_code == 0


def test_fail_without_secret():
    """
    Must fail without a ``SECRET`` environment variable specified
    """
    with EnvironContext(GEONETWORK_USER=None, GEONETWORK_PASSWORD=None):
        results = CliRunner().invoke(cli.cli, ["parse"], catch_exceptions=True)
        raised = results.exception
        assert raised and "Missing expected ENV variables" in str(raised)


# ===
# Command parse_document


def test_parse_document_expect_arguments():
    """Does parse command expect arguments ?"""
    runner = CliRunner()
    result = runner.invoke(cli.parse)
    assert "Missing argument" in result.output


def test_parse_document_creates_nonempty_readable_tmpfile_in_current_folder():
    """Does parse command create a non empty and readable csv file in current folder ?"""
    runner = CliRunner()
    runner.invoke(cli.parse, [sample_records])
    csv_file = os.getcwd() + "/yaml_list.csv"
    assert os.path.exists(csv_file)
    assert open(csv_file, "r", encoding="utf8").read()
    os.unlink(csv_file)


def test_parse_documents_creates_xml_files_at_tmp_folder():
    """Does parse command create xml files in the temp folder ?"""
    current_folder = os.getcwd()
    runner = CliRunner()
    runner.invoke(cli.parse, [sample_records])
    csv_file = f"{current_folder}/yaml_list.csv"
    assert os.path.exists(csv_file)

    main_file = open(csv_file, "r", encoding="utf8")
    reader = csv.DictReader(main_file)

    for row in reader:
        xml_file = row["xml_file_path"]
        assert open(xml_file, "r", encoding="utf8").read()

    os.unlink(csv_file)


def test_parse_documents_creates_xml_files_at_output_folder():
    """Does parse command create xml files at the given output folder ?"""
    current_folder = os.getcwd()
    output_folder = f"{current_folder}/tmp"
    runner = CliRunner()
    runner.invoke(cli.parse, [sample_records, "--output_folder", output_folder])
    csv_file = f"{current_folder}/yaml_list.csv"
    assert os.path.exists(csv_file)

    main_file = open(csv_file, "r", encoding="utf8")
    reader = csv.DictReader(main_file)

    for row in reader:
        xml_file = row["xml_file_path"]
        assert open(xml_file, "r", encoding="utf8").read()
        os.unlink(xml_file)

    os.rmdir(output_folder)
    os.unlink(csv_file)


def test_parse_documents_raise_exception_on_bad_file_format():
    """Does parse command raise exception if input file is not in yaml format ?"""
    wrong_input_file = "csv_file.csv"
    open(wrong_input_file, "a", encoding="utf8").close()

    runner = CliRunner()
    result = runner.invoke(cli.parse, [wrong_input_file])

    assert isinstance(result.exception, ValueError)

    os.unlink(wrong_input_file)
