"""Keyword extractor — identifies important keywords and skills from job descriptions."""

import re
from collections import Counter


class KeywordExtractor:
    """Extracts important keywords from job descriptions."""

    # Common stop words to exclude
    STOP_WORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "are", "was", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can", "need",
        "must", "about", "between", "through", "during", "before", "after",
        "above", "below", "up", "down", "out", "off", "over", "under", "again",
        "further", "then", "once", "here", "there", "when", "where", "why",
        "how", "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "just", "because", "also", "if", "into", "its",
        "our", "their", "your", "this", "that", "these", "those", "we", "they",
        "who", "whom", "which", "what", "experience", "knowledge", "ability",
        "skills", "including", "including", "etc", "etc.",
    }

    # Common technical keyword patterns (programming languages, frameworks, tools)
    TECHNICAL_PATTERNS = [
        r'\b(?:Python|JavaScript|TypeScript|Java|Go|Rust|C\+\+|C#|Ruby|PHP|Swift|Kotlin|Scala|Perl|R|Julia|Dart|Elixir)\b',
        r'\b(?:React|Angular|Vue|Svelte|Next\.?js|Nuxt|Express|Django|Flask|FastAPI|Spring|Rails|Laravel|ASP\.?NET|Node\.?js|Deno|Bun)\b',
        r'\b(?:PostgreSQL|MySQL|SQLite|MongoDB|Redis|Elasticsearch|Cassandra|DynamoDB|Couchbase|MariaDB|Oracle|SQL\s?Server|Firebase|Supabase)\b',
        r'\b(?:Docker|Kubernetes|Terraform|Ansible|Jenkins|GitHub\s?Actions|CircleCI|GitLab\s?CI|AWS|Azure|GCP|Cloud|DevOps|CI/CD|Helm|Prometheus|Grafana)\b',
        r'\b(?:REST|GraphQL|gRPC|WebSocket|OAuth|JWT|API|Microservices|Event\s?Driven|CQRS|Event\s?Sourcing)\b',
        r'\b(?:Machine\s?Learning|Deep\s?Learning|NLP|Computer\s?Vision|TensorFlow|PyTorch|Scikit|LLM|RAG|LangChain|Vector\s?Database)\b',
        r'\b(?:Agile|Scrum|Kanban|JIRA|Confluence|Git|Linux|Unix|Bash|Shell|Unit\s?Test|Integration\s?Test|TDD|BDD)\b',
    ]

    def __init__(self) -> None:
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.TECHNICAL_PATTERNS
        ]

    def extract_keywords(self, job_description: str) -> list[str]:
        """Extract important keywords from a job description.

        Returns a list of unique keywords sorted by frequency.
        """
        words = self._tokenize(job_description)
        keyword_counts: Counter = Counter()

        # 1. Match technical patterns
        for pattern in self._compiled_patterns:
            for match in pattern.finditer(job_description):
                keyword = match.group(0).strip()
                keyword_counts[keyword] += 1

        # 2. Find capitalized multi-word phrases (potential proper nouns)
        phrases = self._extract_phrases(words)
        for phrase in phrases:
            keyword_counts[phrase] += 1

        # 3. Single important words (filtered by length and stop words)
        for word in words:
            if len(word) > 3 and word.lower() not in self.STOP_WORDS:
                keyword_counts[word] += 1

        # Sort by frequency, return unique keywords
        sorted_keywords = sorted(
            keyword_counts.keys(),
            key=lambda k: (-keyword_counts[k], k),
        )

        return sorted_keywords

    def extract_required_skills(self, job_description: str) -> list[str]:
        """Extract specifically required skills from a job description.

        Focuses on technical skills explicitly mentioned as requirements.
        """
        keywords = self.extract_keywords(job_description)

        # Filter to likely technical skills (title case, short phrases)
        technical_skills = [
            kw for kw in keywords
            if len(kw) > 1 and (kw[0].isupper() or any(
                p.search(kw) for p in self._compiled_patterns
            ))
        ]

        return technical_skills

    def extract_experience_years(self, job_description: str) -> int | None:
        """Extract the required years of experience from a job description."""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of)?\s*(?:experience|work)',
            r'(?:experience|work)\s*(?:of)?\s*(\d+)\+?\s*years?',
        ]
        for pattern in patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into words."""
        return re.findall(r'\b[a-zA-Z][a-zA-Z0-9#+.]*\b', text)

    def _extract_phrases(self, words: list[str]) -> list[str]:
        """Extract capitalized multi-word phrases from token list."""
        phrases = []
        current_phrase = []

        for word in words:
            if word[0].isupper() and len(word) > 1:
                current_phrase.append(word)
            else:
                if 2 <= len(current_phrase) <= 4:
                    phrases.append(" ".join(current_phrase))
                current_phrase = []

        if 2 <= len(current_phrase) <= 4:
            phrases.append(" ".join(current_phrase))

        return phrases
