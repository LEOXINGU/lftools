import sys
import importlib
import platform


def _import_module(module_name, attr=None):
    try:
        module = importlib.import_module(module_name)
        return getattr(module, attr) if attr else module
    except Exception:
        return None


def _install_package(package_name, feedback=None):
    system_os = platform.system()

    if feedback:
        feedback.pushInfo(f'Package "{package_name}" not found. Trying to install...')

    try:
        if system_os == "Linux":
            import subprocess

            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # macOS e Windows → funciona melhor
            import pip
            pip.main(["install", package_name])

        if feedback:
            feedback.pushInfo(f'Package "{package_name}" installed successfully.')

        return True

    except Exception as e:
        if feedback:
            feedback.reportError(f'Failed to install "{package_name}": {e}')
        return False


# ==========================
# PILLOW
# ==========================

def ensure_pillow(feedback=None):
    Image = _import_module("PIL", "Image")
    if Image is not None:
        return Image

    if not _install_package("Pillow", feedback):
        return None

    importlib.invalidate_caches()

    return _import_module("PIL", "Image")


# ==========================
# MATPLOTLIB
# ==========================

def ensure_matplotlib(feedback=None):
    path = _import_module("matplotlib", "path")
    if path is not None:
        return path

    if not _install_package("matplotlib", feedback):
        return None

    importlib.invalidate_caches()

    return _import_module("matplotlib", "path")