# tests/test_deskew.py

import os
import unittest

import fitz

from deskew_tool.config import DeskewConfig
from deskew_tool.deskew_pdf import deskew_pdf


class TestDeskewPDF(unittest.TestCase):
    def setUp(self):
        self.input_pdf = "tests/sample_input.pdf"
        self.output_pdf = "tests/sample_output.pdf"

        # Create a dummy PDF for testing if it doesn't exist
        if not os.path.isfile(self.input_pdf):
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), "Test PDF Content")
            doc.save(self.input_pdf)
            doc.close()

    def tearDown(self):
        if os.path.isfile(self.input_pdf):
            os.remove(self.input_pdf)
        if os.path.isfile(self.output_pdf):
            os.remove(self.output_pdf)

    def test_deskew_pdf_valid(self):
        config = DeskewConfig(dpi=300, background_color=(255, 255, 255))

        # 确保输入文件存在
        self.assertTrue(os.path.isfile(self.input_pdf), f"{self.input_pdf} 不存在。")

        deskew_pdf(self.input_pdf, self.output_pdf, config=config)
        # 检查输出文件是否生成
        self.assertTrue(os.path.isfile(self.output_pdf), f"{self.output_pdf} 未生成。")

    def test_deskew_pdf_invalid_input(self):
        input_pdf = "tests/non_existent.pdf"
        output_pdf = "tests/output.pdf"

        with self.assertRaises(OSError):
            deskew_pdf(input_pdf, output_pdf)

    def test_rotate_image(self):
        from deskew_tool.deskew_pdf import rotate_image
        import numpy as np
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        rotated = rotate_image(img, 45)
        self.assertEqual(rotated.shape[2], 3)

    def test_remove_watermark(self):
        from deskew_tool.deskew_pdf import remove_watermark
        import numpy as np
        img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        # Add a "watermark"
        img[40:60, 40:60] = 0
        result = remove_watermark(img, algorithm="Navier-Stokes")
        self.assertEqual(result.shape, img.shape)
        
        # Test unsupported method
        result_unsupported = remove_watermark(img, method="Unknown")
        self.assertTrue(np.array_equal(img, result_unsupported))

    def test_enhance_image(self):
        from deskew_tool.deskew_pdf import enhance_image
        import numpy as np
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Test different contrast levels
        for level in [1, 2, 3, 4]:
            result = enhance_image(img, contrast_level=level, sharpening=True)
            self.assertEqual(result.shape, img.shape)
            
        # Test different denoising methods
        result_median = enhance_image(img, denoising_method="Median")
        self.assertEqual(result_median.shape, img.shape)
        
        result_none = enhance_image(img, denoising_method="None")
        self.assertEqual(result_none.shape, img.shape)

    def test_convert_grayscale(self):
        from deskew_tool.deskew_pdf import convert_grayscale
        import numpy as np
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Test scaling and smoothing
        result = convert_grayscale(img, scale_factor=2, smoothing_method="Median")
        self.assertEqual(result.shape[0], 200)
        self.assertEqual(result.shape[1], 200)
        
        result_none = convert_grayscale(img, smoothing_method="None")
        self.assertEqual(result_none.shape, img.shape)

    def test_process_single_page(self):
        from deskew_tool.deskew_pdf import process_single_page
        import tempfile
        
        config = DeskewConfig(
            remove_watermark=True,
            enhance_image=True,
            convert_grayscale=True
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            page_num, img_path = process_single_page(0, self.input_pdf, config, tmpdir)
            self.assertEqual(page_num, 0)
            self.assertTrue(os.path.exists(img_path))


if __name__ == "__main__":
    unittest.main()
