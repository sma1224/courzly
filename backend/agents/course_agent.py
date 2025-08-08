from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, Any, List
import json
import os

class CourseOutlineAgent:
    """AI agent for generating course outlines"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.system_prompt = """You are an expert instructional designer and course creator. 
        Your task is to create comprehensive, well-structured course outlines that are pedagogically sound 
        and engaging for learners.
        
        Always respond with valid JSON in the following format:
        {
            "title": "Course Title",
            "description": "Course description",
            "learning_objectives": ["objective1", "objective2"],
            "target_audience": "Description of target audience",
            "duration": "Estimated duration",
            "modules": [
                {
                    "title": "Module Title",
                    "description": "Module description",
                    "learning_objectives": ["objective1"],
                    "lessons": [
                        {
                            "title": "Lesson Title",
                            "description": "Lesson description",
                            "duration": "Duration",
                            "content_type": "video|text|interactive|quiz"
                        }
                    ]
                }
            ]
        }"""
    
    async def generate_outline(self, title: str, description: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate course outline based on title and description"""
        
        human_prompt = f"""
        Create a comprehensive course outline for:
        
        Title: {title}
        Description: {description}
        
        Additional requirements:
        - Target audience: {config.get('target_audience', 'General learners')}
        - Course level: {config.get('level', 'Intermediate')}
        - Preferred duration: {config.get('duration', '4-6 hours')}
        - Number of modules: {config.get('num_modules', '4-6')}
        - Include practical exercises: {config.get('include_exercises', True)}
        
        Ensure the outline is:
        1. Logically structured and progressive
        2. Includes clear learning objectives
        3. Balances theory and practice
        4. Appropriate for the target audience
        5. Engaging and interactive
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            outline = json.loads(response.content)
            
            # Validate and enhance outline
            outline = self._validate_outline(outline)
            
            return outline
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate outline: {e}")
    
    def _validate_outline(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the generated outline"""
        required_fields = ["title", "description", "modules"]
        
        for field in required_fields:
            if field not in outline:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure modules have required structure
        for i, module in enumerate(outline.get("modules", [])):
            if "title" not in module:
                module["title"] = f"Module {i+1}"
            if "lessons" not in module:
                module["lessons"] = []
        
        # Add metadata
        outline["metadata"] = {
            "generated_by": "CourseOutlineAgent",
            "version": "1.0",
            "agent_model": "gpt-4"
        }
        
        return outline

class ContentGenerationAgent:
    """AI agent for generating detailed course content"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.6,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.system_prompt = """You are an expert content creator and subject matter expert. 
        Your task is to create detailed, engaging, and educational content for course modules.
        
        Always respond with valid JSON in the following format:
        {
            "title": "Module Title",
            "description": "Module description",
            "content": {
                "introduction": "Module introduction text",
                "lessons": [
                    {
                        "title": "Lesson Title",
                        "content": "Detailed lesson content in markdown format",
                        "activities": ["activity1", "activity2"],
                        "quiz_questions": [
                            {
                                "question": "Question text",
                                "options": ["A", "B", "C", "D"],
                                "correct_answer": "A",
                                "explanation": "Why this is correct"
                            }
                        ]
                    }
                ],
                "summary": "Module summary",
                "resources": ["resource1", "resource2"]
            }
        }"""
    
    async def generate_module_content(self, module_outline: Dict[str, Any], course_context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed content for a module"""
        
        human_prompt = f"""
        Generate detailed content for this module:
        
        Module: {json.dumps(module_outline, indent=2)}
        
        Course Context: {course_context.get('title', '')} - {course_context.get('description', '')}
        
        Content Requirements:
        - Writing style: {config.get('writing_style', 'Professional and engaging')}
        - Include examples: {config.get('include_examples', True)}
        - Include exercises: {config.get('include_exercises', True)}
        - Include quizzes: {config.get('include_quizzes', True)}
        - Content depth: {config.get('content_depth', 'Detailed')}
        
        Create comprehensive content that:
        1. Builds on previous modules logically
        2. Includes practical examples and case studies
        3. Has interactive elements and exercises
        4. Includes assessment questions
        5. Provides additional resources for deeper learning
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            content = json.loads(response.content)
            
            # Validate and enhance content
            content = self._validate_content(content, module_outline)
            
            return content
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate content: {e}")
    
    def _validate_content(self, content: Dict[str, Any], module_outline: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the generated content"""
        
        # Ensure basic structure
        if "content" not in content:
            content["content"] = {}
        
        if "lessons" not in content["content"]:
            content["content"]["lessons"] = []
        
        # Add metadata
        content["metadata"] = {
            "generated_by": "ContentGenerationAgent",
            "version": "1.0",
            "agent_model": "gpt-4",
            "module_outline": module_outline
        }
        
        return content

class ReviewAgent:
    """AI agent for reviewing and providing feedback on content"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.system_prompt = """You are an expert educational content reviewer and quality assurance specialist.
        Your task is to review course content and provide constructive feedback for improvement.
        
        Always respond with valid JSON in the following format:
        {
            "overall_score": 8.5,
            "feedback": {
                "strengths": ["strength1", "strength2"],
                "areas_for_improvement": ["improvement1", "improvement2"],
                "specific_suggestions": [
                    {
                        "section": "Section name",
                        "issue": "Description of issue",
                        "suggestion": "Specific improvement suggestion"
                    }
                ]
            },
            "quality_metrics": {
                "clarity": 8,
                "engagement": 7,
                "accuracy": 9,
                "completeness": 8,
                "pedagogical_soundness": 8
            },
            "recommendation": "approve|revise|reject"
        }"""
    
    async def review_content(self, content: Dict[str, Any], review_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Review content and provide feedback"""
        
        human_prompt = f"""
        Review this course content:
        
        {json.dumps(content, indent=2)}
        
        Review Criteria:
        - Target audience: {review_criteria.get('target_audience', 'General learners')}
        - Quality standards: {review_criteria.get('quality_standards', 'High')}
        - Focus areas: {review_criteria.get('focus_areas', ['clarity', 'engagement', 'accuracy'])}
        
        Provide detailed feedback focusing on:
        1. Content accuracy and completeness
        2. Clarity and readability
        3. Engagement and interactivity
        4. Pedagogical effectiveness
        5. Alignment with learning objectives
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            review = json.loads(response.content)
            
            return review
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to review content: {e}")