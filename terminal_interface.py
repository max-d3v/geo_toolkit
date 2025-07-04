import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from geo_aval import Agent
from rich.pretty import pprint as rpprint
from langgraph.types import interrupt, Command

load_dotenv()

def main():
    console = Console()
    
    # Display welcome banner
    welcome_text = Text("🌍 GEO (Generative Engine Optimization) Evaluator", style="bold blue")
    console.print(Panel(welcome_text, expand=False))
    console.print()
    
    console.print("📊 Analyze how your brand appears in AI responses and discover competitive insights.\n", style="dim")
    
    try:

        if os.getenv("ENV") == "development":
            brand_name = "copapel"
            city = "joinville"
            location = f"{city} ".strip()
            language = "pt_BR" 
        else:
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
        config = {"configurable": {"thread_id": "1"}}
        agent = Agent()
        agent.invoke(target=brand_name, city=city, language=language, config=config)
            

        # Will stop before gathering results
        compiled_graph = agent.get_graph()
        graph_state = compiled_graph.get_state(config)
        values = graph_state.values

        if graph_state.next == ('gather_results',):
            console.print("\n🔄 Want to add keywords / key searches? Max: 5 (divided by ,)", style="yellow")
            words = Prompt.ask("Enter keywords / key searches to refine the search", default="")
            words_list = [word.strip() for word in words.split(",") if word.strip()]

            while len(words_list) > 5:
                console.print("❌ You can only add up to 5 keywords. Please reduce your input.", style="red")
                words = Prompt.ask("Enter keywords / key searches to refine the search", default="")
                words_list = [word.strip() for word in words.split(",") if word.strip()]


            console.print(f"\n🔍 Adding keywords to refine search: {', '.join(words_list)}", style="yellow")
            compiled_graph.update_state(config, {
                "refined_keywords": values.get("refined_keywords", []) + words_list,
            })

            result = compiled_graph.invoke(Command(resume=""), config=config)


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