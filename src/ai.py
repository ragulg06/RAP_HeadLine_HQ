"""
AI module for conversational AI and response generation.
"""

import torch
from datetime import datetime
from typing import List, Dict, Optional
from .models import model_manager
from .config import config


class ResponseGenerator:
    """Generate styled responses using LLM."""
    
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.style_prompts = {
            "📊 Formal business summary": "Provide a formal, professional business summary of the following news:",
            "💬 Casual conversation": "Give me a casual, friendly summary of this news like you're talking to a friend:",
            "📋 Quick bullet points": "Summarize this news in concise bullet points:",
            "📈 Executive briefing": "Create an executive briefing focusing on business impact:",
            "🔍 Technical analysis": "Provide a detailed technical analysis of the news:"
        }
    
    def generate_summary(self, news_items: List[Dict], style: str, company: str) -> str:
        """Generate styled summary from news items."""
        
        if not news_items:
            return f"No recent news found for {company}. Please try again or check the company name."
        
        # Prepare context
        news_context = self._prepare_news_context(news_items)
        
        # Get style prompt
        style_prompt = self.style_prompts.get(style, self.style_prompts["📊 Formal business summary"])
        
        # Create full prompt
        full_prompt = f"""
{style_prompt}

Company: {company}
News Updates:
{news_context}

Please provide a comprehensive summary with source links included. Do not answer any other queries that are not related to company news or company live events.
"""
        
        try:
            # Generate response
            inputs = self.tokenizer.encode(full_prompt, return_tensors='pt', truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            
            # Clean and format response
            formatted_response = self._format_response(response, news_items, style)
            return formatted_response
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            # Fallback to template-based response
            return self._generate_template_response(news_items, style, company)
    
    def _prepare_news_context(self, news_items: List[Dict]) -> str:
        """Prepare news context for LLM."""
        context = ""
        for i, item in enumerate(news_items[:5], 1):  # Limit to top 5
            context += f"""
{i}. {item['title']}
   Source: {item['source']} | Impact: {item['impact_score']:.1f}/10
   URL: {item['url']}
   """
        return context
    
    def _format_response(self, response: str, news_items: List[Dict], style: str) -> str:
        """Format the response with proper styling and links."""
        
        # Add news links at the end
        links_section = "\n\n**📎 Source Links:**\n"
        for i, item in enumerate(news_items[:5], 1):
            links_section += f"{i}. [{item['title'][:60]}...]({item['url']})\n"
        
        return response + links_section
    
    def _generate_template_response(self, news_items: List[Dict], style: str, company: str) -> str:
        """Fallback template-based response."""
        
        if "bullet points" in style.lower():
            response = f"## 📋 Latest News for {company}:\n\n"
            for item in news_items[:5]:
                response += f"• **{item['title']}** (Impact: {item['impact_score']:.1f}/10)\n"
                response += f"  *Source: {item['source']}* - [Read More]({item['url']})\n\n"
        
        elif "casual" in style.lower():
            response = f"## 💬 Hey! Here's what's happening with {company}:\n\n"
            for item in news_items[:3]:
                response += f"**{item['title']}** - This seems pretty important (impact score: {item['impact_score']:.1f}/10). "
                response += f"You can [check it out here]({item['url']}).\n\n"
        
        else:  # Formal
            response = f"## 📊 Business Summary for {company}\n\n"
            response += f"Based on recent news analysis, here are the key developments:\n\n"
            for item in news_items[:5]:
                response += f"**{item['title']}**\n"
                response += f"Impact Assessment: {item['impact_score']:.1f}/10 | Source: {item['source']}\n"
                response += f"[Full Article]({item['url']})\n\n"
        
        return response


class ConversationalAI:
    """Enterprise-level conversational AI with Mistral."""
    
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.context_window = config.model.context_window
    
    def generate_conversational_response(self, user_input: str, news_data: List[Dict] = None, style: str = "professional") -> str:
        """Generate conversational response with news context."""
        
        # Build conversation context
        context = self._build_conversation_context(user_input, news_data, style)
        
        try:
            # Use model manager to generate response
            response = model_manager.generate_response(context, config.model.max_tokens)
            
            # Clean and format response
            formatted_response = self._format_conversational_response(response, news_data, style)
            
            # Store in conversation history
            self.conversation_history.append({
                'user': user_input,
                'assistant': formatted_response,
                'timestamp': datetime.now().isoformat(),
                'style': style
            })
            
            return formatted_response
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return self._generate_fallback_response(user_input, news_data, style)
    
    def _build_conversation_context(self, user_input: str, news_data: List[Dict], style: str) -> str:
        """Build rich conversation context."""
        
        # System prompt based on style
        style_prompts = {
            "professional": "You are an expert financial news analyst. Provide detailed, professional insights.",
            "casual": "You are a friendly news assistant. Explain things in a conversational, easy-to-understand way.",
            "executive": "You are a senior business strategist. Focus on strategic implications and business impact.",
            "technical": "You are a financial technology expert. Provide in-depth technical analysis."
        }
        
        system_prompt = style_prompts.get(style, style_prompts["professional"])
        
        # Build context with conversation history
        context = f"""<s>[INST] {system_prompt}

        User: {user_input}

        """
        
        # Add news context if available
        if news_data:
            context += "Recent News Context:\n"
            for i, item in enumerate(news_data[:3], 1):  # Top 3 items
                context += f"{i}. {item['title']}\n   {item.get('snippet', item.get('content', ''))[:150]}...\n   Impact: {item.get('impact_score', 5)}/10\n\n"
        
        # Add conversation history (last 2 exchanges)
        if len(self.conversation_history) > 0:
            context += "Previous conversation:\n"
            for exchange in self.conversation_history[-2:]:
                context += f"User: {exchange['user'][:100]}...\n"
                context += f"Assistant: {exchange['assistant'][:100]}...\n\n"
        
        context += "Provide a detailed response (5-6 lines) with actionable insights and include relevant source links. [/INST]"
        
        return context
    
    def _format_conversational_response(self, response: str, news_data: List[Dict], style: str) -> str:
        """Format response for better presentation."""
        
        # Clean the response
        response = response.strip()
        
        # Ensure minimum length (5-6 lines as requested)
        if len(response.split('\n')) < 3:
            response = self._expand_response(response, news_data, style)
        
        # Add source links
        if news_data:
            response += "\n\n**📚 Sources:**\n"
            for i, item in enumerate(news_data[:5], 1):
                response += f"{i}. [{item['title'][:70]}...]({item['url']}) - Impact: {item.get('impact_score', 5):.1f}/10\n"
        
        return response
    
    def _expand_response(self, short_response: str, news_data: List[Dict], style: str) -> str:
        """Expand short responses to meet 5-6 line requirement."""
        
        expanded = short_response
        
        if news_data:
            # Add analysis based on news data
            high_impact_news = [item for item in news_data if item.get('impact_score', 5) >= 7]
            
            if high_impact_news:
                expanded += f"\n\nKey developments include {len(high_impact_news)} high-impact stories. "
                expanded += f"The most significant appears to be: '{high_impact_news[0]['title']}' "
                expanded += f"with an impact score of {high_impact_news[0].get('impact_score', 5):.1f}/10. "
            
            # Add trend analysis
            content_types = [item.get('content_type', 'General') for item in news_data]
            most_common_type = max(set(content_types), key=content_types.count) if content_types else 'General'
            expanded += f"\n\nCurrent news trends show a focus on {most_common_type.lower()} developments. "
            
            # Add timing context
            recent_count = len([item for item in news_data if 'today' in item.get('search_query', '').lower()])
            if recent_count > 0:
                expanded += f"There are {recent_count} breaking developments from today that require attention. "
            
            # Add strategic insight based on style
            if style == "executive":
                expanded += "\n\nStrategic Implications: Monitor these developments closely as they may impact market positioning and competitive landscape."
            elif style == "technical":
                expanded += "\n\nTechnical Analysis: The volume and sentiment of recent news suggests increased volatility and attention from institutional investors."
        
        return expanded
    
    def _generate_fallback_response(self, user_input: str, news_data: List[Dict], style: str) -> str:
        """Generate fallback response when AI fails."""
        
        if news_data:
            response = f"Based on the latest research, here's what I found:\n\n"
            
            for i, item in enumerate(news_data[:3], 1):
                response += f"**{i}. {item['title']}**\n"
                response += f"{item.get('snippet', item.get('content', ''))[:200]}...\n"
                response += f"Impact Assessment: {item.get('impact_score', 5):.1f}/10 | Source: {item.get('source', 'Unknown')}\n"
                response += f"[Read Full Article]({item['url']})\n\n"
            
            response += "These developments suggest significant market activity. Would you like me to dive deeper into any specific aspect?"
        
        else:
            response = f"I understand you're asking about: {user_input}\n\n"
            response += "I'm currently gathering the latest information from multiple sources including financial news, press releases, and market data. "
            response += "This comprehensive approach ensures you get the most accurate and up-to-date insights. "
            response += "Please specify a company name or ask about a specific topic, and I'll provide detailed analysis with current market context."
        
        return response
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def set_user_preference(self, key: str, value: str):
        """Set user preference."""
        self.user_preferences[key] = value
    
    def get_user_preference(self, key: str, default: str = None) -> str:
        """Get user preference."""
        return self.user_preferences.get(key, default) 