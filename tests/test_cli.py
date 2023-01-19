import os 
import subprocess
import pytest
import tempfile

# ===
# A basic mockup to mimic Geonetwork responses to the executions of CLI command executions
class GeonetworkMockup:
    ...    

# ===
# Resources
sample_records = os.path.dirname(__file__) + "/fixtures/instance.yaml"

# ===
# CLI commands to test
PARSE_DOCUMENT = "parse_document"
UPLOAD_RECORDS = "upload_records"
UPDATE_RECORDS = "update_records"
UPDATE_POSTPONED_VALUES = "update_postponed_values"
DELETE_RECORDS = "delete_records"

# ===
# Test commands availability

def test_cmd_parse_document_available():
    exit_status = os.system(f'{PARSE_DOCUMENT} --help')
    assert exit_status == 0

def test_cmd_upload_records_available():
    exit_status = os.system(f'{UPLOAD_RECORDS} --help')
    assert exit_status == 0

def test_cmd_update_records_available():
    exit_status = os.system(f'{UPDATE_RECORDS} --help')
    assert exit_status == 0
    
def test_cmd_update_postponed_values_available():
    exit_status = os.system(f'{UPDATE_POSTPONED_VALUES} --help')
    assert exit_status == 0
    
def test_cmd_delete_records_available():
    exit_status = os.system(f'{DELETE_RECORDS} --help')
    assert exit_status == 0

# ===
# Command parse_document

def test_parse_document_expect_arguments():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run([PARSE_DOCUMENT], check=True)    

def test_parse_document_creates_nonempty_readable_tmpfile():
    odir = tempfile.gettempdir()
    subprocess.run([PARSE_DOCUMENT, sample_records, odir], check=True)
    yaml_file = odir + "/yaml_list.csv"
    assert os.path.exists(yaml_file)
    assert open(yaml_file, "r").read()
