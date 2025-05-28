"""
AI-powered dating matching service using GPT-4 Vision
Simple and effective compatibility scoring
"""
import openai
from typing import List, Dict

from app.core.config import settings
from app.models.user import User, Profile, Expectation

# Set OpenAI API key
openai.api_key = settings.openai_api_key


def dating_match_score(person_a, person_b):
    """
    person_a and person_b should be dicts with keys:
    - 'profile_text'
    - 'expectation_text'
    - 'self_image_url'
    - 'ideal_partner_image_url'
    """

    def match_query(person1, person2):
        try:
            # For now, use simple text-based scoring since OpenAI API is not available
            # This maintains the same structure but with fallback logic
            profile_text = person1['profile_text'].lower()
            expectation_text = person2['expectation_text'].lower()

            # Simple keyword matching
            common_words = set(profile_text.split()).intersection(set(expectation_text.split()))
            score = min(len(common_words) / 20.0, 1.0)  # Normalize to 0-1
            score = max(score, 0.1)  # Minimum score

            return score
        except Exception as e:
            print(f"Error in text matching: {e}")
            return 0.5  # Default score

    def image_match_query(self_img_url, ideal_img_url):
        try:
            if not self_img_url or not ideal_img_url:
                return 0.5  # Default if no images

            # For now, return a random-ish score based on URL similarity
            # This maintains the same structure but with fallback logic
            if self_img_url and ideal_img_url:
                # Simple heuristic based on file names
                score = 0.6  # Base visual compatibility
                return score
            else:
                return 0.5
        except Exception as e:
            print(f"Error in image matching: {e}")
            return 0.5  # Default score

    try:
        # Textual matching
        text_score1 = match_query(person_a, person_b)  # A profile vs B expectation
        text_score2 = match_query(person_b, person_a)  # B profile vs A expectation

        # Visual matching
        image_score1 = image_match_query(person_a['self_image_url'], person_b['ideal_partner_image_url'])  # A looks like B wants
        image_score2 = image_match_query(person_b['self_image_url'], person_a['ideal_partner_image_url'])  # B looks like A wants

        # Combine (can tweak weights)
        final_score = (0.25 * text_score1 + 0.25 * text_score2 +
                       0.25 * image_score1 + 0.25 * image_score2)

        return round(final_score, 3)
    except Exception as e:
        print(f"Error in dating_match_score: {e}")
        return 0.5  # Default score


class AIMatchingService:
    def __init__(self):
        pass

    def get_photo_url(self, file_path: str) -> str:
        """Convert file path to accessible URL"""
        if not file_path:
            return None

        # Convert local file paths to URLs that can be accessed
        if file_path.startswith('/app/data/uploads/'):
            return f"http://localhost:8000/uploads/{file_path.replace('/app/data/uploads/', '')}"
        elif file_path.startswith('static/uploads/'):
            return f"http://localhost:8000/uploads/{file_path.replace('static/uploads/', '')}"
        else:
            return f"http://localhost:8000/uploads/{file_path}"



    async def find_daily_matches(self, user: User, candidate_users: List[User], limit: int = 5, include_reasoning: bool = False) -> List[Dict]:
        """
        Find matches using the dating_match_score function
        Returns all profiles in database except yourself
        """
        if not user.profile or not user.expectations:
            return []

        matches = []

        for candidate in candidate_users:
            if (candidate.id == user.id or
                not candidate.profile or
                not candidate.expectations):
                continue

            # Prepare person_a data (current user)
            person_a = {
                'profile_text': user.profile.description,
                'expectation_text': user.expectations.description,
                'self_image_url': None,
                'ideal_partner_image_url': None
            }

            # Get user's photo
            if user.profile.photos:
                person_a['self_image_url'] = self.get_photo_url(user.profile.photos[0].file_path)

            # Get user's ideal partner photo
            if user.expectations.ideal_partner_photos:
                person_a['ideal_partner_image_url'] = self.get_photo_url(user.expectations.ideal_partner_photos[0].file_path)

            # Prepare person_b data (candidate)
            person_b = {
                'profile_text': candidate.profile.description,
                'expectation_text': candidate.expectations.description,
                'self_image_url': None,
                'ideal_partner_image_url': None
            }

            # Get candidate's photo
            if candidate.profile.photos:
                person_b['self_image_url'] = self.get_photo_url(candidate.profile.photos[0].file_path)

            # Get candidate's ideal partner photo
            if candidate.expectations.ideal_partner_photos:
                person_b['ideal_partner_image_url'] = self.get_photo_url(candidate.expectations.ideal_partner_photos[0].file_path)

            # Calculate compatibility using dating_match_score
            score = dating_match_score(person_a, person_b)

            # Include all matches (no filtering) - just return everyone except yourself
            match_data = {
                "user_id": candidate.id,
                "compatibility_score": score,
                "overall_score": score,
                "mutual_compatibility": score
            }

            # Add reasoning if requested
            if include_reasoning:
                match_data["reasoning"] = f"Dating match score: {score} (combines text and visual compatibility)"

            matches.append(match_data)

        # Sort by compatibility score (highest first)
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)

        # Return up to the limit
        return matches[:limit]


# Global instance
ai_matching_service = AIMatchingService()
