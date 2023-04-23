import bs4
import tqdm
import pandas
import meteostat
import pandas_gbq
import unittest
import subprocess


class TestVersion(unittest.TestCase):
    def test_prefect(self):
        command = "prefect --version | tail -n 1"
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()
        self.assertEqual(stdout.strip(), "2.10.4")

    def test_python(self):
        command = "python --version | awk '{print $2}'"
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()
        self.assertEqual(stdout.strip(), "3.9.16")

    def test_bs4(self):
        bs4_version = bs4.__version__
        self.assertEqual(bs4_version, "4.12.1")

    def test_tqdm(self):
        tqdm_version = tqdm.__version__
        self.assertEqual(tqdm_version, "4.65.0")

    def test_pandas(self):
        pandas_version = pandas.__version__
        self.assertEqual(pandas_version, "1.5.2")

    def test_pandas_gbq(self):
        pandas_gbq_version = pandas_gbq.__version__
        self.assertEqual(pandas_gbq_version, "0.18.1")

    def test_meteostat(self):
        meteostat_version = meteostat.__version__
        self.assertEqual(meteostat_version, "1.6.5")


if __name__ == "__main__":
    unittest.main()
