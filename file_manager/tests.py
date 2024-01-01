import hashlib
import shutil
import tempfile
from pathlib import Path

from django.test import TestCase
from django.core.management import call_command

from file_manager.models import Bucket, RootFolder, Object, Backup


class BackupDeleteTest(TestCase):
    TEST_DIRECTORY = Path("_tests")

    def setUp(self):
        if self.TEST_DIRECTORY.exists():
            shutil.rmtree(self.TEST_DIRECTORY)
        self.TEST_DIRECTORY.mkdir()
        bucket = Bucket.objects.create(
                name="test-bucket"
        )
        self.TEST_DIRECTORY.joinpath("root_folder").mkdir()
        self.TEST_DIRECTORY.joinpath("backup").mkdir()
        RootFolder.objects.create(
                bucket=bucket,
                linux_path=self.TEST_DIRECTORY.joinpath(
                    "root_folder").absolute(),
        )
        self.TEST_DIRECTORY.joinpath(
                "root_folder", "README.md").write_text(
                        "README.md", encoding="UTF-8")
        call_command("scan_folder")
        Backup.objects.create(
                bucket=bucket,
                path="_tests/backup",
        )
        call_command("back_up")

    def test_delete_backup(self):
        self.assertEqual(Object.objects.count(), 1)
        md5 = hashlib.md5()
        md5.update(b"README.md")
        backup = Backup.objects.get()
        hash_address = backup.hashfs.get(md5.hexdigest())
        self.assertIsNotNone(hash_address)
        Object.objects.get().rm_backup()
        self.assertIsNone(backup.hashfs.get(md5.hexdigest()))
