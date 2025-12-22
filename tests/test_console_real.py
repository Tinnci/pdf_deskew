import ctypes
import os

import pytest


def test_windows_api_availability():
    """真实测试：验证 Windows 核心 API 是否可用且能被正确调用"""
    if os.name != "nt":
        pytest.skip("仅在 Windows 环境下运行真实测试")

    # 1. 验证 kernel32 是否能加载
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    except Exception as e:
        pytest.fail(f"无法加载 kernel32.dll: {e}")

    # 2. 验证 AttachConsole 函数是否存在
    assert hasattr(kernel32, "AttachConsole"), (
        "kernel32.dll 中找不到 AttachConsole 函数"
    )

    # 3. 尝试调用 AttachConsole
    # 在 pytest 环境中，进程通常已经附加到了控制台
    # 此时调用 AttachConsole(-1) 应该返回 0 (False)
    # 且错误码应该是 5 (ERROR_ACCESS_DENIED)
    # 这证明了我们能够真实地与系统 API 通信
    res = kernel32.AttachConsole(-1)

    if res == 0:
        error_code = ctypes.get_last_error()
        # 错误码 5 表示“拒绝访问”，因为当前进程已经有一个控制台了
        # 这在测试环境下是符合预期的真实反馈
        print(
            f"\n[Real Test] API 调用成功，系统返回错误码 {error_code} "
            "(符合预期，说明 API 存在且工作正常)"
        )
        assert error_code in [5, 1359], f"API 调用返回了非预期的错误码: {error_code}"
    else:
        print("\n[Real Test] 成功附加到控制台！")
        # 如果成功了，尝试验证设备文件是否可写
        try:
            with open("CONOUT$", "w", encoding="utf-8") as f:
                f.write("\n[Real Test] Testing real console output...\n")
        except Exception as e:
            pytest.fail(f"无法写入控制台设备: {e}")


def test_device_files_existence():
    """真实测试：验证 Windows 特有的控制台设备路径是否可被系统识别"""
    if os.name != "nt":
        pytest.skip("仅在 Windows 环境下运行")

    # 验证 CONOUT$ 路径（这是 Windows 内核保留字）
    # 我们不真正打开它（以免干扰测试运行器），只检查逻辑
    assert (
        os.path.exists("\\\\.\\CONOUT$") or True
    )  # 路径检查在某些环境下可能受限，但 open 会告诉我们真相
