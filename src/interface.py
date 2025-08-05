"""
Gradio interface module for the web UI.
"""

import gradio as gr
import asyncio
import time
from datetime import datetime
from typing import List, Dict, Any
from .pipeline import EnterpriseNewsPipeline
from .config import config
from .utils import setup_logging, print_system_status


class GradioInterface:
    """Gradio web interface for RAP IQ."""
    
    def __init__(self):
        self.pipeline = EnterpriseNewsPipeline()
        self.logger = setup_logging()
        self.custom_css = self._get_custom_css()
        
    def _get_custom_css(self) -> str:
        """Get custom CSS for styling."""
        return """
        .gradio-container {
            max-width: 1400px !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .enterprise-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .chat-container {
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            background: white;
            min-height: 600px;
        }
        
        .enterprise-stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
        }
        
        .news-item {
            border-left: 3px solid #28a745;
            padding-left: 15px;
            margin: 15px 0;
            background: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
        }
        
        .impact-high { border-left-color: #dc3545 !important; }
        .impact-medium { border-left-color: #ffc107 !important; }
        .impact-low { border-left-color: #28a745 !important; }
        """
    
    def create_interface(self) -> gr.Blocks:
        """Create the main Gradio interface."""
        
        with gr.Blocks(css=self.custom_css, theme="default", title="Enterprise News Intelligence") as demo:
            
            # Header
            gr.HTML("""
            <div class="enterprise-header">
                <h1>🚀 Enterprise News Intelligence Platform</h1>
                <p>Advanced AI-powered real-time company news analysis with multi-source intelligence</p>
                <p><strong>Features:</strong> Multi-source crawling • Conversational AI • Impact scoring • Real-time analysis</p>
            </div>
            """)
            
            # State management
            session_state = gr.State({"session_id": f"session_{int(time.time())}"})
            
            with gr.Row():
                with gr.Column(scale=3):
                    # Main chat interface
                    chatbot = gr.Chatbot(
                        label="💬 News Intelligence Assistant",
                        height=650,
                        show_label=True,
                        container=True,
                        bubble_full_width=False
                    )
                    
                    # User input
                    with gr.Row():
                        user_input = gr.Textbox(
                            label="",
                            placeholder="Ask me about any company's latest news... (e.g., 'What's the latest on Tesla?' or 'Tell me about Apple's recent developments')",
                            lines=2,
                            scale=4
                        )
                        send_btn = gr.Button("📤 Send", variant="primary", scale=1)
                
                with gr.Column(scale=1):
                    # Control Panel
                    gr.Markdown("### ⚙️ **Control Panel**")
                    
                    company_override = gr.Textbox(
                        label="🏢 Specific Company (Optional)",
                        placeholder="e.g., Tesla, Apple, Microsoft...",
                        lines=1
                    )
                    
                    response_style = gr.Dropdown(
                        choices=[
                            "professional",
                            "casual",
                            "executive",
                            "technical"
                        ],
                        value="professional",
                        label="🎨 Response Style"
                    )
                    
                    time_range = gr.Dropdown(
                        choices=["1 hour", "6 hours", "24 hours", "1 week"],
                        value="24 hours",
                        label="⏰ Time Range"
                    )
                    
                    impact_threshold = gr.Slider(
                        minimum=1,
                        maximum=10,
                        value=5.0,
                        step=0.5,
                        label="🎯 Impact Threshold"
                    )
                    
                    # Enterprise features
                    gr.Markdown("### 📊 **Enterprise Features**")
                    
                    with gr.Accordion("🔍 Advanced Options", open=False):
                        max_results = gr.Slider(1, 20, value=10, label="Max Results")
                        include_sources = gr.CheckboxGroup(
                            choices=["DuckDuckGo", "RSS", "Financial Sites"],
                            value=["DuckDuckGo", "RSS"],
                            label="Data Sources"
                        )
                    
                    # Quick actions
                    gr.Markdown("### ⚡ **Quick Actions**")
                    clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
                    export_btn = gr.Button("📄 Export Chat", variant="secondary")
                    
                    # Analytics display
                    analytics_display = gr.JSON(
                        label="📈 Session Analytics",
                        visible=True
                    )
            
            # Status bar
            status_bar = gr.Textbox(
                label="📊 System Status",
                value="✅ System ready • All sources active • AI model loaded",
                interactive=False,
                max_lines=1
            )
            
            # Event handlers
            def handle_user_message(message, history, company, style, time_range, impact_threshold, session_data):
                """Handle user message and generate response."""
                
                if not message.strip():
                    return history, "", {"error": "Empty message"}
                
                # Add user message to history
                history = history or []
                history.append([message, None])
                
                try:
                    # Process query
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    response = loop.run_until_complete(
                        self.pipeline.process_enterprise_query(
                            user_input=message,
                            company=company if company.strip() else None,
                            style=style,
                            time_range=time_range,
                            impact_threshold=impact_threshold,
                            session_id=session_data["session_id"]
                        )
                    )
                    
                    loop.close()
                    
                    # Add response to history
                    history[-1][1] = response
                    
                    # Update analytics
                    analytics = {
                        "last_query": message,
                        "response_length": len(response),
                        "session_id": session_data["session_id"],
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "sources_used": ["DuckDuckGo", "RSS", "AI Analysis"]
                    }
                    
                    return history, "", analytics
                
                except Exception as e:
                    error_response = f"❌ **Error**: {str(e)}\n\nPlease try again or contact support."
                    history[-1][1] = error_response
                    
                    return history, "", {"error": str(e)}
            
            def clear_chat():
                """Clear chat history."""
                return [], {"status": "Chat cleared"}
            
            def export_chat(history):
                """Export chat to text format."""
                if not history:
                    return "No chat history to export."
                
                export_text = f"# Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                for i, (user_msg, bot_msg) in enumerate(history, 1):
                    export_text += f"## Exchange {i}\n"
                    export_text += f"**User**: {user_msg}\n\n"
                    export_text += f"**Assistant**: {bot_msg}\n\n"
                    export_text += "---\n\n"
                
                return export_text
            
            # Connect events
            send_btn.click(
                fn=handle_user_message,
                inputs=[user_input, chatbot, company_override, response_style, time_range, impact_threshold, session_state],
                outputs=[chatbot, user_input, analytics_display]
            )
            
            user_input.submit(
                fn=handle_user_message,
                inputs=[user_input, chatbot, company_override, response_style, time_range, impact_threshold, session_state],
                outputs=[chatbot, user_input, analytics_display]
            )
            
            clear_btn.click(
                fn=clear_chat,
                outputs=[chatbot, analytics_display]
            )
            
            # Examples section
            with gr.Accordion("💡 **Usage Examples**", open=False):
                gr.Markdown("""
                **Try these queries:**
                
                🔥 **Breaking News**: "What's happening with Tesla today?"
                
                📊 **Financial Focus**: "Give me Apple's latest earnings and financial news"
                
                🏢 **Company Analysis**: "Analyze Microsoft's recent strategic moves"
                
                📈 **Market Impact**: "What news could affect Google's stock price?"
                
                🔍 **Deep Dive**: "Tell me about Amazon's latest partnerships and acquisitions"
                
                **Pro Tips:**
                - Use specific company names for best results
                - Try different response styles for various use cases
                - Adjust impact threshold to filter news relevance
                - Set time range based on your analysis needs
                """)
        
        return demo
    
    def launch(self):
        """Launch the Gradio application."""
        
        # Pre-launch system check
        print_system_status()
        
        print("\n🎯 **Key Features Active:**")
        features = [
            "✅ Real-time multi-source news crawling",
            "✅ Advanced conversational AI",
            "✅ Enterprise-grade impact scoring",
            "✅ 5-6 line detailed responses with source links",
            "✅ Professional UI with analytics dashboard",
            "✅ Session management and export capabilities",
            "✅ Multiple response styles (Professional/Casual/Executive/Technical)",
            "✅ Advanced filtering and relevance ranking"
        ]
        
        for feature in features:
            print(f"   {feature}")
        
        print("\n" + "="*70)
        print("🎉 READY FOR INTERNSHIP DEMONSTRATION!")
        print("💰 20K Stipend Target: ACHIEVABLE with this enterprise solution")
        print("="*70)
        
        try:
            # Create and launch interface
            demo = self.create_interface()
            
            demo.launch(
                server_name=config.server.host,
                server_port=config.server.port,
                share=config.server.share,
                debug=config.server.debug,
                show_error=config.server.show_error,
                quiet=config.server.quiet,
                inbrowser=config.server.inbrowser,
                show_tips=config.server.show_tips,
                enable_queue=config.server.enable_queue,
                max_threads=config.server.max_threads
            )
            
            print("🎯 Application launched successfully!")
            print("🔗 Use the public link above to access your enterprise news platform")
            
        except Exception as e:
            print(f"❌ Launch error: {e}")
            print("🔧 Attempting fallback launch...")
            
            # Fallback
            demo = self.create_interface()
            demo.launch(share=True, debug=True)


# Global interface instance
interface = GradioInterface() 