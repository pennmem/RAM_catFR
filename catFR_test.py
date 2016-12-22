import unittest
import catFR
from pprint import pprint
import config
from collections import defaultdict
from pyepl.locals import *

class CatFRExperimentTestCase(unittest.TestCase):

    class TestCatFRExperiment(catFR.CatFRExperiment):
        def __init__(self, config):
            self.config = config

    def test_assign_categories_to_list(self):

        # Get config
        catFR_exp = self.TestCatFRExperiment(config)

        for _ in range(100):
            cats_by_session = catFR_exp._assign_categories_to_sessions()
            for sess, cats_by_list in enumerate(cats_by_session):
                n_appearances = defaultdict(int)
                for cats_by_item in cats_by_list:
                    for cat in cats_by_item:
                        n_appearances[cat] += 1
                for cat, n in n_appearances.items():
                    self.assertEqual(n, 3, 'Category %d appears %d times in sess %d'%(cat, n, sess))




if __name__ == '__main__':
    unittest.main()
