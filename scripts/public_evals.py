"""Independent synthetic eval; no private packets, network or image generation."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('director', ROOT/'scripts/guardian_visual_director.py')
director = importlib.util.module_from_spec(spec)
spec.loader.exec_module(director)

class PortableDirectorTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((ROOT/'examples/synthetic-cat.input.json').read_text())

    def test_determinism_and_traceability(self):
        one = director.compile_brief(self.fixture)
        two = director.compile_brief(copy.deepcopy(self.fixture))
        self.assertEqual(one, two)
        self.assertEqual(one['preflight_qa']['image_qa_status'], 'pending_pixels')
        self.assertTrue(all(row['evidence_ids'] for row in one['evidence_chain']))
        self.assertTrue(all(set(row['evidence_ids']) <= {e['id'] for e in self.fixture['evidence']} for row in one['evidence_chain']))
        self.assertGreaterEqual(one['humanoid_level']['target'], 0.8)

    def test_missing_identity_stays_unresolved(self):
        output = director.compile_brief(self.fixture)
        self.assertFalse(output['human_identity_direction']['resolved_for_canon'])
        self.assertTrue(output['identity_translator']['uncertainties'] or output['human_identity_direction']['uncertainties'])

    def test_optional_schema_validation(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest('jsonschema not installed; no dependency downloaded')
        jsonschema.validate(self.fixture, json.loads((ROOT/'schemas/director-input.schema.json').read_text()))
        jsonschema.validate(director.compile_brief(self.fixture), json.loads((ROOT/'schemas/visual-brief.schema.json').read_text()))

if __name__ == '__main__':
    unittest.main()
