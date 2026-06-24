"""Naukri.com job scraper using Playwright (headless browser).

Naukri uses client-side JavaScript rendering (SPA), so traditional HTTP-based
scraping cannot extract job data. This scraper uses Playwright to:
1. Launch a headless Chromium browser
2. Navigate to Naukri's search results page
3. Wait for JavaScript-rendered job cards to appear
4. Extract job data from the live DOM
5. Normalize into the standard Job schema
"""

import hashlib
import logging
import re
from typing import Optional

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from .base import JobScraper, ScrapeError

logger = logging.getLogger(__name__)


class NaukriPlaywrightScraper(JobScraper):
    """Scrapes job listings from Naukri.com using a headless Chromium browser.

    Uses Playwright to execute JavaScript and extract data from the
    client-side rendered DOM.
    """

    BASE_URL = "https://www.naukri.com"
    # Use a recent real Chrome user agent to avoid bot detection
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    @property
    def source_name(self) -> str:
        return "naukri"

    async def fetch(self) -> list[dict]:
        """Fetch jobs by rendering Naukri search results in a headless browser.

        Launches Chromium, navigates to the search page, waits for the
        JavaScript-rendered job cards to appear, then extracts structured
        data from the DOM.
        """
        query = self.config.get("query", "software engineer")
        location = self.config.get("location", "india")
        max_jobs = self.config.get("limit", 25)

        # Sanitize query for URL
        query_slug = re.sub(r"[^a-z0-9-]", "", query.lower().replace(" ", "-"))
        location_slug = re.sub(r"[^a-z0-9-]", "", location.lower().replace(" ", "-"))
        if not query_slug:
            query_slug = "software-engineer"
        if not location_slug:
            location_slug = "india"

        search_url = f"{self.BASE_URL}/{query_slug}-jobs-in-{location_slug}"

        headless = self.config.get("headless", True)
        timeout_ms = self.config.get("playwright_timeout_ms", 60000)
        wait_selector = self.config.get(
            "wait_selector",
            "div[class*='jobTuple'], section[class*='job'], div[class*='list'], "
            ".job-search-result, [data-job-id], article.srpJobTuple, "
            "div.srp-jobtuple-wrapper",
        )

        # Proxy configuration (for residential/rotating proxies)
        proxy_config = self.config.get("proxy", None)
        if proxy_config is None:
            # Also check individual proxy settings from config
            proxy_server = self.config.get("proxy_server", None)
            if proxy_server:
                proxy_config = {"server": proxy_server}
                if self.config.get("proxy_username"):
                    proxy_config["username"] = self.config["proxy_username"]
                if self.config.get("proxy_password"):
                    proxy_config["password"] = self.config["proxy_password"]

        if proxy_config and proxy_config.get("server"):
            # Sanitize server URL to avoid leaking credentials in logs
            server_url = proxy_config["server"]
            if "@" in server_url:
                server_display = server_url.split("@")[-1]
            else:
                server_display = server_url
            logger.info("Using proxy: %s", server_display)
        else:
            logger.info("No proxy configured — using direct connection")

        logger.info(
            "Launching Playwright browser to scrape Naukri at %s",
            search_url,
        )

        async with async_playwright() as pw:
            try:
                browser = await pw.chromium.launch(
                    headless=headless,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-web-security",
                        "--disable-features=IsolateOrigins,site-per-process",
                        "--disable-blink-features=AutomationControlled",
                    ],
                )

                # Build context options with optional proxy
                context_options = {
                    "user_agent": self.USER_AGENT,
                    "viewport": {"width": 1920, "height": 1080},
                    "locale": "en-IN",
                    "timezone_id": "Asia/Kolkata",
                    "extra_http_headers": {
                        "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                        "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                    },
                }

                # Add proxy if configured (with validation)
                if proxy_config and proxy_config.get("server"):
                    context_options["proxy"] = {
                        "server": proxy_config["server"],
                    }
                    if proxy_config.get("username"):
                        context_options["proxy"]["username"] = proxy_config["username"]
                    if proxy_config.get("password"):
                        context_options["proxy"]["password"] = proxy_config["password"]

                context = await browser.new_context(**context_options)

                # Override navigator.webdriver to bypass bot detection
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    // Override permissions
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-IN', 'en-US', 'en']
                    });
                """)

                page = await context.new_page()

                # Navigate to search page with a longer timeout
                logger.info("Navigating to %s", search_url)
                await page.goto(search_url, wait_until="domcontentloaded", timeout=timeout_ms)

                # Wait for job cards to appear
                try:
                    await page.wait_for_selector(wait_selector, timeout=15000)
                    logger.info("Job cards loaded successfully")
                except PlaywrightTimeout:
                    logger.warning(
                        "Timed out waiting for job cards. "
                        "Naukri may have changed their HTML structure or "
                        "the page may require additional interaction."
                    )
                    # Try scrolling to trigger lazy loading
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(3000)
                    await page.evaluate("window.scrollTo(0, 0)")
                    await page.wait_for_timeout(1000)

                # Extract job data from live DOM using JavaScript evaluation
                raw_jobs = await self._extract_from_page(page)

                if not raw_jobs:
                    page_title = await page.title()
                    page_content = await page.content()
                    logger.warning(
                        "No job data extracted from Naukri. Page title: '%s'. Content length: %d",
                        page_title,
                        len(page_content),
                    )
                    # Detect common blocking scenarios
                    page_text_lower = (await page.text_content("body") or "").lower()
                    if "access denied" in page_text_lower or "accessdenied" in page_text_lower:
                        logger.error(
                            "Naukri returned Access Denied - bot detection triggered. "
                            "The headless browser was detected as a bot. "
                            "Try: using a different IP, adding more realistic browser fingerprints, "
                            "or reducing request frequency."
                        )
                    # Take screenshot for debugging
                    try:
                        await page.screenshot(path="/tmp/naukri_debug.png")
                        logger.info("Saved debug screenshot to /tmp/naukri_debug.png")
                    except Exception:
                        pass

            except PlaywrightTimeout as e:
                raise ScrapeError(
                    f"Playwright timed out: {e}",
                    self.source_name,
                )
            except Exception as e:
                raise ScrapeError(
                    f"Playwright error: {e}",
                    self.source_name,
                )
            finally:
                try:
                    await browser.close()
                except Exception:
                    pass

        return raw_jobs[:max_jobs] if max_jobs else raw_jobs

    async def _extract_from_page(self, page) -> list[dict]:
        """Extract job data from the live rendered DOM using JavaScript.

        This runs as JavaScript inside the browser context, giving access
        to the fully rendered DOM after client-side rendering.
        """
        extract_script = """
        () => {
            const jobs = [];

            // Common Naukri job card selectors (tried in order)
            const cardSelectors = [
                'article.jobTuple',
                'article[class*="jobTuple"]',
                'div[class*="jobTuple"]',
                'section[class*="job"]',
                'div.srpJobTuple',
                'div[class*="srp-jobtuple"]',
                'article[data-job-id]',
                'div[data-job-id]',
                'div.job-search-card',
                'li[class*="job"]',
                'div[class*="list"]:has(a[href*="job-detail"])',
                'div[class*="card"]:has(a[href*="job-detail"])',
                'article:has(span[class*="salary"])',
                'div:has(> a[href*="job-detail"])',
            ];

            let cards = [];
            for (const selector of cardSelectors) {
                const found = document.querySelectorAll(selector);
                if (found.length > 0) {
                    cards = found;
                    break;
                }
            }

            // Fallback: look for any element with job-related href links
            if (cards.length === 0) {
                const links = document.querySelectorAll('a[href*="job-detail"], a[href*="-jobs-"]');
                const processed = new Set();
                for (const link of links) {
                    const card = link.closest('article, section, div, li');
                    if (card && !processed.has(card)) {
                        processed.add(card);
                        cards = Array.from(processed);
                    }
                }
            }

            for (const card of cards) {
                const job = {};

                // Title
                const titleEl = (
                    card.querySelector('.title') ||
                    card.querySelector('a[class*="title"]') ||
                    card.querySelector('h2 a') ||
                    card.querySelector('h2') ||
                    card.querySelector('a[href*="job-detail"]')
                );
                if (titleEl) {
                    job.title = titleEl.textContent.trim();
                    const href = titleEl.getAttribute('href');
                    if (href) {
                        job.url = href.startsWith('http') ? href : 'https://www.naukri.com' + href;
                    }
                }

                // Company
                const companyEl = (
                    card.querySelector('a[class*="company"]') ||
                    card.querySelector('a[class*="subTitle"]') ||
                    card.querySelector('span[class*="company"]') ||
                    card.querySelector('[class*="company"]')
                );
                if (companyEl) {
                    job.company_name = companyEl.textContent.trim();
                }

                // Location
                const locEl = (
                    card.querySelector('[class*="location"]') ||
                    card.querySelector('[class*="loc"]') ||
                    card.querySelector('[class*="place"]')
                );
                if (locEl) {
                    job.location = locEl.textContent.trim();
                }

                // Salary
                const salaryEl = (
                    card.querySelector('[class*="salary"]') ||
                    card.querySelector('[class*="salary"]')
                );
                if (salaryEl) {
                    job.salary = salaryEl.textContent.trim();
                }

                // Experience
                const expEl = (
                    card.querySelector('[class*="experience"]') ||
                    card.querySelector('[class*="exp"]')
                );
                if (expEl) {
                    job.experience = expEl.textContent.trim();
                }

                // Skills/Tags
                const skillEls = card.querySelectorAll('[class*="skill"], .tag, [class*="tag"]');
                if (skillEls.length > 0) {
                    job.skills = Array.from(skillEls)
                        .map(el => el.textContent.trim())
                        .filter(s => s);
                }

                // Posted date
                const dateEl = (
                    card.querySelector('[class*="date"]') ||
                    card.querySelector('[class*="time"]') ||
                    card.querySelector('[class*="posted"]') ||
                    card.querySelector('[datetime]')
                );
                if (dateEl) {
                    job.posted_date = dateEl.getAttribute('datetime') || dateEl.textContent.trim();
                }

                // Job description snippet
                const descEl = (
                    card.querySelector('[class*="desc"]') ||
                    card.querySelector('[class*="description"]')
                );
                if (descEl) {
                    job.description = descEl.textContent.trim();
                }

                // Job ID from data attribute
                const jobId = card.getAttribute('data-job-id');
                if (jobId) {
                    job.id = jobId;
                } else if (job.url) {
                    // Generate deterministic ID from URL
                    const parts = job.url.split('/').filter(p => p);
                    if (parts.length > 0) {
                        const lastPart = parts[parts.length - 1].split('?')[0];
                        if (lastPart && lastPart !== 'job-detail') {
                            job.id = lastPart;
                        }
                    }
                }

                if (job.title && !job.id) {
                    // Deterministic fallback: hash the title + company (no random!)
                    const hashStr = (job.title + '|' + (job.company_name || '')).replace(/\\s/g, '');
                    let hash = 0;
                    for (let i = 0; i < hashStr.length; i++) {
                        const char = hashStr.charCodeAt(i);
                        hash = ((hash << 5) - hash) + char;
                        hash = hash & hash;
                    }
                    job.id = Math.abs(hash).toString(16).slice(0, 12);
                }

                if (job.title) {
                    jobs.push(job);
                }
            }

            return jobs;
        }
        """

        raw_jobs = await page.evaluate(extract_script)

        if isinstance(raw_jobs, list):
            logger.info("Extracted %d raw jobs from Naukri page", len(raw_jobs))
            return raw_jobs

        logger.warning("Unexpected data format from page evaluation: %s", type(raw_jobs))
        return []

    def parse(self, raw_jobs: list[dict]) -> list[dict]:
        """Parse Naukri job listings into normalized format."""
        parsed = []
        for job in raw_jobs:
            if not job or not isinstance(job, dict):
                continue

            title = job.get("title", "") or ""
            company = job.get("company_name", "") or job.get("company", "") or ""

            # Extract skills from tags and description
            skills = job.get("skills", [])
            if isinstance(skills, str):
                skills = [skills]
            skills = [s for s in skills if s and isinstance(s, str)]
            jd = job.get("description", "") or ""
            if jd:
                skills_from_jd = self._extract_skills(jd)
                for s in skills_from_jd:
                    if s not in skills:
                        skills.append(s)

            # Parse location
            loc = job.get("location", "") or ""
            is_remote = "remote" in loc.lower() or "work from home" in loc.lower() or "wfh" in loc.lower()

            # Parse salary
            salary_min, salary_max = self._parse_salary(job.get("salary", "") or "")

            external_id = job.get("id", "") or job.get("jobId", "") or ""
            if external_id:
                external_id = f"naukri_{external_id}"
            else:
                external_id = None

            normalized = {
                "external_id": external_id,
                "title": title.strip() or "Unknown Position",
                "company_name": company.strip() or "Unknown Company",
                "company_description": None,
                "company_url": None,
                "company_logo": None,
                "location": loc.strip() if loc.strip() else None,
                "location_type": "remote" if is_remote else "onsite",
                "is_remote": is_remote,
                "remote_type": "fully_remote" if is_remote else None,
                "description": jd.strip() if jd.strip() else None,
                "requirements": None,
                "responsibilities": None,
                "required_skills": skills if skills else None,
                "nice_to_have_skills": None,
                "experience_min_years": self._parse_experience(job.get("experience", "") or "")[0],
                "experience_max_years": self._parse_experience(job.get("experience", "") or "")[1],
                "experience_level": None,
                "education_required": None,
                "degree_preferred": None,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_currency": "INR",
                "salary_period": "yearly",
                "salary_visible": salary_min is not None,
                "employment_type": "full_time",
                "industry": None,
                "function": None,
                "department": None,
                "job_url": job.get("url", "") or "",
                "apply_url": job.get("url", "") or "",
                "posted_at": job.get("posted_date", None),
                "status": "active",
                "raw_data": job,
            }
            parsed.append(normalized)

        return parsed

    def _extract_skills(self, text: str) -> list[str]:
        """Extract skill keywords from job description text."""
        if not text:
            return []
        skills = set()
        tech_keywords = [
            r"Python", r"Java(?:Script)?", r"TypeScript", r"React", r"Angular",
            r"Vue\.?js", r"Node\.?js", r"\.NET", r"C#", r"Go(lang)?", r"Rust",
            r"SQL", r"PostgreSQL", r"MySQL", r"MongoDB", r"Redis", r"Docker",
            r"Kubernetes", r"AWS", r"Azure", r"GCP", r"CI/CD", r"Git",
            r"REST\s*API", r"GraphQL", r"Flask", r"Django", r"FastAPI",
            r"TensorFlow", r"PyTorch", r"Machine Learning", r"Deep Learning",
            r"Agile", r"Scrum", r"DevOps",
        ]
        for pattern in tech_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                cleaned = pattern.replace(r"\.", ".").replace(r"\s*", "").replace(r"\?", "")
                skills.add(cleaned)
        return sorted(skills)

    def _parse_salary(self, salary_str: str) -> tuple[Optional[float], Optional[float]]:
        """Parse salary string like '6-12 Lacs PA' or '10L'."""
        if not salary_str or not isinstance(salary_str, str):
            return None, None
        amounts = re.findall(r"(\d+\.?\d*)", salary_str.replace(",", ""))
        if not amounts:
            return None, None
        multiplier = 1
        salary_lower = salary_str.lower()
        if "lac" in salary_lower or "lakh" in salary_lower:
            multiplier = 100000
        elif "cr" in salary_lower or "crore" in salary_lower:
            multiplier = 10000000
        values = [float(a) * multiplier for a in amounts]
        if len(values) >= 2:
            return min(values), max(values)
        return values[0], None

    def _parse_experience(self, exp_str: str) -> tuple[Optional[int], Optional[int]]:
        """Parse experience string like '3-5 yrs'."""
        if not exp_str or not isinstance(exp_str, str):
            return None, None
        amounts = re.findall(r"(\d+)", exp_str)
        if not amounts:
            return None, None
        values = [int(a) for a in amounts]
        if len(values) >= 2:
            return values[0], values[1]
        return values[0], None

    async def close(self) -> None:
        """No persistent browser session to close."""
        pass
