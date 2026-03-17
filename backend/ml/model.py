from transformers import pipeline
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

MODEL_DIR = os.path.dirname(__file__)
SCORER_MODEL_PATH = os.path.join(MODEL_DIR, "risk_scorer.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

class NLPProcessor:
    def __init__(self):
        # Lazy-loaded on first use to avoid blocking server startup.
        self._sentiment_analyzer = None

    def _get_analyzer(self):
        if self._sentiment_analyzer is None:
            print("Loading HuggingFace sentiment pipeline (first use)...")
            self._sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                truncation=True
            )
        return self._sentiment_analyzer

    def analyze_sentiment(self, texts):
        """Returns average negative sentiment score (0 to 1) for a list of texts."""
        if not texts:
            return 0.5  # Neutral

        results = self._get_analyzer()(texts)
        negative_scores = []
        for r in results:
            if r['label'] == 'NEGATIVE':
                negative_scores.append(r['score'])
            else:
                negative_scores.append(1 - r['score'])

        return sum(negative_scores) / len(negative_scores) if negative_scores else 0.5


class RiskPredictionModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self._load_or_train()

    def _generate_synthetic_data(self, n_samples=500):
        """Generate synthetic dataset for the Risk Model."""
        np.random.seed(42)
        # Features: resource_utilization (0-1), payment_delay_days, tasks_completion_rate (0-1), negative_sentiment (0-1)
        res_util = np.random.uniform(0.5, 1.2, n_samples)
        pay_delay = np.random.exponential(10, n_samples)
        task_comp = np.random.uniform(0.1, 1.0, n_samples)
        neg_sent = np.random.uniform(0.0, 1.0, n_samples)
        
        # Target: Risk Score (0-100)
        # High utilization, high delay, low completion, high neg sentiment = High Risk
        risk_score = (res_util * 20) + (pay_delay * 1.5) + ((1 - task_comp) * 30) + (neg_sent * 30)
        risk_score = np.clip(risk_score, 0, 100)
        
        df = pd.DataFrame({
            'res_util': res_util,
            'pay_delay': pay_delay,
            'task_comp': task_comp,
            'neg_sent': neg_sent,
            'risk_score': risk_score
        })
        return df

    def _load_or_train(self):
        if os.path.exists(SCORER_MODEL_PATH) and os.path.exists(SCALER_PATH):
            self.model = joblib.load(SCORER_MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            print("Loaded trained Risk Prediction model.")
        else:
            print("Training synthetic Risk Prediction model...")
            df = self._generate_synthetic_data()
            X = df[['res_util', 'pay_delay', 'task_comp', 'neg_sent']]
            y = df['risk_score']
            
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            self.model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.model.fit(X_scaled, y)
            
            joblib.dump(self.model, SCORER_MODEL_PATH)
            joblib.dump(self.scaler, SCALER_PATH)
            print("Model training complete.")

    def predict_risk(self, resource_utilization: float, payment_delays_days: int, 
                     completed_tasks: int, total_tasks: int, negative_sentiment: float):
        
        task_comp = completed_tasks / total_tasks if total_tasks > 0 else 0
        features = np.array([[resource_utilization, payment_delays_days, task_comp, negative_sentiment]])
        features_scaled = self.scaler.transform(features)
        
        score = self.model.predict(features_scaled)[0]
        score = float(np.clip(score, 0, 100))
        
        category = "Low"
        if score > 70:
            category = "High"
        elif score > 40:
            category = "Medium"
            
        return score, category

# Singletons — NLPProcessor is lazy (model downloaded on first use)
# RiskPredictionModel trains/loads immediately (fast, no network needed)
nlp_processor = NLPProcessor()
risk_predictor = RiskPredictionModel()
