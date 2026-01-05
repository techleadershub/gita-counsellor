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
    def __init__(self, vector_store: VectorStore, log_callback=None, progress_callback=None):
        self.vector_store = vector_store
        self.log_callback = log_callback
        self.progress_callback = progress_callback
        
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
    
    def emit_progress(self, step: str, message: str, details: dict = None):
        """Emit progress update for frontend visualization."""
        if self.progress_callback:
            try:
                # Ensure details is JSON-serializable
                safe_details = {}
                if details:
                    for key, value in details.items():
                        # Convert non-serializable types
                        if isinstance(value, (list, dict, str, int, float, bool, type(None))):
                            # Recursively check nested structures
                            if isinstance(value, list):
                                safe_details[key] = [str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v for v in value]
                            elif isinstance(value, dict):
                                safe_details[key] = {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v for k, v in value.items()}
                            else:
                                safe_details[key] = value
                        else:
                            safe_details[key] = str(value)
                
                self.progress_callback({
                    "step": step,
                    "message": message,
                    "details": safe_details
                })
            except Exception as e:
                # Don't let progress callback errors crash the research
                self.log(f"Error emitting progress: {e}")

    # --- Nodes ---
    
    def analyze_problem_node(self, state: AgentState):
        """Analyze the user's problem and extract key aspects."""
        query = state["user_query"]
        self.log(f"Analyzing problem: '{query}'...")
        self.emit_progress("analyzing", "Analyzing your question and identifying key themes...", {"query": query})
        
        prompt = f"""You are an expert counselor analyzing a modern person's problem or question, providing guidance for diverse seekers including students, professionals, individuals, families, and corporate employees. Use universal, inclusive language that appeals to people of all backgrounds.

User's Query: "{query}"

Your task:
1. Identify the core issue or question (consider modern context like digital age, social media, AI, etc., and different life contexts: academic, professional, personal, family, corporate)
2. Extract key themes (e.g., stress, relationships, purpose, decision-making, leadership, resilience, morals, ethics, career, studies, work-life balance, etc.)
3. Identify which universal principles from the Bhagavad Gita might be relevant (both spiritual and practical: selfless service, divine purpose, detachment, equanimity, self-knowledge, God Consciousness, duty, responsibility, etc.)
4. Note any generational or modern context (Gen Z, Gen Alpha, digital age, social media, technology, etc.) and the type of seeker (student, professional, individual, family member, corporate employee)

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
        self.emit_progress("questions_generated", f"Generated {len(questions)} research questions to explore", {"count": len(questions), "questions": questions})
        return {
            "problem_context": analysis,
            "research_questions": questions
        }

    def research_verses_node(self, state: AgentState):
        """Search for relevant verses based on research questions."""
        questions = state["research_questions"]
        all_verses = []
        
        # Handle empty questions list
        if not questions:
            self.log("No research questions generated")
            self.emit_progress("verses_found", "No research questions to search", {"count": 0})
            return {"relevant_verses": []}
        
        self.log(f"Researching {len(questions)} questions...")
        self.emit_progress("researching", f"Searching through {len(questions)} research questions in the Bhagavad Gita...", {"total": len(questions), "current": 0})
        
        for i, question in enumerate(questions, 1):
            self.log(f"  [{i}/{len(questions)}] Searching: {question}")
            self.emit_progress("searching_verse", f"Searching: {question[:60]}...", {"current": i, "total": len(questions), "question": question})
            
            # Search vector store with error handling
            try:
                results = self.vector_store.search(question, limit=5)
                self.log(f"    Found {len(results)} relevant verses")
            except Exception as e:
                self.log(f"    Error searching for question: {e}")
                continue  # Skip this question and continue with next
            
            # Get full verse details from SQLite
            db_session = get_db_session()
            try:
                for result in results:
                    try:
                        # Try multiple ways to get verse_id (from direct field or from chunk payload)
                        verse_id = result.get("verse_id", "") or result.get("chunk", {}).get("verse_id", "")
                        
                        if verse_id:
                            verse = db_session.query(Verse).filter_by(verse_id=verse_id).first()
                            if verse:
                                verse_dict = verse.to_dict()
                                verse_dict["relevance_score"] = result.get("score", 0)
                                verse_dict["research_question"] = question
                                all_verses.append(verse_dict)
                    except Exception as e:
                        self.log(f"    Error processing verse result: {e}")
                        continue  # Skip this result and continue
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
        self.emit_progress("verses_found", f"Found {len(unique_verses)} relevant verses from the Bhagavad Gita", {"count": len(unique_verses)})
        return {"relevant_verses": unique_verses}

    def synthesize_guidance_node(self, state: AgentState):
        """Synthesize comprehensive guidance from verses."""
        query = state["user_query"]
        context = state["problem_context"]
        verses = state["relevant_verses"]
        
        self.log("Synthesizing comprehensive guidance...")
        self.emit_progress("synthesizing", "Synthesizing comprehensive guidance from the verses...", {"verse_count": len(verses)})
        
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
        
        prompt = f"""You are an expert counselor and guide helping modern people solve their problems using timeless wisdom from the Bhagavad Gita. You provide both spiritual and practical guidance for diverse seekers including students, professionals, individuals, families, and corporate employees. Write in a universal, inclusive style that appeals to people of all backgrounds and faiths, similar to how A.C. Bhaktivedanta Swami Prabhupada wrote in "Science of Self Realization" - using terms like "God Consciousness" and universal principles that resonate with everyone.

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

