import json
import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = "gpt-3.5-turbo"


def _client(api_key: Optional[str] = None) -> OpenAI:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=key)


def call_llm(messages, temperature=0.7, max_tokens=800, api_key: Optional[str] = None) -> str:
    client = _client(api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content


@dataclass
class StoryFeedback:
    approved: bool
    critique: str
    score: int


@dataclass
class StoryResult:
    request: str
    outline: str
    draft: str
    final_story: str
    feedback: StoryFeedback
    image_prompt: str
    image_url: Optional[str]
    iterations: int
    genre: Optional[str] = None
    length: Optional[str] = None


class StoryGenerator:
    def __init__(self, writer_temperature: float = 0.85, api_key: Optional[str] = None):
        self.writer_temperature = writer_temperature
        self.api_key = api_key

    def create_outline(self, request: str, genre: Optional[str] = None, length: Optional[str] = None) -> str:
        system = (
            "You are a story architect creating short outlines for children's "
            "bedtime stories (ages 5-10). Keep outlines to 3-5 bullet points."
        )
        length_hint = ""
        if length == "short":
            length_hint = "Target 2-3 short paragraphs."
        elif length == "medium":
            length_hint = "Target 4-6 short paragraphs."
        elif length == "long":
            length_hint = "Target 7-10 short paragraphs."
        genre_hint = f"Genre/arc: {genre}." if genre else ""
        user = (
            f"Create a concise outline for this request. "
            f"Focus on kindness, curiosity, and friendly adventure.\n"
            f"Request: {request}\n{genre_hint}\n{length_hint}"
        )
        return call_llm(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.6,
            max_tokens=200,
            api_key=self.api_key,
        )

    def write_story(self, request: str, outline: Optional[str], genre: Optional[str] = None, length: Optional[str] = None) -> str:
        system = (
            "You are a whimsical children's book author. Write for ages 5-10 with simple "
            "vocabulary and short sentences. Avoid scary elements. Highlight friendship, "
            "curiosity, and kindness."
        )
        length_hint = "Length: 4-8 short paragraphs."
        if length == "short":
            length_hint = "Length: 2-3 short paragraphs."
        elif length == "medium":
            length_hint = "Length: 4-6 short paragraphs."
        elif length == "long":
            length_hint = "Length: 7-10 short paragraphs."
        genre_hint = f"Genre/arc: {genre}." if genre else ""
        user = (
            f"User request: {request}\n"
            f"Story outline (use but keep it short and clear):\n{outline or 'None provided'}\n"
            f"Write a complete bedtime story.\n{genre_hint}\n{length_hint}"
        )
        return call_llm(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=self.writer_temperature,
            max_tokens=900,
            api_key=self.api_key,
        )

    def refine_story(self, draft: str, critique: str) -> str:
        system = (
            "You are revising a children's bedtime story for ages 5-10. "
            "Apply the given critique while keeping the tone warm and safe."
        )
        user = (
            f"Draft:\n{draft}\n\nCritique:\n{critique}\n"
            "Rewrite the story so it fully addresses the critique."
        )
        return call_llm(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=self.writer_temperature,
            max_tokens=900,
            api_key=self.api_key,
        )

    def illustration_prompt(self, story: str) -> str:
        system = "You create concise illustration prompts for children's stories."
        user = (
            "Provide one vivid illustration prompt for this story, 25 words max, "
            "no characters' faces described in detail.\n"
            f"Story:\n{story}"
        )
        return call_llm(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.6,
            max_tokens=80,
            api_key=self.api_key,
        )


class StoryJudge:
    def __init__(self, judge_temperature: float = 0.15, api_key: Optional[str] = None):
        self.judge_temperature = judge_temperature
        self.api_key = api_key

    def evaluate(self, story: str) -> StoryFeedback:
        system = (
            "You are a strict editor for a children's publisher. "
            "Check the story for: vocabulary fit for age 5-10, plot consistency, safety, and fun. "
            "Return JSON with keys approved (bool), critique (string), score (1-10). "
            "Return JSON only."
        )
        user = f"Story to review:\n{story}"
        raw = call_llm(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=self.judge_temperature,
            max_tokens=300,
            api_key=self.api_key,
        )
        try:
            data = json.loads(raw)
            approved = bool(data.get("approved", False))
            critique = str(data.get("critique", ""))
            score = int(data.get("score", 0))
        except Exception:
            approved = False
            critique = f"Invalid JSON from judge. Content: {raw}"
            score = 0
        return StoryFeedback(approved=approved, critique=critique, score=score)


class ImageGenerator:
    def __init__(self, size: str = "1024x1024", api_key: Optional[str] = None):
        self.size = size
        self.api_key = api_key

    def generate_image(self, prompt: str) -> Optional[str]:
        client = _client(self.api_key)
        resp = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=self.size,
            n=1,
        )
        if resp.data and resp.data[0].url:
            return resp.data[0].url
        return None


class StoryOrchestrator:
    def __init__(self, writer_temperature: float = 0.85, judge_temperature: float = 0.15, api_key: Optional[str] = None):
        self.generator = StoryGenerator(writer_temperature=writer_temperature, api_key=api_key)
        self.judge = StoryJudge(judge_temperature=judge_temperature, api_key=api_key)
        self.image_generator = ImageGenerator(api_key=api_key)

    def run(self, request: str, retries: int = 2, genre: Optional[str] = None, length: Optional[str] = None) -> StoryResult:
        outline = self.generator.create_outline(request, genre=genre, length=length)
        draft = self.generator.write_story(request, outline, genre=genre, length=length)
        feedback = self.judge.evaluate(draft)
        iterations = 0
        while not feedback.approved and iterations < retries:
            draft = self.generator.refine_story(draft, feedback.critique)
            iterations += 1
            feedback = self.judge.evaluate(draft)
        final_story = draft
        image_prompt = self.generator.illustration_prompt(final_story)
        image_url = self.image_generator.generate_image(image_prompt)
        return StoryResult(
            request=request,
            outline=outline,
            draft=draft,
            final_story=final_story,
            feedback=feedback,
            image_prompt=image_prompt,
            image_url=image_url,
            iterations=iterations,
            genre=genre,
            length=length,
        )

