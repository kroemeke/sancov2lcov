import os
import subprocess
import unittest

class TestSancov2Lcov(unittest.TestCase):
    def test_conversion(self):
        input_file = "test_input.json"
        output_file = "test_output.info"
        
        # Run the script
        result = subprocess.run(
            ["python3", "sancov2lcov.py", "--symcov", input_file, "--output", output_file],
            capture_output=True,
            text=True
        )
        
        # Check return code
        self.assertEqual(result.returncode, 0, f"Script failed with stderr: {result.stderr}")
        
        # Read the output file
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Basic checks on content
        self.assertIn("SF:", content)
        self.assertIn("file1.c", content)
        self.assertIn("file2.c", content)
        
        # Check specific coverage
        # file1.c has 3 points, 2 covered. Lines 1 and 2 covered, 3 not.
        self.assertIn("DA:1,1", content)
        self.assertIn("DA:2,1", content)
        self.assertIn("DA:3,0", content)
        
        # file2.c has 1 point, 0 covered. Line 10 not covered.
        self.assertIn("DA:10,0", content)
        
        # Cleanup
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == '__main__':
    unittest.main()
