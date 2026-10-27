"""Unit tests for the sim-agnostic helpers in render_mcap.py.

No simulator, GPU, or foxglove install is needed: missing third-party modules
are stubbed so the module can be imported and its pure helpers exercised.
"""
import importlib.util
import py_compile
import sys
import types
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'render_mcap.py'
MESSAGE_NAMES = ['FrameTransform', 'FrameTransforms', 'SceneUpdate', 'SceneEntity',
                 'ModelPrimitive', 'Pose', 'Vector3', 'Quaternion', 'Color']


def _stub(name, **attrs):
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


def load_module():
    for name in ('numpy', 'trimesh', 'foxglove'):
        try:
            __import__(name)
        except ImportError:
            _stub(name)
    try:
        import foxglove.messages  # noqa: F401
    except ImportError:
        messages = _stub('foxglove.messages', **{n: type(n, (), {}) for n in MESSAGE_NAMES})
        sys.modules['foxglove'].messages = messages
    spec = importlib.util.spec_from_file_location('render_mcap', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RenderMcapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_script_compiles(self):
        py_compile.compile(str(SCRIPT), doraise=True)

    def test_quaternion_is_reordered_from_wxyz_to_xyzw(self):
        self.assertEqual(self.mod.wxyz_to_xyzw((1.0, 0.0, 0.0, 0.0)), (0.0, 0.0, 0.0, 1.0))
        self.assertEqual(self.mod.wxyz_to_xyzw([0.5, 0.1, 0.2, 0.3]), (0.1, 0.2, 0.3, 0.5))

    def test_log_time_is_integer_nanoseconds(self):
        self.assertEqual(self.mod.log_time_ns(0, 0.02), 0)
        self.assertEqual(self.mod.log_time_ns(3, 0.02), 60_000_000)
        self.assertIsInstance(self.mod.log_time_ns(7, 0.01), int)

    def test_mesh_rules_are_kept(self):
        text = SCRIPT.read_text()
        self.assertIn('media_type="model/obj"', text)   # OBJ, never STL
        self.assertIn('frame_locked=True', text)        # /robot logged once, frame-locked
        self.assertIn('if t == 0:', text)


if __name__ == '__main__':
    unittest.main()
