import os
import fitz
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

class InstructionDeliveryAgent:
    def __init__(self, pdf_path, llm=None):
        self.pdf_path = pdf_path
        self.instructions = []
        self.llm = llm or ChatOpenAI(
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def extract_text_from_pdf(self):
        print("[📄] Extracting text from PDF...")
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        print("[✅] Text extraction complete.")
        return text

    def split_recipe_chunks(self, full_text):
        print("[✂️] Splitting into manageable chunks...")
        return RecursiveCharacterTextSplitter(
            chunk_size=2500,
            chunk_overlap=200
        ).split_text(full_text)

    def extract_instruction_blocks(self, chunk):
        instruction_prompt = f"""
        You are a cooking instruction extraction assistant.

        From the following cookbook text, extract clearly structured JSON with:
        - Recipe name
        - List of ingredients with quantities
        - Step-by-step instructions

        Format:
        {{
            "name": "Recipe Title",
            "ingredients": [
                "1 cup flour",
                "2 eggs",
                ...
            ],
            "instructions": "Step-by-step instructions here..."
        }}

        Return only valid JSON.

        Text:
        \"\"\"
        {chunk}
        \"\"\"
        """

        try:
            response = self.llm.invoke(instruction_prompt)
            return json.loads(response.content.strip())
        except Exception as e:
            print(f"[⚠️] Extraction failed: {e}")
            return None

    def run(self):
        text = self.extract_text_from_pdf()
        chunks = self.split_recipe_chunks(text)

        all_recipes = []
        print("[🤖] Parsing each chunk with LLM...")
        for i, chunk in enumerate(chunks):
            print(f"[🔍] Chunk {i+1}/{len(chunks)}")
            data = self.extract_instruction_blocks(chunk)
            if data:
                all_recipes.append(data)

        self.instructions = all_recipes
        print(f"[✅] Extracted {len(all_recipes)} complete recipes with instructions.")
        return all_recipes

    def save_to_file(self, output_path="data/instruction_recipes.json"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.instructions, f, indent=2)
        print(f"[💾] Instructions saved to {output_path}")
