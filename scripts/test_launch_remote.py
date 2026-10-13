"""Exercise terminal lifecycle without a Claude login or network connection."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'launch-claude-remote/scripts/launch_remote.py'
FAKE = '''#!/usr/bin/env python3
import json, pathlib, sys, time
root = pathlib.Path(__file__).resolve().parent
if '--version' in sys.argv:
    print('test-claude'); sys.exit(0)
if '--help' in sys.argv:
    if (root / 'ineligible').exists():
        print('Login required', file=sys.stderr); sys.exit(1)
    print('--name --spawn --permission-mode'); sys.exit(0)
pathlib.Path('received.json').write_text(json.dumps(sys.argv[1:]))
if (root / 'exit').exists():
    print('https://claude.ai/code/session_stale', flush=True); sys.exit(1)
if not (root / 'pending').exists():
    print('https://claude.ai/code/session_test123', flush=True)
while True: time.sleep(1)
'''


@unittest.skipUnless(shutil.which('tmux'), 'tmux is needed for terminal integration tests')
class LaunchRemoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / 'workspace with spaces'
        self.workspace.mkdir()
        self.binary = self.root / 'claude'
        self.binary.write_text(FAKE)
        self.binary.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ['PATH'])
        self.sessions = set()
        self.addCleanup(self.stop_sessions)

    def stop_sessions(self):
        for session in self.sessions:
            subprocess.run(['tmux', 'kill-session', '-t', '=' + session], capture_output=True)

    def launch(self, *args, name='Remote workspace'):
        proc = subprocess.run([sys.executable, str(SCRIPT), '--cwd', str(self.workspace),
                               '--name', name, '--timeout', '1', *args],
                              env=self.env, text=True, capture_output=True, timeout=30)
        result = json.loads(proc.stdout)
        if 'tmux_session' in result:
            self.sessions.add(result['tmux_session'])
        return proc.returncode, result

    def test_detaches_reuses_and_passes_literal_arguments(self):
        name = "Remote ' quoted $(touch injected) `touch other` ; title"
        code, first = self.launch(name=name)
        self.assertEqual(code, 0, first)
        self.assertEqual(first['status'], 'registered')
        self.assertEqual(first['url'], 'https://claude.ai/code/session_test123')
        args = json.loads((self.workspace / 'received.json').read_text())
        self.assertEqual(args, ['remote-control', '--name', name, '--spawn', 'session',
                                '--permission-mode', 'bypassPermissions'])
        self.assertFalse((self.workspace / 'injected').exists())
        self.assertFalse((self.workspace / 'other').exists())
        code, second = self.launch(name=name)
        self.assertEqual(code, 0, second)
        self.assertTrue(second['reused'])
        self.assertEqual(first['tmux_session'], second['tmux_session'])

    def test_pending_is_retained_and_reused(self):
        (self.root / 'pending').touch()
        code, first = self.launch()
        self.assertEqual(code, 2, first)
        self.assertEqual(first['status'], 'pending')
        code, second = self.launch()
        self.assertEqual(code, 2, second)
        self.assertTrue(second['reused'])

    def test_dead_process_with_url_is_failure(self):
        (self.root / 'exit').touch()
        code, result = self.launch()
        self.assertEqual(code, 1, result)
        self.assertEqual(result['status'], 'exited')

    def test_existing_permissions_cannot_silently_change(self):
        self.launch()
        code, result = self.launch('--permission-mode', 'plan')
        self.assertEqual(code, 1, result)
        self.assertIn('different or unknown launch settings', result['detail'])

    def test_check_does_not_launch(self):
        code, result = self.launch('--check')
        self.assertEqual(code, 0, result)
        self.assertEqual(result['status'], 'checked')
        self.assertFalse((self.workspace / 'received.json').exists())

    def test_ineligible_help_reports_original_error(self):
        (self.root / 'ineligible').touch()
        code, result = self.launch()
        self.assertEqual(code, 1, result)
        self.assertEqual(result['detail'], 'Login required')
        self.assertFalse((self.workspace / 'received.json').exists())


if __name__ == '__main__':
    unittest.main()
