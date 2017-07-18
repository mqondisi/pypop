import base
import subprocess
import hashlib
import pytest
import psutil

memory_in_gb = 2  # memory needed for this test in GB
memory_in_bytes = memory_in_gb * (1024 * 1024 * 1024)

@pytest.mark.skipif(psutil.virtual_memory().available <= memory_in_bytes, reason="test can only be run if there is sufficient memory on the machine")
def test_100k_Emhaplofreq():
    process=subprocess.Popen(
	['./bin/pypop.py', '-m', '-c', './tests/data/Test_100k_20loci_Dataset.ini', './tests/data/Test_100k_20loci_Dataset.pop'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
        )
    process.communicate()
    exit_code = process.wait()  # wait until script completed

    # check exit code
    assert exit_code == 0
    # compare with md5sum of output file
    assert hashlib.md5(open("Test_100k_20loci_Dataset-out.txt", 'rb').read()).hexdigest() == 'd899396e90d99ad9eb2002506e699091'

