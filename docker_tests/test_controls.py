import unittest
import subprocess


class TestControls(unittest.TestCase):
    # Edirect doesn't show any version info
    # Using this to test that it is working
    def test_esearch(self):
        command = "esearch"
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()
        self.assertEqual(stderr.strip(), "ERROR:  Missing -db argument")

    def test_efetch(self):
        command = "efetch"
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        stdout, stderr = process.communicate()
        self.assertEqual(stderr.strip(), "ERROR:  Missing -db argument")


if __name__ == "__main__":
    unittest.main()
