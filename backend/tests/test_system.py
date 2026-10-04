from __future__ import annotations
import unittest
import numpy as np
import pandas as pd

from backend.app.ml.feature_extractor import MODEL_FEATURES,URLValidationError,extract_url_features,normalize_for_model
from backend.app.ml.preprocessing import Standardizer,grouped_split,matrix_from_frame
from backend.app.ml.unit1 import analyze
from backend.app.ml.unit3 import PCA
from backend.app.ml.unit4 import analyze as markov
from backend.app.ml.models import BayesianLogistic
from backend.app.ml.evaluation import evaluate
from backend.app.services.predictor import Predictor


class SystemTests(unittest.TestCase):
    def test_normalizer_and_feature_order_for_training_and_live(self):
        self.assertEqual(normalize_for_model('https://example.com/a'), 'example.com/a')
        f=extract_url_features('https://example.com/a')
        self.assertEqual(tuple(f),tuple(__import__('backend.app.ml.feature_extractor',fromlist=['EXTRACTED_FEATURES']).EXTRACTED_FEATURES))
        self.assertEqual(len(MODEL_FEATURES),17)
        self.assertEqual(f['length_url'],13)
    def test_preprocessing_fits_and_transforms(self):
        x=np.array([[1.,2.],[3.,2.]])
        scaler=Standardizer.fit(x)
        np.testing.assert_allclose(scaler.transform(x),[[-1,0],[1,0]])
        self.assertEqual(scaler.to_dict()['features'],list(MODEL_FEATURES))
    def test_grouped_split_keeps_identical_predictors_together(self):
        f=pd.DataFrame({'x':[1,1,2,3,3,4],'phishing':[0,0,1,0,1,1]})
        tr,te=grouped_split(f,.5,42)
        train=set(f.iloc[tr].x);test=set(f.iloc[te].x)
        self.assertFalse(train&test)
        self.assertEqual(set(tr)|set(te),set(range(len(f))))
    def test_unit1_real_formula_on_fixture(self):
        f=pd.DataFrame({'phishing':[0,1,1,0],'qty_dot_url':[1,3,4,2],**{name:[0,1,2,3] for name in MODEL_FEATURES if name!='qty_dot_url'}})
        data=analyze(f)
        self.assertEqual(data['rows'],4)
        self.assertEqual(data['class_distribution'],{'legitimate':2,'phishing':2})
        self.assertAlmostEqual(data['bayes_example']['P(phishing|event)'],1.0)
        self.assertAlmostEqual(data['features']['length_url']['variance_population'],1.25)
    def test_pca_explained_variance_is_monotone(self):
        x=np.array([[1.,0],[0,1],[-1,0],[0,-1]])
        p=PCA(2).fit(x)
        self.assertAlmostEqual(float(p.explained_variance_ratio_.sum()),1.0)
        self.assertTrue(np.all(np.diff(np.cumsum(p.explained_variance_ratio_))>=0))
    def test_bayesian_log_likelihood_and_prior_are_finite(self):
        x=np.array([[0.],[1.],[2.]])
        y=np.array([0,0,1])
        weights=np.array([0.,1.])
        self.assertLess(BayesianLogistic.log_likelihood(x,y,weights),0)
        self.assertLess(BayesianLogistic.log_prior(weights),0)
        self.assertAlmostEqual(BayesianLogistic.log_posterior(x,y,weights),BayesianLogistic.log_likelihood(x,y,weights)+BayesianLogistic.log_prior(weights))
    def test_metrics_confusion_matrix_and_auc(self):
        r=evaluate([0,0,1,1],[.1,.4,.6,.9])
        self.assertEqual(r['confusion_matrix']['matrix'],[[2,0],[0,2]])
        self.assertAlmostEqual(r['roc_auc'],1.0)
        self.assertEqual(r['f1'],1.0)
    def test_markov_sequence_and_transitions(self):
        r=markov('ab/2?x=3')
        self.assertEqual(r['sequence'][0],'ALPHA')
        self.assertTrue(r['transition_counts'])
        self.assertGreaterEqual(r['mean_transition_surprise'],0)
        self.assertAlmostEqual(sum(r['initial_state_probabilities'].values()),1.0)
        self.assertIn('not a full Hidden Markov Model',r['description'])
    def test_saved_model_bundle_loads_and_predicts(self):
        p=Predictor()
        result=p.predict('https://example.com/login?x=1')
        self.assertIn(result['prediction'],(0,1))
        self.assertEqual(list(result['extracted_features']),list(MODEL_FEATURES))
        self.assertIn(result['risk_level'],('low','high'))
        self.assertTrue(result['explanation'])
        self.assertGreaterEqual(result['probability'],0)
        self.assertLessEqual(result['probability'],1)
    def test_invalid_url_throws_validation_error_in_prediction(self):
        with self.assertRaises(URLValidationError):Predictor().predict('file:///etc/passwd')


try:
    from fastapi.testclient import TestClient
    from backend.app.main import app
    API_AVAILABLE=True
except ImportError:
    API_AVAILABLE=False

@unittest.skipUnless(API_AVAILABLE,'FastAPI/TestClient dependencies are not installed')
class APITests(unittest.TestCase):
    def setUp(self):
        self.context=TestClient(app)
        self.client=self.context.__enter__()
    def tearDown(self):self.context.__exit__(None,None,None)
    def test_health_and_model_info(self):
        self.assertEqual(self.client.get('/health').status_code,200)
        self.assertEqual(self.client.get('/model-info').status_code,200)
    def test_prediction_api_and_validation(self):
        r=self.client.post('/predict',json={'url':'https://example.com'});self.assertEqual(r.status_code,200)
        self.assertIn('explanation',r.json())
        self.assertEqual(self.client.post('/predict',json={'url':'ftp://example.com'}).status_code,422)
    def test_analysis_endpoints(self):
        for path in ['/model-comparison','/dataset-summary','/unit1','/unit3','/unit5','/course-mapping']:
            with self.subTest(path=path):self.assertEqual(self.client.get(path).status_code,200)
        self.assertEqual(self.client.get('/unit4',params={'url':'https://example.com'}).status_code,200)
    def test_frontend_cors_and_unit4_rejects_bad_scheme(self):
        r=self.client.options('/predict',headers={'Origin':'http://127.0.0.1:5173','Access-Control-Request-Method':'POST'})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.headers.get('access-control-allow-origin'),'http://127.0.0.1:5173')
        self.assertEqual(self.client.get('/unit4',params={'url':'ftp://example.com'}).status_code,422)

if __name__=='__main__':unittest.main()
