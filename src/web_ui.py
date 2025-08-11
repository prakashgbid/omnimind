#!/usr/bin/env python3
"""
OmniMind Web UI - Browser Interface

A beautiful web interface for OmniMind using Gradio.
Access your persistent intelligence from any browser.
"""

import sys
import os
import json
from datetime import datetime
from typing import List, Tuple, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
import pandas as pd
import plotly.graph_objects as go
from src.core.omnimind_enhanced import OmniMindEnhanced as OmniMind
from src.providers.ollama_provider import OllamaProvider


class OmniMindWebUI:
    """
    Web interface for OmniMind using Gradio.
    
    This provides a user-friendly way to interact with OmniMind
    through a web browser, with chat, search, and visualization features.
    """
    
    def __init__(self):
        """Initialize the web UI."""
        self.omnimind = None
        self.chat_history = []
        self.current_model = 'llama3.2:3b'
        self.available_models = []
        
    def initialize_omnimind(self):
        """Initialize OmniMind instance."""
        try:
            self.omnimind = OmniMind()
            return "✅ OmniMind initialized successfully!"
        except Exception as e:
            return f"❌ Failed to initialize: {str(e)}"
    
    def process_message(self, message: str, history: List[Tuple[str, str]], 
                       model: str = 'llama3.2:3b', use_consensus: bool = False) -> Tuple[List[Tuple[str, str]], str]:
        """
        Process a user message and return updated chat history.
        
        Args:
            message: User's input message
            history: Current chat history
            use_consensus: Whether to use multi-model consensus
        
        Returns:
            Updated history and status message
        """
        if not self.omnimind:
            status = self.initialize_omnimind()
            if "Failed" in status:
                return history + [(message, "Please initialize OmniMind first!")], status
        
        try:
            # Get response from OmniMind
            kwargs = {'use_consensus': use_consensus}
            if not use_consensus:
                kwargs['model'] = model
            response = self.omnimind.think(message, **kwargs)
            
            # Update history
            history.append((message, response))
            
            return history, "✅ Response generated"
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history.append((message, error_msg))
            return history, f"❌ {error_msg}"
    
    def search_memories(self, query: str, limit: int = 10) -> pd.DataFrame:
        """
        Search memories and return as DataFrame for display.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            DataFrame with search results
        """
        if not self.omnimind:
            return pd.DataFrame({"Error": ["Please initialize OmniMind first"]})
        
        try:
            memories = self.omnimind.search_memories(query, limit=limit)
            
            if not memories:
                return pd.DataFrame({"Result": ["No memories found"]})
            
            # Convert to DataFrame
            data = []
            for mem in memories:
                data.append({
                    "Score": f"{mem['score']:.3f}",
                    "Date": mem['metadata'].get('timestamp', 'Unknown')[:19],
                    "Content": mem['content'][:200] + "..." if len(mem['content']) > 200 else mem['content'],
                    "Type": mem['metadata'].get('type', 'memory')
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            return pd.DataFrame({"Error": [str(e)]})
    
    def get_timeline(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get timeline of memories between dates.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with timeline
        """
        if not self.omnimind:
            return pd.DataFrame({"Error": ["Please initialize OmniMind first"]})
        
        try:
            memories = self.omnimind.get_timeline(start_date, end_date)
            
            if not memories:
                return pd.DataFrame({"Result": ["No memories in this period"]})
            
            # Convert to DataFrame
            data = []
            for mem in memories[:50]:  # Limit to 50 for display
                data.append({
                    "Timestamp": mem.get('timestamp', 'Unknown'),
                    "Thought": mem.get('thought', '')[:300],
                    "Project": mem.get('project', 'None'),
                    "Tags": mem.get('tags', '')
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            return pd.DataFrame({"Error": [str(e)]})
    
    def visualize_knowledge_graph(self) -> go.Figure:
        """
        Create a visualization of the knowledge graph.
        
        Returns:
            Plotly figure showing the graph
        """
        if not self.omnimind or not self.omnimind.graph:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No knowledge graph data available yet",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        # Create network visualization
        # This is simplified - real implementation would be more complex
        graph = self.omnimind.graph
        
        if len(graph.nodes) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Knowledge graph is empty - start adding memories!",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False
            )
            return fig
        
        # Create simple visualization
        # In reality, you'd use spring layout or similar
        fig = go.Figure()
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=[0, 1, 2],  # Placeholder positions
            y=[0, 1, 0],
            mode='markers+text',
            marker=dict(size=20, color='lightblue'),
            text=["Memory 1", "Memory 2", "Memory 3"],
            textposition="top center"
        ))
        
        fig.update_layout(
            title="Knowledge Graph (Preview)",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface.
        
        Returns:
            Gradio Blocks interface
        """
        # Custom CSS for better styling
        css = """
        .gradio-container {
            font-family: 'Inter', sans-serif;
        }
        .chat-window {
            height: 500px;
        }
        #component-0 {
            max-width: 1200px;
            margin: auto;
        }
        """
        
        with gr.Blocks(title="OmniMind", css=css, theme=gr.themes.Soft()) as interface:
            # Header
            gr.Markdown(
                """
                # 🧠 OmniMind - FREE Local AI System
                ### 5 Local Models • Perfect Memory • $0/month • 100% Private
                
                **No API costs, no data leaves your computer, unlimited usage!**
                Powered by Llama, Mistral, Phi-3, DeepSeek, and Gemma models.
                """
            )
            
            # Status indicator
            with gr.Row():
                status = gr.Textbox(
                    value="🔄 Initializing OmniMind...",
                    label="Status",
                    interactive=False
                )
                init_btn = gr.Button("🚀 Initialize OmniMind", variant="primary")
            
            # Main tabs
            with gr.Tabs():
                # Chat Tab
                with gr.TabItem("💬 Chat"):
                    gr.Markdown("### Have a conversation with OmniMind")
                    
                    chatbot = gr.Chatbot(
                        elem_classes=["chat-window"],
                        show_label=False
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            placeholder="Ask anything... OmniMind remembers everything!",
                            label="Your Message",
                            lines=2,
                            scale=4
                        )
                        
                    with gr.Row():
                        model_selector = gr.Dropdown(
                            choices=['llama3.2:3b', 'mistral:7b', 'phi3:mini', 'deepseek-coder:6.7b', 'gemma2:2b'],
                            value='llama3.2:3b',
                            label="Select Model",
                            info="Choose which local model to use"
                        )
                        consensus_check = gr.Checkbox(
                            label="Use Multi-Model Consensus",
                            value=False,
                            info="Query multiple models for better answers (slower)"
                        )
                    with gr.Row():
                        submit_btn = gr.Button("Send", variant="primary")
                        clear_btn = gr.Button("Clear Chat")
                    
                    # Chat functionality
                    submit_btn.click(
                        fn=self.process_message,
                        inputs=[msg, chatbot, model_selector, consensus_check],
                        outputs=[chatbot, status]
                    ).then(
                        lambda: "",
                        outputs=[msg]
                    )
                    
                    msg.submit(
                        fn=self.process_message,
                        inputs=[msg, chatbot, model_selector, consensus_check],
                        outputs=[chatbot, status]
                    ).then(
                        lambda: "",
                        outputs=[msg]
                    )
                    
                    clear_btn.click(lambda: [], outputs=[chatbot])
                
                # Search Tab
                with gr.TabItem("🔍 Search"):
                    gr.Markdown("### Search through your memories semantically")
                    
                    with gr.Row():
                        search_input = gr.Textbox(
                            placeholder="Search for memories...",
                            label="Search Query",
                            scale=3
                        )
                        search_limit = gr.Slider(
                            minimum=1,
                            maximum=50,
                            value=10,
                            step=1,
                            label="Max Results"
                        )
                        search_btn = gr.Button("Search", variant="primary")
                    
                    search_results = gr.DataFrame(
                        headers=["Score", "Date", "Content", "Type"],
                        label="Search Results"
                    )
                    
                    search_btn.click(
                        fn=self.search_memories,
                        inputs=[search_input, search_limit],
                        outputs=[search_results]
                    )
                
                # Timeline Tab
                with gr.TabItem("📅 Timeline"):
                    gr.Markdown("### View memories from specific time periods")
                    
                    with gr.Row():
                        start_date = gr.Textbox(
                            placeholder="YYYY-MM-DD",
                            label="Start Date"
                        )
                        end_date = gr.Textbox(
                            placeholder="YYYY-MM-DD",
                            label="End Date"
                        )
                        timeline_btn = gr.Button("Get Timeline", variant="primary")
                    
                    timeline_results = gr.DataFrame(
                        headers=["Timestamp", "Thought", "Project", "Tags"],
                        label="Timeline"
                    )
                    
                    timeline_btn.click(
                        fn=self.get_timeline,
                        inputs=[start_date, end_date],
                        outputs=[timeline_results]
                    )
                
                # Knowledge Graph Tab
                with gr.TabItem("🕸️ Knowledge Graph"):
                    gr.Markdown("### Visualize how your thoughts connect")
                    
                    refresh_graph_btn = gr.Button("🔄 Refresh Graph", variant="primary")
                    graph_plot = gr.Plot(label="Knowledge Graph")
                    
                    refresh_graph_btn.click(
                        fn=self.visualize_knowledge_graph,
                        outputs=[graph_plot]
                    )
                
                # Settings Tab
                with gr.TabItem("⚙️ Settings"):
                    gr.Markdown("### OmniMind Configuration")
                    
                    gr.Markdown(
                        """
                        **Data Storage:**
                        - ChromaDB: `./data/chromadb/`
                        - SQLite: `./data/sqlite/omnimind.db`
                        - Knowledge Graph: `./data/graphs/`
                        
                        **Available Local Models (FREE!):**
                        - 🦙 Llama 3.2 (3B) - Fast general purpose
                        - 🧙 Mistral (7B) - Best reasoning
                        - 🔮 Phi-3 Mini - Microsoft's efficient model
                        - 💻 DeepSeek Coder (6.7B) - Best for code
                        - 💎 Gemma 2 (2B) - Google's fast model
                        
                        **Privacy:**
                        - ✅ 100% Local Processing
                        - ✅ No Data Leaves Your Machine
                        - ✅ No API Keys Required
                        """
                    )
                    
                    with gr.Row():
                        export_btn = gr.Button("💾 Export Memories")
                        backup_btn = gr.Button("🔄 Backup Data")
                        
                    export_status = gr.Textbox(label="Export Status", interactive=False)
                    
                    def export_memories():
                        return "Export functionality coming soon!"
                    
                    def backup_data():
                        return "Backup functionality coming soon!"
                    
                    export_btn.click(fn=export_memories, outputs=[export_status])
                    backup_btn.click(fn=backup_data, outputs=[export_status])
            
            # Initialize button
            init_btn.click(
                fn=self.initialize_omnimind,
                outputs=[status]
            )
            
            # Auto-initialize on load
            interface.load(
                fn=self.initialize_omnimind,
                outputs=[status]
            )
        
        return interface


def main():
    """Launch the web UI."""
    print("🧠 Starting OmniMind Web UI...")
    print("=" * 50)
    
    # Create and launch interface
    ui = OmniMindWebUI()
    interface = ui.create_interface()
    
    # Launch with options
    interface.launch(
        server_name="0.0.0.0",  # Allow network access
        server_port=7860,        # Default Gradio port
        share=False,             # Set to True for public URL
        inbrowser=True,          # Open browser automatically
        favicon_path=None,       # Could add a brain emoji favicon
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    main()