import unittest
import subprocess
from pathlib import Path
from . import git
from .testutils import sandbox_dir, working_dir

class GitProviders_Test(unittest.TestCase):

	def clone(self, url):
		self.sandbox = self.enterContext(sandbox_dir())
		output = subprocess.check_output(['git', 'clone', url, 'repo']).decode().strip()
		print(output)
		self.repo = self.enterContext(working_dir('repo'))

	def test_clone(self):
		original_path = Path().resolve()
		original_license = Path('LICENSE').read_text()

		self.clone('https://github.com/vokimon/godot-asset-library-client.git')

		# Path is different
		self.assertNotEqual(Path().resolve(), original_path)

		# LICENSE stil the same content
		cloned_license = Path("LICENSE").read_text()
		self.assertEqual(cloned_license, original_license)









