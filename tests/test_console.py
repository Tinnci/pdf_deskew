import sys
from unittest.mock import MagicMock, patch

from pdf_deskew_ui.main import attach_to_console


def test_attach_to_console_windows_success():
    """测试在 Windows 环境下成功附加到控制台的情况"""
    # 模拟 Windows 环境和相关的 API 调用
    with (
        patch("os.name", "nt"),
        patch("sys.platform", "win32"),
        patch("ctypes.WinDLL", create=True) as mock_windll,
        patch("builtins.open", MagicMock()) as mock_open,
    ):
        # 设置 mock kernel32
        mock_kernel32 = MagicMock()
        mock_kernel32.AttachConsole.return_value = True
        mock_windll.return_value = mock_kernel32

        # 保存原始流以便恢复
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        orig_stdin = sys.stdin

        try:
            result = attach_to_console()

            assert result is True
            # 验证是否调用了 AttachConsole(-1)
            mock_kernel32.AttachConsole.assert_called_once_with(-1)

            # 验证是否尝试打开了 Windows 特有的控制台设备
            # 注意：由于 mock_open 是 MagicMock，它不会真的改变 sys.stdout
            # 但我们可以检查 open 是否被正确调用
            mock_open.assert_any_call("CONOUT$", "w", encoding="utf-8", buffering=1)
            mock_open.assert_any_call("CONIN$", encoding="utf-8")

        finally:
            # 恢复原始流，防止影响其他测试
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr
            sys.stdin = orig_stdin


def test_attach_to_console_windows_fail():
    """测试在 Windows 环境下附加失败的情况（例如没有父控制台）"""
    with (
        patch("os.name", "nt"),
        patch("sys.platform", "win32"),
        patch("ctypes.WinDLL", create=True) as mock_windll,
    ):
        mock_kernel32 = MagicMock()
        mock_kernel32.AttachConsole.return_value = False
        mock_windll.return_value = mock_kernel32

        result = attach_to_console()
        assert result is False


def test_attach_to_console_non_windows():
    """测试在非 Windows 环境下直接返回 False"""
    with patch("os.name", "posix"), patch("sys.platform", "linux"):
        result = attach_to_console()
        assert result is False
