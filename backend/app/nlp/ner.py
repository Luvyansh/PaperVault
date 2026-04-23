import spacy

class NERProcessor:
    """
    Extracts Named Entities from research paper text using spaCy.
    """
    def __init__(self):
        # Load the small English pipeline
        # Disable components we don't need (like parser) to make it run faster
        try:
            self.nlp = spacy.load("en_core_web_sm", disable=["parser"])
        except OSError:
            print("Downloading spacy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm", disable=["parser"])
            
        # We only care about specific types of entities relevant to ML papers
        self.target_labels = {"ORG", "PERSON", "GPE", "PRODUCT", "WORK_OF_ART"}

    def extract_entities(self, text: str) -> list[dict]:
        """
        Scans text and returns a list of dictionaries containing the entity and its label.
        """
        if not text:
            return []

        # Process the text through the spaCy pipeline
        doc = self.nlp(text)
        
        entities = []
        # Use a set to track what we've already added so we don't store duplicates
        seen_entities = set()
        
        for ent in doc.ents:
            # Clean up the text (remove leading/trailing whitespace)
            clean_text = ent.text.strip()
            
            # Filter: Must be a target label, at least 2 chars, and not already seen
            if (ent.label_ in self.target_labels and 
                len(clean_text) > 1 and 
                clean_text.lower() not in seen_entities):
                
                entities.append({
                    "entity_type": ent.label_,
                    "value": clean_text
                })
                seen_entities.add(clean_text.lower())
                
        return entities

# Simple test block
if __name__ == "__main__":
    sample_abstract = "Researchers at Google DeepMind and Stanford University introduced a new Transformer model in London."
    
    processor = NERProcessor()
    results = processor.extract_entities(sample_abstract)
    
    print("\nExtracting from:", sample_abstract)
    print("-" * 40)
    for res in results:
        print(f"[{res['entity_type']}] -> {res['value']}")