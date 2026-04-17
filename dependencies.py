import sys
import io
import importlib
import platform


def _import_module(module_name, feedback=None):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        if feedback:
            feedback.pushInfo(f'Could not import "{module_name}": {e}')
        return None


def _pip_install(args, feedback=None):
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    fake_out = io.StringIO()
    fake_err = io.StringIO()

    try:
        import pip

        sys.stdout = fake_out
        sys.stderr = fake_err

        result = pip.main(args)

        stdout_text = fake_out.getvalue().strip()
        stderr_text = fake_err.getvalue().strip()

        if stdout_text and feedback:
            feedback.pushInfo(stdout_text)
        if stderr_text and feedback:
            feedback.pushInfo(stderr_text)

        if result not in (0, None):
            msg = stderr_text or stdout_text or f'pip.main returned code {result}'
            if feedback:
                feedback.reportError(msg)
            return False

        return True

    except Exception as e:
        stdout_text = fake_out.getvalue().strip()
        stderr_text = fake_err.getvalue().strip()
        extra = stderr_text or stdout_text

        if feedback:
            if extra:
                feedback.reportError(f'{e} | pip output: {extra}')
            else:
                feedback.reportError(str(e))
        return False

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def _install_package(package_name, feedback=None):
    system_os = platform.system()

    if feedback:
        feedback.pushInfo(f'Package "{package_name}" not found. Trying to install...')
        feedback.pushInfo(f'Operating system detected: {system_os}')
        feedback.pushInfo('Installation method: pip.main()')

    strategies = [
        ["install", package_name],
        ["install", "--user", package_name],
        ["install", "--upgrade", package_name],
        ["install", "--user", "--upgrade", package_name],
    ]

    for args in strategies:
        if feedback:
            feedback.pushInfo(f'Trying pip: {" ".join(args)}')

        ok = _pip_install(args, feedback)
        if ok:
            importlib.invalidate_caches()
            if feedback:
                feedback.pushInfo(f'Package "{package_name}" installed successfully.')
            return True

    if feedback:
        feedback.reportError(
            f'Failed to install "{package_name}" automatically. '
            f'Try manual installation in the QGIS Python environment.'
        )
    return False


# ==========================
# PILLOW
# ==========================

def ensure_pillow(feedback=None):
    Image = _import_module("PIL.Image", feedback)
    if Image is not None:
        if feedback:
            try:
                feedback.pushInfo(f'Pillow already available: {Image.__file__}')
            except Exception:
                feedback.pushInfo('Pillow already available.')
        return Image

    if not _install_package("Pillow", feedback):
        return None

    importlib.invalidate_caches()

    Image = _import_module("PIL.Image", feedback)
    if Image is None:
        if feedback:
            feedback.reportError(
                'Pillow installation was attempted, but PIL.Image is still unavailable.'
            )
        return None

    if feedback:
        try:
            feedback.pushInfo(f'Pillow loaded after installation: {Image.__file__}')
        except Exception:
            feedback.pushInfo('Pillow loaded after installation.')

    return Image


# ==========================
# MATPLOTLIB
# ==========================

def ensure_matplotlib(feedback=None):
    path = _import_module("matplotlib.path", feedback)
    if path is not None:
        if feedback:
            try:
                feedback.pushInfo(f'Matplotlib already available: {path.__file__}')
            except Exception:
                feedback.pushInfo('Matplotlib already available.')
        return path

    if not _install_package("matplotlib", feedback):
        return None

    importlib.invalidate_caches()

    path = _import_module("matplotlib.path", feedback)
    if path is None:
        if feedback:
            feedback.reportError(
                'Matplotlib installation was attempted, but matplotlib.path is still unavailable.'
            )
        return None

    if feedback:
        try:
            feedback.pushInfo(f'Matplotlib loaded after installation: {path.__file__}')
        except Exception:
            feedback.pushInfo('Matplotlib loaded after installation.')

    return path