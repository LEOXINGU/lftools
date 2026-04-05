import os
import sys
import subprocess
import importlib

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_PACKAGES_DIR = os.path.join(
    PLUGIN_DIR,
    f'python{sys.version_info.major}.{sys.version_info.minor}'
)


def _add_local_packages():
    if os.path.isdir(LOCAL_PACKAGES_DIR) and LOCAL_PACKAGES_DIR not in sys.path:
        sys.path.insert(0, LOCAL_PACKAGES_DIR)


def _import_pil():
    _add_local_packages()
    try:
        from PIL import Image
        return Image
    except Exception:
        return None


def _ensure_pip(feedback=None):
    cmd = [sys.executable, "-m", "pip", "--version"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        if feedback is not None:
            feedback.pushInfo("pip not found. Trying to bootstrap with ensurepip...")

        cmd = [sys.executable, "-m", "ensurepip", "--upgrade"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0 and feedback is not None:
            feedback.reportError("Failed to initialize pip.")
            if result.stderr:
                feedback.reportError(result.stderr.strip())


def ensure_pillow(feedback=None):
    image_module = _import_pil()
    if image_module is not None:
        return image_module

    os.makedirs(LOCAL_PACKAGES_DIR, exist_ok=True)

    _ensure_pip(feedback)

    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-U",
        "--target",
        LOCAL_PACKAGES_DIR,
        "pillow"
    ]

    try:
        if feedback is not None:
            feedback.pushInfo("Pillow library not found. Trying to install automatically...")
            feedback.pushInfo("Executing: " + " ".join(cmd))

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            if feedback is not None:
                feedback.reportError("Failed to install Pillow.")
                if result.stderr:
                    feedback.reportError(result.stderr.strip())
            return None

    except Exception as e:
        if feedback is not None:
            feedback.reportError(f"Failed to install Pillow: {e}")
        return None

    importlib.invalidate_caches()
    image_module = _import_pil()

    if image_module is not None:
        if feedback is not None:
            feedback.pushInfo("Pillow installed successfully.")
        return image_module

    if feedback is not None:
        feedback.reportError(
            "Pillow was installed, but could not be imported. Please check the installation and try again."
        )

    return None