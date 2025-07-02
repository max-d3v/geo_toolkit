import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from geo_aval import Agent

load_dotenv()

def main():
    console = Console()
    
    # Display welcome banner
    welcome_text = Text("🌍 GEO (Generative Engine Optimization) Evaluator", style="bold blue")
    console.print(Panel(welcome_text, expand=False))
    console.print()
    
    console.print("📊 Analyze how your brand appears in AI responses and discover competitive insights.\n", style="dim")
    
    try:
        # Get language/region selection
        console.print("🌐 Select your target market:", style="bold")
        console.print("1. 🇺🇸 United States (English)")
        console.print("2. 🇧🇷 Brazil (Portuguese)")
        
        while True:
            choice = Prompt.ask("Enter your choice (1 or 2)", choices=["1", "2"])
            if choice == "1":
                language = "en_US"
                break
            elif choice == "2":
                language = "pt_BR"
                break
        
        console.print(f"✅ Selected: {'🇺🇸 English (US)' if language == 'en_US' else '🇧🇷 Portuguese (BR)'}\n")
        
        # Get user inputs
        brand_name = Prompt.ask("🏢 Enter the brand/company name", default="")
        if not brand_name.strip():
            console.print("❌ Brand name is required!", style="red")
            return
        
        city = Prompt.ask("🏙️  Enter city", default="")
        
        # Combine location
        location = f"{city} ".strip()
        
        # Display analysis info
        console.print(f"\n🔍 Starting GEO analysis for: [bold]{brand_name}[/bold]")
        console.print(f"📍 Location: [dim]{location}[/dim]")
        console.print(f"🌐 Language: [dim]{language}[/dim]\n")
        
        # Initialize and run agent
        agent = Agent(language=language)
        result = agent.invoke(brand_name, city)
        graph = result["graph"]
        
        console.print("\n✅ Analysis completed successfully!", style="green")
        console.print(f"\n🔗 Companies found in analysis:\n", style="bold")
        
        for company in graph:
            console.print(f"• {company.name} (mentioned {company.times_cited} times)")
            if company.relevantUrls:
                console.print(f"  URLs: {', '.join(company.relevantUrls[:3])}")  # Show first 3 URLs
        
    except KeyboardInterrupt:
        console.print("\n\n👋 Analysis cancelled by user.", style="yellow")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ Error during analysis: {str(e)}", style="red")
        sys.exit(1)

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv("GEO_AVAL_API_KEY"):
        console = Console()
        console.print("❌ GEO_AVAL_API_KEY not found in environment variables!", style="red")
        console.print("Please add your OpenAI API key to the .env file", style="dim")
        sys.exit(1)
    
    main()