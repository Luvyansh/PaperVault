import joblib
import os
import logging

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.label_encoder = None
        self.is_ready = False

    def load_models(self):
        """Loads the ML artifacts into memory on server startup."""
        try:
            # Resolves to backend/app/models where you placed the .pkl files
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            models_dir = os.path.join(base_dir, "models")

            self.vectorizer = joblib.load(os.path.join(models_dir, "label_encoder.pkl")) # Swap these names if needed!
            # Ensure the actual file names match what you exported:
            self.vectorizer = joblib.load(os.path.join(models_dir, "tfidf_vectorizer.pkl"))
            self.classifier = joblib.load(os.path.join(models_dir, "stacking_ensemble.pkl"))
            self.label_encoder = joblib.load(os.path.join(models_dir, "label_encoder.pkl"))
            
            self.is_ready = True
            logger.info("✅ ML Pipeline loaded successfully into active memory.")
        except Exception as e:
            logger.error(f"❌ Failed to load ML models: {str(e)}")
            self.is_ready = False

    def predict_category(self, abstract_text: str):
        """Vectorizes text and predicts the ArXiv category."""
        if not self.is_ready:
            raise RuntimeError("ML Models are not loaded. Check server startup logs.")

        # 1. Transform the raw text
        X_features = self.vectorizer.transform([abstract_text])

        # 2. Predict the integer class
        pred_idx = self.classifier.predict(X_features)[0]

        # 3. Decode back to the human-readable string (e.g., 'cs.AI')
        predicted_category = self.label_encoder.inverse_transform([pred_idx])[0]

        # 4. Extract confidence score
        try:
            probabilities = self.classifier.predict_proba(X_features)[0]
            confidence = max(probabilities)
        except AttributeError:
            confidence = None

        return {
            "predicted_category": predicted_category,
            "confidence": round(float(confidence), 4) if confidence else None
        }

# Initialize a singleton instance
ml_classifier = MLService()