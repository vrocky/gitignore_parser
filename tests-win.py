from unittest.mock import patch, mock_open
from pathlib import Path, WindowsPath
from tempfile import TemporaryDirectory

from gitignore_parser import parse_gitignore

from unittest import TestCase, main


class Test(TestCase):
    def test_simple(self):
        matches = _parse_gitignore_string(
            '__pycache__/\n'
            '*.py[cod]',
            fake_base_dir='C:\\Users\\michael'
        )
        self.assertFalse(matches('C:\\Users\\michael\\main.py'))
        self.assertTrue(matches('C:\\Users\\michael\\main.pyc'))
        self.assertTrue(matches('C:\\Users\\michael\\dir\\main.pyc'))
        self.assertTrue(matches('C:\\Users\\michael\\__pycache__'))

    def test_incomplete_filename(self):
        matches = _parse_gitignore_string('o.py', fake_base_dir='C:\\Users\\michael')
        self.assertTrue(matches('C:\\Users\\michael\\o.py'))
        self.assertFalse(matches('C:\\Users\\michael\\foo.py'))
        self.assertFalse(matches('C:\\Users\\michael\\o.pyc'))
        self.assertTrue(matches('C:\\Users\\michael\\dir\\o.py'))
        self.assertFalse(matches('C:\\Users\\michael\\dir\\foo.py'))
        self.assertFalse(matches('C:\\Users\\michael\\dir\\o.pyc'))

    def test_wildcard(self):
        matches = _parse_gitignore_string(
            'hello.*',
            fake_base_dir='C:\\Users\\michael'
        )
        self.assertTrue(matches('C:\\Users\\michael\\hello.txt'))
        self.assertTrue(matches('C:\\Users\\michael\\hello.foobar\\'))
        self.assertTrue(matches('C:\\Users\\michael\\dir\\hello.txt'))
        self.assertTrue(matches('C:\\Users\\michael\\hello.'))
        self.assertFalse(matches('C:\\Users\\michael\\hello'))
        self.assertFalse(matches('C:\\Users\\michael\\helloX'))

    def test_anchored_wildcard(self):
        matches = _parse_gitignore_string(
            '/hello.*',
            fake_base_dir='C:\\Users\\michael'
        )
        self.assertTrue(matches('C:\\Users\\michael\\hello.txt'))
        self.assertTrue(matches('C:\\Users\\michael\\hello.c'))
        self.assertFalse(matches('C:\\Users\\michael\\a\\hello.java'))

    def test_trailingspaces(self):
        matches = _parse_gitignore_string(
            'ignoretrailingspace \n'
            'notignoredspace\\ \n'
            'partiallyignoredspace\\  \n'
            'partiallyignoredspace2 \\  \n'
            'notignoredmultiplespace\\ \\ \\ ',
            fake_base_dir='C:\\Users\\michael'
        )
        self.assertTrue(matches('C:\\Users\\michael\\ignoretrailingspace'))
        self.assertFalse(matches('C:\\Users\\michael\\ignoretrailingspace '))
        self.assertTrue(matches('C:\\Users\\michael\\partiallyignoredspace '))
        self.assertFalse(matches('C:\\Users\\michael\\partiallyignoredspace  '))
        self.assertFalse(matches('C:\\Users\\michael\\partiallyignoredspace'))
        self.assertTrue(matches('C:\\Users\\michael\\partiallyignoredspace2  '))
        self.assertFalse(matches('C:\\Users\\michael\\partiallyignoredspace2   '))
        self.assertFalse(matches('C:\\Users\\michael\\partiallyignoredspace2 '))
        self.assertFalse(matches('C:\\Users\\michael\\partiallyignoredspace2'))
        self.assertTrue(matches('C:\\Users\\michael\\notignoredspace '))
        self.assertFalse(matches('C:\\Users\\michael\\notignoredspace'))
        self.assertTrue(matches('C:\\Users\\michael\\notignoredmultiplespace   '))
        self.assertFalse(matches('C:\\Users\\michael\\notignoredmultiplespace'))

    def test_supports_path_type_argument(self):
        matches = _parse_gitignore_string(
            'file1\n!file2', fake_base_dir='C:\\Users\\michael'
        )
        self.assertTrue(matches(WindowsPath('C:\\Users\\michael\\file1')))
        self.assertFalse(matches(WindowsPath('C:\\Users\\michael\\file2')))

"""
    def test_symlink_to_another_directory(self):
        with TemporaryDirectory() as project_dir:
            with TemporaryDirectory() as another_dir:
                matches = \
                    _parse_gitignore_string('link', fake_base_dir=project_dir)

                # Create a symlink to another directory.
                link = Path(project_dir, 'link')
                target = Path(another_dir, 'target')
                link.symlink_to(target)

                # Check the intended behavior according to
                # https://git-scm.com/docs/gitignore#_notes:
                # Symbolic links are not followed and are matched as if they
                # were regular files.
                self.assertTrue(matches(link))
"""


def _parse_gitignore_string(data: str, fake_base_dir: str = None):
    with patch('builtins.open', mock_open(read_data=data)):
        success = parse_gitignore(f'{fake_base_dir}\\.gitignore', fake_base_dir)
        return success

if __name__ == '__main__':
    main()
