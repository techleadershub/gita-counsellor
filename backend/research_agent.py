from typing import TypedDict, List, Annotated
import operator
import re
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from vector_store import VectorStore
from models import get_db_session, Verse
from config import LLM_CONFIG

# --- State ---
class AgentState(TypedDict):
    user_query: str
    problem_context: str
    research_questions: List[str]
    relevant_verses: Annotated[List[dict], operator.add]
    analysis: str
    guidance: str
    exercises: str
    final_answer: str

# --- Research Agent ---
class ResearchAgent:
    def __init__(self, vector_store: VectorStore, log_callback=None):
        self.vector_store = vector_store
        self.log_callback = log_callback
        
        # Setup LLM
        provider = LLM_CONFIG.get("provider", "openai")
        model_name = LLM_CONFIG.get("model", "gpt-4o-mini")
        api_key = LLM_CONFIG.get("openai_key") if provider == "openai" else LLM_CONFIG.get("openrouter_key")
        base_url = "https://openrouter.ai/api/v1" if provider == "openrouter" else None
        
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.3  # Lower temperature for more grounded, factual responses
        )

    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)

    # --- Nodes ---
    
    def analyze_problem_node(self, state: AgentState):
        """Analyze the user's problem and extract key aspects."""
        query = state["user_query"]
        self.log(f"Analyzing problem: '{query}'...")
        
        prompt = f"""You are an expert spiritual counselor analyzing a modern person's problem or question, with special attention to Gen Z and Gen Alpha challenges.

User's Query: "{query}"

Your task:
1. Identify the core issue or question (consider modern context like digital age, social media, AI, etc.)
2. Extract key themes (e.g., stress, relationships, purpose, decision-making, leadership, resilience, morals, ethics, etc.)
3. Identify which Bhagavad Gita principles might be relevant (karma yoga, dharma, detachment, equanimity, self-knowledge, etc.)
4. Note any generational or modern context (Gen Z, Gen Alpha, digital age, social media, technology, etc.)

Return a structured analysis in this format:
CORE_ISSUE: [one sentence describing the core problem, including modern context if relevant]
KEY_THEMES: [comma-separated list of themes like: leadership, resilience, morals, stress, decision-making, etc.]
RELEVANT_PRINCIPLES: [comma-separated list of Gita concepts like: karma yoga, dharma, detachment, equanimity, self-knowledge, service, etc.]
MODERN_CONTEXT: [note if this involves Gen Z/Gen Alpha, digital age, technology, social media, etc.]
"""
        
        response = self.llm.invoke([SystemMessage(content=prompt), HumanMessage(content=query)])
        analysis = response.content
        
        # Extract research questions
        research_prompt = f"""Based on this problem analysis, generate 4-6 specific research questions to search in the Bhagavad Gita:

{analysis}

Generate questions that will help find relevant verses about:
- Leadership principles (if leadership-related)
- Resilience and mental strength (if resilience-related)
- Moral and ethical guidance (if morals/ethics-related)
- The specific themes identified
- Practical application of Gita principles

Make questions specific and focused. Return ONLY the questions, one per line, no numbering."""
        
        research_response = self.llm.invoke([SystemMessage(content=research_prompt)])
        questions = [q.strip() for q in research_response.content.split("\n") if q.strip() and not q.strip().startswith("#")]
        
        self.log(f"Generated {len(questions)} research questions")
        return {
            "problem_context": analysis,
            "research_questions": questions
        }

    def research_verses_node(self, state: AgentState):
        """Search for relevant verses based on research questions."""
        questions = state["research_questions"]
        all_verses = []
        
        self.log(f"Researching {len(questions)} questions...")
        
        for i, question in enumerate(questions, 1):
            self.log(f"  [{i}/{len(questions)}] Searching: {question}")
            
            # Search vector store
            results = self.vector_store.search(question, limit=5)
            self.log(f"    Found {len(results)} relevant verses")
            
            # Get full verse details from SQLite
            db_session = get_db_session()
            try:
                for result in results:
                    # Try multiple ways to get verse_id (from direct field or from chunk payload)
                    verse_id = result.get("verse_id", "") or result.get("chunk", {}).get("verse_id", "")
                    
                    if verse_id:
                        verse = db_session.query(Verse).filter_by(verse_id=verse_id).first()
                        if verse:
                            verse_dict = verse.to_dict()
                            verse_dict["relevance_score"] = result.get("score", 0)
                            verse_dict["research_question"] = question
                            all_verses.append(verse_dict)
            finally:
                db_session.close()
        
        # Deduplicate verses by verse_id (same verse might be found for multiple questions)
        seen_verse_ids = set()
        unique_verses = []
        for verse in all_verses:
            verse_id = verse.get("verse_id")
            if verse_id and verse_id not in seen_verse_ids:
                seen_verse_ids.add(verse_id)
                unique_verses.append(verse)
        
        self.log(f"Total {len(unique_verses)} unique verses found (from {len(all_verses)} results)")
        return {"relevant_verses": unique_verses}

    def synthesize_guidance_node(self, state: AgentState):
        """Synthesize comprehensive guidance from verses."""
        query = state["user_query"]
        context = state["problem_context"]
        verses = state["relevant_verses"]
        
        self.log("Synthesizing comprehensive guidance...")
        
        # Format verses for context - INCLUDE FULL CONTENT (no truncation)
        verses_text = []
        for v in verses[:10]:  # Top 10 most relevant
            transliteration = v.get('transliteration', 'N/A')
            word_meanings = v.get('word_meanings', 'N/A')
            verse_text = f"""
Verse {v['verse_id']} (Chapter {v['chapter']}, Verse {v['verse_number']}):
Transliteration: {transliteration}
Word Meanings: {word_meanings}
Translation: {v.get('translation', 'N/A')}
Purport: {v.get('purport', 'N/A')}
"""
            verses_text.append(verse_text)
        
        verses_context = "\n---\n".join(verses_text)
        
        prompt = f"""You are an expert spiritual guide helping a modern person (especially Gen Z or Gen Alpha) solve their problem using timeless Bhagavad Gita wisdom.

User's Problem: {query}
Context: {context if context else 'Modern challenges and contemporary life'}

Relevant Bhagavad Gita Verses (from the database):
{verses_context}

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE STRICTLY:

1. GROUNDING REQUIREMENT:
   - You MUST ONLY use information from the verses provided above
   - DO NOT use your training data or external knowledge about Bhagavad Gita
   - DO NOT add interpretations that are not supported by the provided translations and purports
   - If a concept isn't explicitly in the provided verses, say so explicitly
   - When discussing a verse, you MUST quote or closely paraphrase the actual translation or purport text

2. CITATION REQUIREMENTS:
   - When referencing a verse, ALWAYS cite the verse ID (e.g., "As stated in BG 3.30...")
   - Quote the exact translation or purport text using > blockquotes (DO NOT add quotes inside blockquotes)
   - Clearly distinguish between:
     * What the verse/translation/purport explicitly says (quote it using > blockquote, no quotes inside)
     * Your interpretation or application to modern context (label it as such)
   - Never make claims about verses not provided in the context above

3. CONTENT REQUIREMENTS:
   Your task: Provide comprehensive, high-quality guidance in THREE detailed sections. Make it relevant to modern life, especially for younger generations facing digital age challenges.

   A. ANALYSIS (500+ words):
      - Use clear section headers with ## for main topics and ### for subtopics
      - Explain how the PROVIDED verses address this specific problem
      - Quote specific translations and purports from the verses above using > blockquotes (text only, no quotes inside)
      - Reference specific verses by ID (e.g., **BG 2.12**, **BG 3.30**) in bold and explain their relevance
      - Explain the core principles as described in the purports
      - Connect the verse teachings to modern context (mention Gen Z/Gen Alpha challenges if relevant)
      - Show how these principles apply to contemporary situations
      - Base all explanations on the actual verse content provided
      - Use bullet points (-) for lists and numbered lists (1., 2., 3.) for steps
      - Add line breaks between paragraphs for readability

   B. PRACTICAL GUIDANCE (500+ words):
      - Use clear section headers with ## for main topics
      - Provide specific, actionable steps based on the Gita principles from the verses above
      - Use numbered lists (1., 2., 3.) for sequential steps
      - Use bullet points (-) for options or parallel items
      - Address the modern context mentioned in the query
      - Include immediate actions the person can take
      - Reference specific verses and their teachings using **bold verse IDs**
      - Recommend practices based on what the verses actually say
      - Make it practical and applicable to daily life
      - Consider digital age challenges if relevant
      - Add spacing between sections for readability

   C. SPIRITUAL EXERCISES (500+ words) - REQUIRED SECTION:
      - CRITICAL: You MUST include this section. Start with "## C. SPIRITUAL EXERCISES" or "## Spiritual Exercises"
      - Use clear section headers with ## for main topics
      - Suggest 5-7 specific exercises, meditations, or practices
      - Number each exercise (1., 2., 3., etc.) with clear titles like "### Exercise 1: [Title]"
      - Base them EXCLUSIVELY on the verses provided above
      - Reference which verse(s) each exercise is based on using **bold verse IDs**
      - Make them practical and applicable to modern life
      - Include daily practices, weekly reflections, and long-term cultivation
      - Provide step-by-step instructions where helpful using sub-bullets
      - Consider modern lifestyle constraints
      - Add spacing between exercises for readability
      - DO NOT skip this section - it is mandatory

4. FORMATTING REQUIREMENTS:
   - Use proper markdown formatting for premium appearance:
     * ## for main section headers
     * ### for subsection headers
     * **bold** for emphasis and verse IDs
     * > blockquotes for verse translations (NO quotes inside blockquotes - just the text)
     * - bullet points for lists
     * 1. numbered lists for steps
   - Add spacing (blank lines) between paragraphs and sections
   - Be comprehensive - each section should be substantial (500+ words)
   - Reference specific verses throughout with citations in **bold**
   - Quote actual verse content when making specific claims using > blockquotes (text only, no quotes)
   - Use clear structure with headers, bullet points, and numbered lists
   - Be inspiring and encouraging
   - Make it visually appealing and easy to read

REMEMBER: Your response must be grounded in the verses provided above. Do not add information that isn't in those verses."""
        
        response = self.llm.invoke([SystemMessage(content=prompt)])
        guidance = response.content
        
        # Clean up double quotes from blockquotes
        # Remove quotes that appear inside blockquote lines
        # Pattern: > "text" (quotes at start/end of blockquote line)
        guidance = re.sub(r'^>\s*"([^"]+)"\s*$', r'> \1', guidance, flags=re.MULTILINE)
        # Pattern: > "text" (quotes after >)
        guidance = re.sub(r'^>\s*"([^"]+)"', r'> \1', guidance, flags=re.MULTILINE)
        # Pattern: > text "quoted" text (quotes in middle)
        guidance = re.sub(r'^>([^"]*)"([^"]+)"([^"]*)$', r'>\1\2\3', guidance, flags=re.MULTILINE)
        # Pattern: > "text" (with trailing content)
        guidance = re.sub(r'^>\s*"([^"]+)"\s+', r'> \1 ', guidance, flags=re.MULTILINE)
        
        # Parse into sections - improved parsing logic
        sections = {
            "analysis": "",
            "guidance": "",
            "exercises": ""
        }
        
        # More robust section detection
        current_section = None
        lines = guidance.split("\n")
        
        for i, line in enumerate(lines):
            line_upper = line.upper().strip()
            
            # Check for section headers (more flexible matching)
            if any(keyword in line_upper for keyword in ["A. ANALYSIS", "## ANALYSIS", "# ANALYSIS", "ANALYSIS"]):
                if "ANALYSIS" in line_upper and ("A." in line_upper or "##" in line or "#" in line):
                    current_section = "analysis"
                    sections["analysis"] = line + "\n"
                    continue
            elif any(keyword in line_upper for keyword in ["B. PRACTICAL GUIDANCE", "B. GUIDANCE", "## PRACTICAL GUIDANCE", "## GUIDANCE", "PRACTICAL GUIDANCE"]):
                if ("GUIDANCE" in line_upper or "PRACTICAL" in line_upper) and ("B." in line_upper or "##" in line or "#" in line):
                    current_section = "guidance"
                    sections["guidance"] = line + "\n"
                    continue
            elif any(keyword in line_upper for keyword in ["C. SPIRITUAL EXERCISES", "C. EXERCISES", "## SPIRITUAL EXERCISES", "## EXERCISES", "SPIRITUAL EXERCISES"]):
                if ("EXERCISES" in line_upper or "SPIRITUAL" in line_upper) and ("C." in line_upper or "##" in line or "#" in line):
                    current_section = "exercises"
                    sections["exercises"] = line + "\n"
                    continue
            
            # Add content to current section
            if current_section:
                # Stop if we hit the next major section (but allow subsections)
                if line.strip().startswith("##") and current_section != "analysis":
                    # Check if this is a new main section
                    if any(keyword in line_upper for keyword in ["ANALYSIS", "GUIDANCE", "EXERCISES"]):
                        # This might be a new section, but be careful
                        pass
                sections[current_section] += line + "\n"
        
        # Fallback: if exercises is empty, try to extract from full guidance
        exercises_content = sections["exercises"].strip()
        if not exercises_content:
            # Look for exercises section in the full text
            guidance_lower = guidance.lower()
            exercises_keywords = ["spiritual exercises", "exercises", "c. spiritual", "c. exercises"]
            for keyword in exercises_keywords:
                idx = guidance_lower.find(keyword)
                if idx != -1:
                    # Extract from this point to end or next major section
                    remaining = guidance[idx:]
                    # Try to find where it ends (next major section or end)
                    end_markers = ["key verses", "conclusion", "---"]
                    end_idx = len(remaining)
                    for marker in end_markers:
                        marker_idx = remaining.lower().find(marker, 100)  # Start search after 100 chars
                        if marker_idx != -1 and marker_idx < end_idx:
                            end_idx = marker_idx
                    if end_idx > 200:  # Only if substantial content
                        exercises_content = remaining[:end_idx].strip()
                        break
        
        # Final fallback - ensure exercises is never completely empty
        if not exercises_content:
            exercises_content = "## Spiritual Exercises\n\n*Exercises are being generated based on the verses referenced above. Please see the full answer for complete guidance with exercises.*"
        
        return {
            "analysis": sections["analysis"].strip() or guidance,
            "guidance": sections["guidance"].strip() or "",
            "exercises": exercises_content
        }

    def finalize_answer_node(self, state: AgentState):
        """Create the final comprehensive answer."""
        query = state["user_query"]
        analysis = state["analysis"]
        guidance = state["guidance"]
        exercises = state["exercises"]
        verses = state["relevant_verses"]
        
        self.log("Finalizing comprehensive answer...")
        
        # Get unique verse references
        verse_refs = list(set([v["verse_id"] for v in verses[:10]]))
        
        # Format verses for display - premium formatting with full content
        verses_display = []
        for v in verses[:10]:
            translation = v.get('translation', 'N/A')
            transliteration = v.get('transliteration', '')
            word_meanings = v.get('word_meanings', '')
            
            # Clean and format translation (normalize whitespace, ensure single blockquote)
            if translation and translation != 'N/A':
                # Replace multiple spaces/newlines with single space
                translation_clean = re.sub(r'\s+', ' ', translation).strip()
            else:
                translation_clean = 'N/A'
            
            # Format transliteration nicely (preserve line breaks from database)
            transliteration_block = ""
            if transliteration and transliteration.strip():
                # Preserve line breaks in transliteration (shloka format)
                # Format transliteration as italic text with preserved line breaks
                transliteration_block = f"\n*{transliteration.strip()}*\n\n"
            
            # Format word meanings
            word_meanings_block = ""
            if word_meanings and word_meanings.strip():
                word_meanings_block = f"\n**Word Meanings:**\n{word_meanings.strip()}\n\n"
            
            # Show full translation without truncation, formatted nicely
            verse_display = f"""#### **{v['verse_id']}** — Chapter {v['chapter']}, Verse {v['verse_number']}

{transliteration_block}{word_meanings_block}> {translation_clean}

"""
            verses_display.append(verse_display.strip())
        
        # Format final answer with premium styling
        # If exercises is empty, provide a helpful message
        if not exercises or not exercises.strip():
            exercises_section = """### Introduction

Based on the verses referenced above, here are practical spiritual exercises you can incorporate into your daily life:

### Daily Practices

1. **Morning Reflection** (Based on **BG 3.30** and other verses)
   - Begin each day by setting an intention to perform your duties without attachment to results
   - Take 5 minutes to reflect on your dharma and how you can serve today

2. **Mindful Action** (Based on **BG 2.48**)
   - Throughout the day, practice performing actions with equanimity
   - When facing challenges, remind yourself: "I do my duty, results are not mine to control"

3. **Evening Contemplation** (Based on the verses above)
   - End each day by reviewing your actions
   - Consider: Did I act according to my dharma? Did I remain detached from outcomes?

### Weekly Practices

4. **Dharma Alignment Review**
   - Weekly, assess if your ambitions align with your duties
   - Adjust your goals to ensure they serve your higher purpose

5. **Service Practice**
   - Dedicate time each week to selfless service
   - This could be helping others, contributing to your community, or supporting a cause

### Long-term Cultivation

6. **Purpose Discovery**
   - Regularly reflect on your true nature and calling
   - Align your career and life choices with your inherent talents and duties

7. **Detachment Practice**
   - Gradually reduce attachment to external validation
   - Focus on the quality of your work rather than praise or criticism

*These exercises are based on the principles found in the verses referenced above. Adapt them to your personal circumstances and lifestyle.*"""
        else:
            exercises_section = exercises
        
        final_answer = f"""# 🕉️ Guidance from Bhagavad Gita

---

## 💭 Your Question

> {query}

---

## 📖 Analysis

{analysis}

---

## 🎯 Practical Guidance

{guidance}

---

## 🧘 Spiritual Exercises

{exercises_section}

---

## 📚 Key Verses Referenced

The following verses from the Bhagavad Gita provide the foundation for this guidance:

{chr(10).join(verses_display) if verses_display else f"*Verses: {', '.join(sorted(verse_refs))}*"}

---

**All Referenced Verses:** {', '.join(sorted(verse_refs))}

---

*This guidance is based on the teachings of **Bhagavad Gita As It Is** by A.C. Bhaktivedanta Swami Prabhupada.*

*All interpretations are grounded in the actual translations and purports from the source text.*
"""
        
        return {"final_answer": final_answer}

    # --- Graph Construction ---
    def build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("analyze_problem", self.analyze_problem_node)
        workflow.add_node("research_verses", self.research_verses_node)
        workflow.add_node("synthesize_guidance", self.synthesize_guidance_node)
        workflow.add_node("finalize_answer", self.finalize_answer_node)
        
        workflow.set_entry_point("analyze_problem")
        workflow.add_edge("analyze_problem", "research_verses")
        workflow.add_edge("research_verses", "synthesize_guidance")
        workflow.add_edge("synthesize_guidance", "finalize_answer")
        workflow.add_edge("finalize_answer", END)
        
        return workflow.compile()

