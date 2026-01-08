import os
import json
import glob
from src.utils.logging import add_system_log
from src.utils.security_utils import rate_limit_check, sanitize_input

class LangChainFree:
    """LangChain implementation using OpenRouter Free models"""
    def __init__(self, api_key=None):
        from src.config import CONFIG
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or CONFIG.get("OPENROUTER_API_KEY")
        self.model = "mistralai/mistral-7b-instruct:free"
        self._llm = None

        if self.api_key:
            try:
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                    model=self.model,
                    temperature=0.7
                )
            except Exception as e:
                add_system_log(f"[red]AI-ERROR:[/] LangChain init failed: {type(e).__name__}")

    def generate(self, system_prompt, user_input):
        """Unified prompt execution with LangChain"""
        if not self._llm:
            return "Error: AI not configured (Missing OPENROUTER_API_KEY)"

        # Rate limiting
        if not rate_limit_check("ai_generate", max_calls=5, time_window=60):
            return "Error: Rate limit exceeded. Please wait before making another request."

        # Sanitize inputs
        system_prompt = sanitize_input(system_prompt, 2000)
        user_input = sanitize_input(user_input, 2000)

        try:
            from langchain.prompts import ChatPromptTemplate
            from langchain.schema.output_parser import StrOutputParser

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "{input}")
            ])

            chain = prompt | self._llm | StrOutputParser()
            return chain.invoke({"input": user_input})
        except Exception as e:
            add_system_log(f"[red]AI-ERROR:[/] Generation failed: {type(e).__name__}")
            return f"AI Error: {type(e).__name__}"

def search_intel(keyword):
    """Fast search through all stored sniper reports"""
    from rich.table import Table
    from rich.console import Console
    
    console = Console()
    report_files = glob.glob("txt/bounty_intel_*.json")
    
    if not report_files:
        return "[yellow]No structured reports found to search.[/yellow]"

    table = Table(title=f"🔍 Search Results for: '{keyword}'", border_style="green")
    table.add_column("Target Path", style="cyan")
    table.add_column("AI Intel / Content Match", style="white")
    table.add_column("Source Report", style="dim")

    count = 0
    for file_path in report_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for find in data.get("findings", []):
                    search_text = f"{find.get('path', '')} {find.get('intel', '')} {find.get('snippet', '')}".lower()
                    if keyword.lower() in search_text:
                        table.add_row(
                            find.get('path'), 
                            find.get('intel')[:100] + "...", 
                            os.path.basename(file_path)
                        )
                        count += 1
        except: continue
    
    if count > 0:
        console.print(table)
        return f"Found {count} matches."
    return "No matching intelligence found."
