import json
import os
import logging
from typing import List, Dict, Any
from openai import OpenAI
from backend.models import Question

logger = logging.getLogger(__name__)


class TriviaService:
    """Service for generating trivia questions using OpenAI."""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=api_key)
    
    def generate_quiz(self, topic: str) -> List[Question]:
        """
        Generate exactly 10 trivia questions for the given topic.
        
        Args:
            topic: TV show or movie name
            
        Returns:
            List of 10 Question objects
            
        Raises:
            ValueError: If OpenAI response is invalid or cannot be parsed
        """
        prompt = self._build_prompt(topic)
        
        # Prepare request parameters
        # Using gpt-4o which supports response_format with json_object
        # Alternative models that support json_object: gpt-4-turbo-preview, gpt-4-0125-preview
        request_params = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a trivia master. Generate exactly 10 multiple-choice trivia questions in valid JSON format. Each question must have exactly 4 options and exactly 1 correct answer. The incorrect answers must be plausible and not obviously wrong."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        # Log the exact request being sent
        logger.info("=" * 80)
        logger.info("OPENAI API REQUEST")
        logger.info("=" * 80)
        logger.info(f"Topic: {topic}")
        logger.info(f"Model: {request_params['model']}")
        logger.info(f"Temperature: {request_params['temperature']}")
        logger.info(f"Response Format: {request_params['response_format']}")
        logger.info("Messages:")
        for i, msg in enumerate(request_params['messages']):
            logger.info(f"  [{i}] Role: {msg['role']}")
            logger.info(f"      Content: {msg['content']}")
        logger.info("=" * 80)
        
        try:
            try:
                response = self.client.chat.completions.create(**request_params)
            except Exception as e:
                # If response_format is not supported, try without it
                error_str = str(e)
                if "response_format" in error_str.lower() or "json_object" in error_str.lower():
                    logger.warning(f"Model does not support response_format, retrying without it: {e}")
                    request_params_no_format = request_params.copy()
                    request_params_no_format.pop("response_format", None)
                    # Enhance prompt to emphasize JSON output
                    enhanced_prompt = prompt + "\n\nIMPORTANT: You MUST return ONLY valid JSON. Do not include any text before or after the JSON. The JSON must be parseable."
                    request_params_no_format["messages"][1]["content"] = enhanced_prompt
                    logger.info("Retrying with enhanced prompt (no response_format)")
                    response = self.client.chat.completions.create(**request_params_no_format)
                else:
                    raise
            
            # Log the exact raw response
            logger.info("=" * 80)
            logger.info("OPENAI API RESPONSE (RAW)")
            logger.info("=" * 80)
            logger.info(f"Response ID: {response.id}")
            logger.info(f"Model: {response.model}")
            logger.info(f"Created: {response.created}")
            logger.info(f"Usage - Prompt tokens: {response.usage.prompt_tokens}")
            logger.info(f"Usage - Completion tokens: {response.usage.completion_tokens}")
            logger.info(f"Usage - Total tokens: {response.usage.total_tokens}")
            logger.info(f"Choices count: {len(response.choices)}")
            
            content = response.choices[0].message.content
            if not content:
                logger.error("Empty content in OpenAI response")
                raise ValueError("Empty response from OpenAI")
            
            logger.info("Raw Content (full):")
            logger.info(content)
            logger.info("=" * 80)
            
            # Extract JSON from content (handle markdown code blocks or extra text)
            json_content = self._extract_json_from_content(content)
            
            # Parse and validate JSON response
            quiz_data = json.loads(json_content)
            
            # Log the parsed JSON response
            logger.info("=" * 80)
            logger.info("OPENAI API RESPONSE (PARSED JSON)")
            logger.info("=" * 80)
            logger.info(f"Parsed JSON structure: {json.dumps(quiz_data, indent=2)}")
            logger.info("=" * 80)
            
            questions = self._parse_and_validate_response(quiz_data, topic)
            
            logger.info(f"Successfully generated and validated {len(questions)} questions for topic: {topic}")
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            if 'content' in locals():
                logger.error(f"Failed to parse content (full): {content}")
            else:
                logger.error("Content not available (error occurred before response parsing)")
            raise ValueError(f"Invalid JSON response from OpenAI: {e}")
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}", exc_info=True)
            raise ValueError(f"Error generating quiz: {str(e)}")
    
    def generate_performance_phrase(self, topic: str, score: int, total: int) -> str:
        """
        Generate a performance phrase based on the user's score, connected to the show/movie.
        
        Args:
            topic: TV show or movie name
            score: User's score
            total: Total number of questions
            
        Returns:
            Performance phrase string
        """
        # Determine performance category
        if score == total:
            category = "Amazing"
        elif score >= 6:
            category = "Decent"
        elif score >= 3:
            category = "Poor"
        else:
            category = "Abysmal"
        
        prompt = f"""Generate a short, witty performance phrase (1-2 sentences max) for someone who scored {score}/{total} on a trivia quiz about "{topic}".

The performance level is: {category}

Requirements:
- The phrase should be connected to or reference the show/movie "{topic}"
- It should be appropriate for the score level ({category})
- Keep it fun and engaging
- Maximum 2 sentences
- Do not include the score in the phrase itself

Examples for different shows:
- For "The Office": "Looks like someone needs to watch more episodes of Dunder Mifflin!"
- For "Breaking Bad": "You might need to cook up some more knowledge about this show!"
- For "Inception": "Your understanding of this movie might need another layer!"

Generate the phrase now:"""
        
        try:
            request_params = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a witty trivia commentator. Generate short, engaging phrases that reference the show or movie."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.8,
                "max_tokens": 100
            }
            
            logger.info("=" * 80)
            logger.info("OPENAI API REQUEST - Performance Phrase")
            logger.info("=" * 80)
            logger.info(f"Topic: {topic}")
            logger.info(f"Score: {score}/{total} ({category})")
            logger.info(f"Model: {request_params['model']}")
            logger.info("Prompt:")
            logger.info(prompt)
            logger.info("=" * 80)
            
            try:
                response = self.client.chat.completions.create(**request_params)
            except Exception as e:
                # Fallback if model doesn't support parameters
                error_str = str(e)
                if "response_format" in error_str.lower():
                    request_params.pop("response_format", None)
                    response = self.client.chat.completions.create(**request_params)
                else:
                    raise
            
            content = response.choices[0].message.content
            if not content:
                # Fallback phrase
                return self._get_fallback_phrase(category, topic)
            
            phrase = content.strip()
            
            logger.info("=" * 80)
            logger.info("OPENAI API RESPONSE - Performance Phrase")
            logger.info("=" * 80)
            logger.info(f"Generated phrase: {phrase}")
            logger.info("=" * 80)
            
            return phrase
            
        except Exception as e:
            logger.error(f"Error generating performance phrase: {e}")
            # Return fallback phrase
            return self._get_fallback_phrase(category, topic)
    
    def _get_fallback_phrase(self, category: str, topic: str) -> str:
        """Generate a fallback phrase if OpenAI fails."""
        fallbacks = {
            "Amazing": f"Outstanding knowledge of {topic}!",
            "Decent": f"Not bad! You know your {topic}.",
            "Poor": f"Time to rewatch {topic}!",
            "Abysmal": f"You might want to brush up on {topic}."
        }
        return fallbacks.get(category, f"Thanks for playing the {topic} quiz!")
    
    def _extract_json_from_content(self, content: str) -> str:
        """
        Extract JSON from content, handling markdown code blocks or extra text.
        
        Args:
            content: Raw content from OpenAI
            
        Returns:
            JSON string
        """
        # Remove markdown code blocks if present
        if "```json" in content:
            # Extract content between ```json and ```
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end != -1:
                content = content[start:end].strip()
        elif "```" in content:
            # Extract content between ``` and ```
            start = content.find("```") + 3
            end = content.find("```", start)
            if end != -1:
                content = content[start:end].strip()
        
        # Try to find JSON object boundaries
        start_idx = content.find("{")
        end_idx = content.rfind("}")
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx + 1]
        
        return content.strip()
    
    def _build_prompt(self, topic: str) -> str:
        """Build the prompt for OpenAI based on the topic."""
        return f"""Generate exactly 10 trivia questions about "{topic}".

Requirements:
- Each question must demonstrate deep knowledge of: plot, characters, actors, iconic moments
- For TV shows, include season-level understanding questions
- Each question must be multiple-choice with exactly 4 options
- Exactly 1 correct answer per question
- 3 plausible incorrect answers (not obviously wrong)
- Questions should vary in difficulty

Return the response as a JSON object with this exact structure:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A"
    }}
  ]
}}

Generate exactly 10 questions. Make them challenging and interesting."""
    
    def _parse_and_validate_response(self, data: Dict[str, Any], topic: str) -> List[Question]:
        """
        Parse and validate the OpenAI response.
        
        Args:
            data: Parsed JSON response from OpenAI
            topic: Original topic for error messages
            
        Returns:
            List of validated Question objects
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValueError("Response is not a JSON object")
        
        if "questions" not in data:
            raise ValueError("Response missing 'questions' key")
        
        questions_data = data["questions"]
        
        if not isinstance(questions_data, list):
            raise ValueError("'questions' must be an array")
        
        if len(questions_data) != 10:
            raise ValueError(f"Expected exactly 10 questions, got {len(questions_data)}")
        
        questions = []
        for i, q_data in enumerate(questions_data):
            try:
                # Validate structure
                if not isinstance(q_data, dict):
                    raise ValueError(f"Question {i+1} is not an object")
                
                if "question" not in q_data:
                    raise ValueError(f"Question {i+1} missing 'question' field")
                
                if "options" not in q_data:
                    raise ValueError(f"Question {i+1} missing 'options' field")
                
                if "correct_answer" not in q_data:
                    raise ValueError(f"Question {i+1} missing 'correct_answer' field")
                
                options = q_data["options"]
                if not isinstance(options, list):
                    raise ValueError(f"Question {i+1} 'options' must be an array")
                
                if len(options) != 4:
                    raise ValueError(f"Question {i+1} must have exactly 4 options, got {len(options)}")
                
                correct_answer = q_data["correct_answer"]
                if correct_answer not in options:
                    raise ValueError(f"Question {i+1} 'correct_answer' must be one of the options")
                
                # Create Question object (Pydantic will validate types)
                question = Question(
                    question=str(q_data["question"]),
                    options=[str(opt) for opt in options],
                    correct_answer=str(correct_answer)
                )
                questions.append(question)
                
            except Exception as e:
                raise ValueError(f"Error validating question {i+1}: {str(e)}")
        
        return questions

