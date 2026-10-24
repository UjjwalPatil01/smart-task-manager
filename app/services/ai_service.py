"""Isolated, resilient AI service using Google Gemini with offline fallback."""
import json
import logging
import re
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class AIService:
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Google Gemini API key is configured."""
        return bool(settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY.strip())

    @classmethod
    def _call_gemini_api(cls, prompt: str, timeout_seconds: float = 8.0) -> Optional[str]:
        """
        Direct REST call to Google Gemini generateContent endpoint.
        Eliminates external SDK installation issues and works with standard httpx.
        """
        if not cls.is_configured():
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GOOGLE_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                else:
                    logger.warning(f"Gemini API returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error connecting to Gemini API: {e}")

        return None

    @classmethod
    def suggest_priority(cls, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Suggest priority and category with transparent reasoning.
        Gracefully falls back to keyword heuristics if offline or unconfigured.
        """
        # Rule-based heuristic for fallback
        title_lower = title.lower()
        desc_lower = (description or "").lower()
        combined = f"{title_lower} {desc_lower}"

        fallback_priority = "low"
        fallback_category = "personal"
        fallback_reason = "Classified as low priority routine task."

        if any(w in combined for w in ["exam", "urgent", "deadline", "asap", "critical", "emergency", "interview", "today"]):
            fallback_priority = "high"
            fallback_reason = "Contains urgent or high-stakes deadline keywords (exam, urgent, deadline)."
        elif any(w in combined for w in ["meeting", "project", "review", "assignment", "report", "bug", "feature"]):
            fallback_priority = "medium"
            fallback_reason = "Identified as a scheduled or collaborative milestone."

        if any(w in combined for w in ["study", "exam", "assignment", "homework", "lecture", "course", "read"]):
            fallback_category = "study"
        elif any(w in combined for w in ["meeting", "client", "project", "deploy", "code", "work", "office", "presentation"]):
            fallback_category = "work"
        elif any(w in combined for w in ["doctor", "health", "gym", "workout", "medicine", "exercise"]):
            fallback_category = "health"
        elif any(w in combined for w in ["bill", "rent", "tax", "bank", "pay", "invoice", "salary"]):
            fallback_category = "finance"

        if not cls.is_configured():
            return {
                "priority": fallback_priority,
                "reasoning": f"[Offline Mode] {fallback_reason}",
                "suggested_category": fallback_category,
                "offline_fallback": True
            }

        prompt = f"""
        Analyze the following task and return a JSON object with:
        1. "priority": exactly one of "low", "medium", "high", "urgent"
        2. "reasoning": 1-2 sentence explanation of why this priority was assigned
        3. "category": suggested category (e.g. "work", "study", "personal", "health", "finance")

        Task Title: {title}
        Task Notes: {description or 'None'}

        Respond with JSON ONLY in this format:
        {{"priority": "...", "reasoning": "...", "category": "..."}}
        """

        raw_response = cls._call_gemini_api(prompt)
        if raw_response:
            try:
                # Clean json code block markdown if present
                clean = re.sub(r"```(json)?", "", raw_response).strip()
                data = json.loads(clean)
                priority = str(data.get("priority", "medium")).lower()
                if priority not in ["low", "medium", "high", "urgent"]:
                    priority = fallback_priority
                return {
                    "priority": priority,
                    "reasoning": data.get("reasoning", "AI analyzed task urgency and context."),
                    "suggested_category": data.get("category", fallback_category).lower(),
                    "offline_fallback": False
                }
            except Exception as e:
                logger.warning(f"Failed to parse Gemini JSON: {e}. Raw: {raw_response}")

        # Fallback if API failed
        return {
            "priority": fallback_priority,
            "reasoning": f"[Offline Fallback] {fallback_reason}",
            "suggested_category": fallback_category,
            "offline_fallback": True
        }

    @classmethod
    def decompose_task(cls, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Decompose a high-level task into 3-5 actionable subtasks.
        """
        default_subtasks = [
            f"Define requirements and clear goal for '{title}'",
            f"Gather required resources or research prerequisites",
            f"Execute core action steps",
            f"Review outcome and mark complete"
        ]

        if not cls.is_configured():
            return {
                "subtasks": default_subtasks,
                "offline_fallback": True
            }

        prompt = f"""
        Break down this task into 3 to 5 concise, actionable, chronological subtasks:
        Task Title: {title}
        Task Details: {description or 'None'}

        Return a JSON array of strings ONLY.
        Example: ["Subtask 1", "Subtask 2", "Subtask 3"]
        """

        raw_response = cls._call_gemini_api(prompt)
        if raw_response:
            try:
                clean = re.sub(r"```(json)?", "", raw_response).strip()
                subtasks = json.loads(clean)
                if isinstance(subtasks, list) and len(subtasks) > 0:
                    return {
                        "subtasks": [str(st).strip() for st in subtasks[:6]],
                        "offline_fallback": False
                    }
            except Exception as e:
                logger.warning(f"Failed to parse decomposition JSON: {e}")

        return {
            "subtasks": default_subtasks,
            "offline_fallback": True
        }

    @classmethod
    def generate_productivity_insights(cls, tasks_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized productivity insights and recommendations based on task metrics.
        """
        total = tasks_summary.get("total", 0)
        completed = tasks_summary.get("completed", 0)
        overdue = tasks_summary.get("overdue", 0)
        rate = tasks_summary.get("completion_rate", 0.0)

        # Base heuristic insight
        recommendations = []
        if overdue > 0:
            recommendations.append(f"You have {overdue} overdue task(s). Tackle the highest priority deadline first.")
        if rate > 75:
            recommendations.append("Strong completion velocity! Maintain your current batching habits.")
        elif rate < 40 and total > 3:
            recommendations.append("Consider breaking down larger tasks into smaller 15-minute subtasks to build momentum.")
        else:
            recommendations.append("Prioritize high-impact items during your peak focus hours.")

        score = min(100, max(20, int(rate * 0.7 + (30 if overdue == 0 else 10))))

        if not cls.is_configured():
            return {
                "summary": f"You have {total} total tasks with a {rate}% completion rate and {overdue} overdue tasks.",
                "actionable_recommendations": recommendations,
                "productivity_score": score,
                "offline_fallback": True
            }

        prompt = f"""
        You are a productivity coach analyzing task manager metrics:
        - Total tasks: {total}
        - Completed tasks: {completed}
        - Overdue tasks: {overdue}
        - Completion rate: {rate}%
        - High priority pending: {tasks_summary.get('high_priority', 0)}

        Return a JSON object with:
        1. "summary": A motivational 2-sentence assessment of user productivity.
        2. "actionable_recommendations": List of 2-3 specific, actionable recommendations.
        3. "productivity_score": An integer score from 0 to 100 representing current productivity health.

        JSON ONLY:
        """

        raw = cls._call_gemini_api(prompt)
        if raw:
            try:
                clean = re.sub(r"```(json)?", "", raw).strip()
                data = json.loads(clean)
                return {
                    "summary": data.get("summary", "Productivity review complete."),
                    "actionable_recommendations": data.get("actionable_recommendations", recommendations),
                    "productivity_score": int(data.get("productivity_score", score)),
                    "offline_fallback": False
                }
            except Exception as e:
                logger.warning(f"Error parsing insight JSON: {e}")

        return {
            "summary": f"You have completed {completed} out of {total} tasks ({rate}% completion rate).",
            "actionable_recommendations": recommendations,
            "productivity_score": score,
            "offline_fallback": True
        }
