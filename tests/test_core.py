import tempfile
import unittest
from pathlib import Path

from src.image_loader import get_image_files
from src.rename_manager import RenameManager
from src.utils import build_target_name, has_illegal_chars, natural_sort_key


class CoreLogicTests(unittest.TestCase):
    def test_natural_sort_key_orders_numbers_naturally(self):
        names = ["10.jpg", "1.jpg", "2.jpg", "a11.png", "a2.png"]
        ordered = sorted(names, key=natural_sort_key)
        self.assertEqual(ordered, ["1.jpg", "2.jpg", "10.jpg", "a2.png", "a11.png"])

    def test_image_loader_ignores_non_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name in ["2.jpg", "1.png", "note.txt", "photo.webp"]:
                (folder / name).write_bytes(b"x")
            files = get_image_files(folder)
            self.assertEqual([p.name for p in files], ["1.png", "2.jpg", "photo.webp"])

    def test_filename_validation_and_extension_handling(self):
        self.assertTrue(has_illegal_chars("bad:name"))
        self.assertFalse(has_illegal_chars("good_name"))
        self.assertEqual(build_target_name("cat", ".jpg"), "cat.jpg")
        self.assertEqual(build_target_name("cat.png", ".jpg"), "cat.png")
        with self.assertRaises(ValueError):
            build_target_name("cat.exe", ".jpg")

    def test_unique_name_and_copy2_save(self):
        with tempfile.TemporaryDirectory() as src_tmp, tempfile.TemporaryDirectory() as dst_tmp:
            source = Path(src_tmp) / "1.jpg"
            source.write_bytes(b"image")
            output = Path(dst_tmp)
            (output / "cat.jpg").write_bytes(b"exists")

            manager = RenameManager(output)
            self.assertEqual(manager.make_unique_path("cat.jpg").name, "cat_001.jpg")
            saved = manager.save_copy(source, "cat_001.jpg")

            self.assertTrue(saved.exists())
            self.assertEqual(saved.read_bytes(), b"image")


if __name__ == "__main__":
    unittest.main()
