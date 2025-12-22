# tests/test_deskew.py

import os
import unittest

import fitz

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
        dpi = 300
        background_color = (255, 255, 255)

        # 确保输入文件存在
        self.assertTrue(os.path.isfile(self.input_pdf), f"{self.input_pdf} 不存在。")

        deskew_pdf(self.input_pdf, self.output_pdf, dpi, background_color)
        # 检查输出文件是否生成
        self.assertTrue(os.path.isfile(self.output_pdf), f"{self.output_pdf} 未生成。")

    def test_deskew_pdf_invalid_input(self):
        input_pdf = "tests/non_existent.pdf"
        output_pdf = "tests/output.pdf"

        with self.assertRaises(OSError):
            deskew_pdf(input_pdf, output_pdf)


if __name__ == "__main__":
    unittest.main()
