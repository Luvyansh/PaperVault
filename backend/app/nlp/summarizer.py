from transformers import pipeline
import warnings

# HuggingFace sometimes throws noisy warnings about hardware, we can ignore them for now
warnings.filterwarnings("ignore", category=UserWarning)

class Summarizer:
    """
    Condenses long research abstracts into short, punchy summaries.
    """
    def __init__(self):
        print("Loading Summarization Model...")
        # sshleifer/distilbart-cnn-12-6 is a highly optimized, smaller version of BART.
        # Perfect for running locally without melting your CPU.
        self.pipeline = pipeline(
            "summarization", 
            model="sshleifer/distilbart-cnn-12-6", 
            device=-1 # -1 forces it to use CPU. (0 would use GPU if you had CUDA setup)
        )
        
    def summarize(self, text: str) -> str:
        """
        Returns a shorter version of the input text.
        """
        if not text:
            return ""
            
        words = text.split()
        if len(words) < 40:
            # If the abstract is already very short, don't waste compute summarizing it
            return text
            
        # Dynamically set max_length based on the input size so the model doesn't crash
        input_length = len(words)
        max_len = min(100, input_length - 10)
        min_len = min(30, max_len - 10)
        
        try:
            # do_sample=False means it uses greedy decoding (faster, more deterministic)
            result = self.pipeline(text, max_length=max_len, min_length=min_len, do_sample=False)
            return result[0]['summary_text'].strip()
        except Exception as e:
            print(f"Summarization failed: {e}")
            return text

if __name__ == "__main__":
    summarizer = Summarizer()
    long_abstract = """
    Large language models (LLMs) have demonstrated remarkable capabilities in natural language understanding and generation. 
    However, their massive scale presents significant challenges for deployment on edge devices due to extreme memory and 
    computational requirements. In this paper, we propose a novel quantization technique combined with structured pruning 
    that drastically reduces the footprint of these models by over 70% while maintaining 95% of their original accuracy 
    on standard benchmark datasets. Our approach introduces a hardware-aware routing mechanism that dynamically allocates 
    compute resources based on the complexity of the input prompt.
    """
    
    summary = summarizer.summarize(long_abstract)
    print("\nOriginal Length:", len(long_abstract.split()), "words")
    print("Summary Length:", len(summary.split()), "words")
    print("-" * 40)
    print(summary)