2. MORAL & ETHICAL GUIDANCE REQUIREMENTS:
   - When addressing questions about relationships, morality, or ethical conduct:
     * ALWAYS reference scriptural injunctions and dharma (righteous duty) as the foundation
     * If verses about scriptural injunctions are provided (e.g., BG 16.23, BG 16.24), you MUST quote and explain them
     * Emphasize that relationships should follow scriptural principles and dharma
     * For questions about relationships outside marriage: Gently but clearly explain that according to scriptural injunctions, relationships should be within the bounds of dharma and scriptural principles
     * If BG 7.11 or similar verses about sex life according to religious principles are provided, quote them and explain that relationships should be for the purpose of dharma, not contrary to it
     * Frame guidance in a compassionate but principled way, explaining the spiritual and practical benefits of following dharma
   - When verses about scriptural injunctions are available, prioritize them in your guidance
   - Always ground moral guidance in the actual verses provided, especially those about following scriptural regulations

3. CITATION REQUIREMENTS:
   - When referencing a verse, ALWAYS cite the verse ID (e.g., "As stated in BG 3.30...")
   - Quote the exact translation or purport text using > blockquotes (DO NOT add quotes inside blockquotes)
   - Clearly distinguish between:
     * What the verse/translation/purport explicitly says (quote it using > blockquote, no quotes inside)
     * Your interpretation or application to modern context (label it as such)
   - Never make claims about verses not provided in the context above
   - When verses about scriptural injunctions (BG 16.23, BG 16.24) or dharma-based relationships (BG 7.11) are provided, you MUST include them in your guidance

4. LANGUAGE & TONE REQUIREMENTS:
   - Use UNIVERSAL, INCLUSIVE spiritual language that appeals to all backgrounds
   - Use terms like "God Consciousness," "Divine Consciousness," "Supreme Consciousness" instead of sectarian terms
   - Refer to "the Supreme," "the Divine," "God" in a way that's accessible to all faiths
   - Use universal concepts like "self-realization," "spiritual growth," "divine purpose"
   - Write in Prabhupada's inclusive style from "Science of Self Realization" - making ancient wisdom accessible to modern, diverse audiences
   - Avoid overly sectarian language while maintaining the essence of the teachings
   - Make it feel welcoming to people of all religious backgrounds or no religious background
   - Focus on universal spiritual principles that everyone can relate to

