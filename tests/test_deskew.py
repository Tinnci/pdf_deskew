# tests/test_deskew.py

import unittest
import os
from deskew_tool.deskew_pdf import deskew_pdf

class TestDeskewPDF(unittest.TestCase):
    def test_deskew_pdf_valid(self):
        input_pdf = "tests/sample_input.pdf"
        output_pdf = "tests/sample_output.pdf"
        dpi = 300
        background_color = (255, 255, 255)

        # 确保输入文件存在
        self.assertTrue(os.path.isfile(input_pdf), f"{input_pdf} 不存在。")

        try:
            deskew_pdf(input_pdf, output_pdf, dpi, background_color)
            # 检查输出文件是否生成
            self.assertTrue(os.path.isfile(output_pdf), f"{output_pdf} 未生成。")
        finally:
            # 清理生成的输出文件
            if os.path.isfile(output_pdf):
                os.remove(output_pdf)

    def test_deskew_pdf_invalid_input(self):
        input_pdf = "tests/non_existent.pdf"
        output_pdf = "tests/output.pdf"

        with self.assertRaises(IOError):
            deskew_pdf(input_pdf, output_pdf)

if __name__ == '__main__':
    unittest.main()
