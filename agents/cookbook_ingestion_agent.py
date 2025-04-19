import os
import fitz
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

class CookbookIngestionAgent:
    def __init__(self, pdf_path, llm=None):
        self.pdf_path = pdf_path
        self.recipes = []
        self.llm = llm or ChatOpenAI(
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    def extract_text_from_pdf(self):
        print("[🔍] Extracting text from PDF...")
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        text = "\n".join([page.get_text() for page in doc])
        doc.close()
        print("[✅] PDF text extracted.")
        return text

    def split_recipes_with_llm(self, full_text):
        print("[🤖] Asking LLM to detect and split recipes...")
        large_chunks = RecursiveCharacterTextSplitter(
            chunk_size=2500,
            chunk_overlap=200
        ).split_text(full_text)

        all_recipe_blocks = []

        splitter_prompt_template = """
        You are a recipe detection assistant.

        Split the following cookbook text into individual recipe blocks.
        Each block must include the title, ingredients, and instructions.

        Separate each block with a line containing only: ===

        Text:
        \"\"\"
        {chunk}
        \"\"\"
        """

        for i, chunk in enumerate(large_chunks):
            print(f"[🔍] Splitting chunk {i+1}/{len(large_chunks)}")

            prompt = splitter_prompt_template.format(chunk=chunk)
            try:
                response = self.llm.invoke(prompt)
                blocks = response.content.split("===")
                clean_blocks = [b.strip() for b in blocks if len(b.strip()) > 100]
                all_recipe_blocks.extend(clean_blocks)
            except Exception as e:
                print(f"[⚠️] Failed to split chunk {i+1}: {e}")

        print(f"[📦] LLM returned {len(all_recipe_blocks)} recipe blocks.")
        return all_recipe_blocks

    def parse_recipe_block(self, block):
        parsing_prompt = f"""
        You are a recipe extraction assistant.

        Convert the following recipe into JSON format with this structure:
        {{
        "name": "Recipe title",
        "ingredients": ["item1", "item2", ...],
        "instructions": "Step-by-step instructions..."
        }}

        Only return valid JSON.

        Recipe:
        \"\"\"
        {block}
        \"\"\"
        """
        try:
            response = self.llm.invoke(parsing_prompt)
            json_str = response.content.strip()
            recipe = json.loads(json_str)
            return recipe
        except Exception as e:
            print(f"[❌] Error parsing block: {str(e)}")
            return None

    def parse_cookbook(self):
        print("[🚀] Starting full recipe extraction pipeline...")
        content = self.extract_text_from_pdf()

        recipe_blocks = self.split_recipes_with_llm(content)

        print("[🧠] Now parsing recipe blocks into structured data...")
        structured_recipes = []
        for i, block in enumerate(recipe_blocks):
            print(f"[📑] Parsing block {i+1}/{len(recipe_blocks)}")
            recipe = self.parse_recipe_block(block)
            if recipe:
                structured_recipes.append(recipe)

        print(f"[✅] Finished! Parsed {len(structured_recipes)} structured recipes.")
        self.recipes = structured_recipes
        return self.recipes