5. CONTENT REQUIREMENTS:
   Your task: Provide comprehensive, high-quality guidance in THREE detailed sections. This guidance serves diverse seekers including students, professionals, individuals, families, and corporate employees - addressing both spiritual and practical life challenges. Make it relevant to modern life, especially for younger generations facing digital age challenges. Write in a way that appeals to a wide, diverse audience seeking both spiritual growth and practical solutions.

   A. ANALYSIS (500+ words):
      - Use clear section headers with ## for main topics and ### for subtopics
      - Explain how the PROVIDED verses address this specific problem using UNIVERSAL language (both spiritual and practical)
      - For questions about relationships, morality, or ethical conduct:
        * If verses about scriptural injunctions (BG 16.23, BG 16.24) are provided, you MUST include a section explaining the importance of following scriptural regulations
        * Quote BG 16.23: "He who discards scriptural injunctions and acts according to his own whims attains neither perfection, nor happiness, nor the supreme destination"
        * Quote BG 16.24: "One should therefore understand what is duty and what is not duty by the regulations of the scriptures. Knowing such rules and regulations, one should act so that he may gradually be elevated"
        * If BG 7.11 is provided, explain that relationships should be according to religious principles (dharma), not contrary to them. Quote the verse and its purport about sex life being for the propagation of children according to dharma, not otherwise
        * Emphasize that following scriptural injunctions leads to spiritual progress, happiness, and the supreme destination
        * Explain that relationships outside the bounds of scriptural injunctions and dharma should be discouraged, as they do not lead to spiritual progress
      - Frame teachings in terms that apply to different contexts: academic (students), professional (corporate employees, professionals), personal (individuals), and family life
      - Use inclusive spiritual language like "God Consciousness," "Divine principles," "spiritual wisdom" when relevant, but also provide practical, actionable insights
      - Quote specific translations and purports from the verses above using > blockquotes (text only, no quotes inside)
      - Reference specific verses by ID (e.g., **BG 2.12**, **BG 3.30**, **BG 16.23**, **BG 16.24**, **BG 7.11**) in bold and explain their relevance
      - Explain the core principles as described in the purports, using inclusive language
      - Connect the verse teachings to modern context across different life situations (academic, professional, personal, family)
      - Show how these universal principles apply to contemporary situations for students, professionals, individuals, families, and corporate employees
      - Base all explanations on the actual verse content provided
      - Use language that makes ancient wisdom accessible to modern, diverse audiences seeking both spiritual and practical guidance
      - Use bullet points (-) for lists and numbered lists (1., 2., 3.) for steps
      - Add line breaks between paragraphs for readability

   B. PRACTICAL GUIDANCE (500+ words):
      - Use clear section headers with ## for main topics
      - Provide specific, actionable steps based on the universal principles from the verses above
      - For questions about relationships or moral conduct:
        * If BG 16.23, BG 16.24, or BG 7.11 are provided, include guidance on following scriptural injunctions
        * Explain the importance of understanding duty through scriptural regulations
        * Provide compassionate but clear guidance on aligning relationships with dharma
        * Emphasize the spiritual benefits of following scriptural principles
        * If applicable, explain that relationships should be within the bounds of dharma and scriptural injunctions
      - Offer guidance that applies to different contexts: students (academic, career planning), professionals (work-life balance, leadership), individuals (personal growth), families (relationships, parenting), and corporate employees (teamwork, ethics, decision-making)
      - Frame guidance in terms that resonate with all seekers - both spiritual concepts (when relevant) and practical life principles
      - Use numbered lists (1., 2., 3.) for sequential steps
      - Use bullet points (-) for options or parallel items
      - Address the modern context mentioned in the query
      - Include immediate actions the person can take in their specific role (student, professional, family member, employee, etc.)
      - Reference specific verses and their teachings using **bold verse IDs** (especially BG 16.23, BG 16.24, BG 7.11 if provided)
      - Recommend practices based on what the verses actually say, making them applicable to various life situations
      - Make it practical and applicable to daily life for people of all backgrounds and roles
      - Consider digital age challenges if relevant
      - Write in a way that makes the principles accessible to everyone, whether they seek spiritual growth, practical solutions, or both
      - Add spacing between sections for readability

   C. PRACTICAL EXERCISES & PRACTICES (500+ words) - REQUIRED SECTION:
      - CRITICAL: You MUST include this section. Start with "## C. PRACTICAL EXERCISES & PRACTICES" or "## Practical Exercises & Practices"
      - Use clear section headers with ## for main topics
      - Suggest 5-7 specific exercises, practices, or activities that can be applied by different types of seekers (students, professionals, individuals, families, corporate employees)
      - IMPORTANT: Include practices based on Srila Prabhupada's teachings:
        * Early morning spiritual practice (rising early, morning meditation/prayer/chanting) - present this universally
        * The Hare Krishna maha mantra SHOULD be explicitly mentioned as it is important - you can present it as: "The Hare Krishna maha mantra (Hare Krishna, Hare Krishna, Krishna Krishna, Hare Hare / Hare Rama, Hare Rama, Rama Rama, Hare Hare) is recommended by Srila Prabhupada as a powerful practice for spiritual growth and God Consciousness"
        * Also provide generic/universal guidance based on Prabhupada's general teachings (e.g., "sacred sound meditation," "divine name meditation," "spiritual vibration practice") for those who prefer more universal language
        * Balance between being explicit about the Hare Krishna maha mantra (which is important) and providing generic alternatives
      - Include both spiritual practices (when relevant) and practical exercises for personal and professional growth
      - Frame exercises in universal terms that appeal to all - from spiritual growth to practical skill development
      - When including Prabhupada's practices:
        * Explicitly mention the Hare Krishna maha mantra with its full form
        * Also provide generic alternatives like "connecting with the Divine through sound," "early morning spiritual discipline," "sacred vibration meditation" for broader appeal
        * Explain that chanting sacred mantras (including the Hare Krishna maha mantra) is a universal practice for spiritual growth
      - Number each exercise (1., 2., 3., etc.) with clear titles like "### Exercise 1: [Title]"
      - Base them on the verses provided above AND on spiritual practices recommended by Srila Prabhupada (explicitly mention the Hare Krishna maha mantra, and also provide generic guidance)
      - Reference which verse(s) each exercise is based on using **bold verse IDs**
      - Make them practical and applicable to modern life for people of all backgrounds and roles
      - Include daily practices (like early morning routine, meditation/chanting - mention the Hare Krishna maha mantra explicitly), weekly reflections, and long-term cultivation suitable for different life contexts
      - Provide step-by-step instructions where helpful using sub-bullets
      - Consider modern lifestyle constraints and different schedules (student life, corporate work, family responsibilities)
      - Use inclusive language that makes practices accessible to everyone, whether they seek spiritual growth, practical solutions, or both
      - When describing chanting practices:
        * Explicitly mention the Hare Krishna maha mantra as recommended by Srila Prabhupada
        * Also provide generic alternatives like "sacred sound meditation," "divine name meditation," or "spiritual vibration practice" for those who prefer universal language
        * Explain that these practices help develop God Consciousness and spiritual growth
      - Add spacing between exercises for readability
      - DO NOT skip this section - it is mandatory

6. FORMATTING REQUIREMENTS:
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
        self.emit_progress("finalizing", "Finalizing answer format...", {})
        
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
        
        final_answer = f"""# Guidance for Modern Life

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

## 🧘 Practical Exercises & Practices

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

