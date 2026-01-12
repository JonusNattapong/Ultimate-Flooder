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

class OffensiveAI:
    """AI-powered offensive security assistant using fine-tuned model"""

    def __init__(self, model_path="./models/offensive_ai"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        """Load the trained offensive AI model"""
        try:
            # Try to load transformers if available
            from transformers import AutoTokenizer, AutoModelForCausalLM
            if os.path.exists(self.model_path):
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_path)
                add_system_log("[AI] Offensive AI model loaded successfully")
            else:
                add_system_log("[yellow]AI-WARN:[/] Trained model not found. Using fallback responses")
                self._use_fallback_mode()
        except ImportError:
            add_system_log("[yellow]AI-WARN:[/] Transformers not available. Using fallback AI responses")
            self._use_fallback_mode()
        except Exception as e:
            add_system_log(f"[red]AI-ERROR:[/] Failed to load model: {e}")
            self._use_fallback_mode()

    def _use_fallback_mode(self):
        """Fallback mode with pre-defined responses when model unavailable"""
        self.fallback_responses = {
            "web server": [
                "1. SQL Injection testing on login forms and search parameters",
                "2. XSS vulnerability scanning on user input fields",
                "3. Directory traversal attacks on file upload endpoints",
                "4. CSRF token analysis and bypass attempts",
                "5. API endpoint enumeration and parameter tampering"
            ],
            "database": [
                "1. SQL injection via user inputs and API parameters",
                "2. Blind SQL injection with time-based techniques",
                "3. Union-based injection for data extraction",
                "4. Error-based injection for database fingerprinting",
                "5. Out-of-band injection using DNS exfiltration"
            ],
            "network": [
                "1. Port scanning and service enumeration",
                "2. Vulnerability scanning with NSE scripts",
                "3. Man-in-the-middle attacks on unencrypted traffic",
                "4. ARP poisoning for network traffic interception",
                "5. Wireless network attacks if applicable"
            ],
            "default": [
                "1. Reconnaissance and information gathering",
                "2. Vulnerability assessment and scanning",
                "3. Exploitation of identified weaknesses",
                "4. Privilege escalation attempts",
                "5. Persistence and lateral movement techniques"
            ]
        }

    def generate_attack_strategy(self, target_info, max_length=300):
        """Generate attack strategies based on target information"""
        if not self.model or not self.tokenizer:
            # Use fallback responses
            return self._generate_fallback_strategy(target_info)

        prompt = f"""Analyze this target and suggest offensive red team techniques:

Target Information: {target_info}

Suggested Attack Strategies:"""

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            # Check if torch is available
            try:
                import torch
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                    self.model.cuda()
            except ImportError:
                pass

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=len(prompt.split()) + max_length,
                    num_return_sequences=1,
                    temperature=0.8,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract only the generated part
            generated = response.replace(prompt, "").strip()
            return generated if generated else "No specific strategies generated"

        except Exception as e:
            add_system_log(f"[red]AI-ERROR:[/] Generation failed: {e}")
            return self._generate_fallback_strategy(target_info)

    def _generate_fallback_strategy(self, target_info):
        """Generate fallback attack strategies based on target type"""
        target_lower = target_info.lower()

        if "web" in target_lower or "http" in target_lower or "apache" in target_lower or "nginx" in target_lower:
            strategies = self.fallback_responses["web server"]
        elif "database" in target_lower or "mysql" in target_lower or "postgres" in target_lower or "sql" in target_lower:
            strategies = self.fallback_responses["database"]
        elif "network" in target_lower or "port" in target_lower or "service" in target_lower:
            strategies = self.fallback_responses["network"]
        else:
            strategies = self.fallback_responses["default"]

        return "\n".join(strategies)

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
