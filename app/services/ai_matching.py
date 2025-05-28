"""
AI-powered bidirectional matching service using only GPT-4o-mini
Specialized for BDSM and alternative lifestyle dating with comprehensive compatibility analysis
"""
import base64
from typing import List, Dict
import openai
import json

from app.core.config import settings
from app.models.user import User, Profile, Expectation


class AIMatchingService:
    def __init__(self):
        # Using only GPT-4o-mini for all analysis - no embeddings
        self.system_prompt = """
You are an expert relationship compatibility analyst specializing in BDSM, kink, and alternative lifestyle dating. You have deep knowledge of:

BDSM FUNDAMENTALS:
- Power exchange dynamics (Dom/sub, Master/slave, Owner/pet, etc.)
- BDSM roles and relationship structures (24/7, bedroom only, switches, etc.)
- Kink categories: Impact play, bondage, sensory play, psychological play, etc.
- Safety principles: SSC (Safe, Sane, Consensual), RACK (Risk Aware Consensual Kink)
- Communication protocols, limits, safewords, aftercare

RELATIONSHIP DYNAMICS:
- Traditional monogamous relationships
- Polyamory, open relationships, relationship anarchy
- LGBTQ+ relationships and gender identities
- Age gap relationships and power dynamics
- Alternative family structures

COMPATIBILITY FACTORS:
- Experience levels and learning curves
- Hard limits vs soft limits vs interests to explore
- Communication styles and emotional needs
- Lifestyle integration (public vs private, 24/7 vs scene-only)
- Long-term relationship goals and growth potential

You analyze compatibility with nuance, respect, and deep understanding of consent culture.
You never judge any consensual adult relationship style or kink preference.
You focus on communication, compatibility, safety, and mutual growth.
"""

    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI Vision API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def calculate_user_score_for_target(
        self,
        user_a_profile: str,
        user_a_expectations: str,
        user_a_ideal_photos: List[str],
        user_b_profile: str,
        user_b_photos: List[str]
    ) -> Dict[str, any]:
        """
        Calculate how well User B matches what User A is looking for
        Returns a score from User A's perspective about User B
        """
        try:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

            # Prepare the analysis prompt
            analysis_prompt = f"""
Analyze how well User B matches what User A is looking for in a partner.

USER A PROFILE: {user_a_profile}

USER A EXPECTATIONS: {user_a_expectations}

USER B PROFILE: {user_b_profile}

Analyze the compatibility from User A's perspective:

1. TEXT COMPATIBILITY: How well does User B's profile match User A's expectations?
   - Role compatibility (Dom/sub dynamics, switches, vanilla preferences)
   - Experience levels and learning interests
   - Kink interests and limits alignment
   - Communication style and emotional needs
   - Lifestyle preferences (24/7, bedroom only, public/private)
   - Relationship structure preferences (monogamy, polyamory, etc.)

2. OVERALL ASSESSMENT: Rate the match from User A's perspective (0.0 to 1.0)
   - 0.0-0.3: Poor match, significant incompatibilities
   - 0.4-0.6: Moderate match, some compatibility
   - 0.7-0.8: Good match, strong compatibility
   - 0.9-1.0: Excellent match, exceptional compatibility

Provide your analysis in this exact JSON format:
{{
    "text_score": 0.85,
    "role_compatibility": 0.90,
    "experience_compatibility": 0.80,
    "kink_compatibility": 0.85,
    "lifestyle_compatibility": 0.80,
    "communication_compatibility": 0.90,
    "overall_score": 0.85,
    "reasoning": "Detailed explanation of why this is or isn't a good match from User A's perspective"
}}
"""

            response = await client.chat.completions.create(
                model=settings.gpt_model,  # gpt-4o-mini
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            # Parse JSON response
            result_text = response.choices[0].message.content.strip()
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx]
                result = json.loads(json_str)

                # Validate and clamp scores
                for key in ['text_score', 'role_compatibility', 'experience_compatibility',
                           'kink_compatibility', 'lifestyle_compatibility', 'communication_compatibility', 'overall_score']:
                    if key in result:
                        result[key] = max(0.0, min(1.0, float(result[key])))

                return result
            else:
                raise ValueError("No valid JSON found in response")

        except Exception as e:
            print(f"Error in user score calculation: {e}")
            return {
                "text_score": 0.5,
                "role_compatibility": 0.5,
                "experience_compatibility": 0.5,
                "kink_compatibility": 0.5,
                "lifestyle_compatibility": 0.5,
                "communication_compatibility": 0.5,
                "overall_score": 0.5,
                "reasoning": "Analysis unavailable due to technical error"
            }

    async def calculate_visual_compatibility(
        self,
        user_a_ideal_photos: List[str],
        user_b_photos: List[str]
    ) -> float:
        """
        Calculate visual compatibility between User A's ideal partner photos and User B's actual photos
        """
        if not user_a_ideal_photos or not user_b_photos:
            return 0.0

        try:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

            # Prepare images for the API call (limit to avoid token limits)
            ideal_images_b64 = [self.encode_image_to_base64(img) for img in user_a_ideal_photos[:2]]
            actual_images_b64 = [self.encode_image_to_base64(img) for img in user_b_photos[:3]]

            # Create the visual analysis prompt
            visual_prompt = """
Analyze the visual compatibility between the ideal partner photos and the actual person's photos.

Consider:
- Physical appearance and aesthetic preferences
- Style, fashion, and presentation
- Energy, vibe, and overall appeal
- Body type and physical characteristics
- How well the actual person matches the ideal preferences

Rate the visual compatibility from 0.0 to 1.0:
- 0.0-0.3: Poor visual match
- 0.4-0.6: Moderate visual compatibility
- 0.7-0.8: Good visual match
- 0.9-1.0: Excellent visual compatibility

Respond with only a single number between 0.0 and 1.0.
"""

            # Prepare messages with images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": visual_prompt},
                        {"type": "text", "text": "IDEAL PARTNER PHOTOS:"}
                    ]
                }
            ]

            # Add ideal partner photos
            for img_b64 in ideal_images_b64:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            messages[0]["content"].append({"type": "text", "text": "ACTUAL PERSON PHOTOS:"})

            # Add actual person photos
            for img_b64 in actual_images_b64:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            # Make API call
            response = await client.chat.completions.create(
                model=settings.gpt_model,  # gpt-4o-mini supports vision
                messages=messages,
                max_tokens=10,
                temperature=0.3
            )

            # Extract and validate the score
            score_text = response.choices[0].message.content.strip()
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))
            except ValueError:
                return 0.5

        except Exception as e:
            print(f"Error in visual compatibility analysis: {e}")
            return 0.0

    async def get_llm_text_similarity_fallback(self, text1: str, text2: str) -> float:
        """Fallback method using LLM to assess text similarity when embeddings fail"""
        try:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

            prompt = """
            You are an expert at analyzing text similarity and semantic meaning.

            I will provide you with two texts. Please analyze how similar they are in terms of:
            - Semantic meaning and content
            - Themes and topics discussed
            - Overall compatibility of ideas

            Rate the similarity on a scale from 0.0 to 1.0, where:
            - 0.0 = Completely different/incompatible
            - 0.5 = Moderately similar
            - 1.0 = Very similar/highly compatible

            Respond with only a single number between 0.0 and 1.0.
            """

            response = await client.chat.completions.create(
                model=settings.gpt_model,  # Use configured model (gpt-4o-mini)
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Text 1: {text1}\n\nText 2: {text2}"}
                ],
                max_tokens=10,
                temperature=0.3
            )

            # Extract and validate the score
            score_text = response.choices[0].message.content.strip()
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            except ValueError:
                return 0.5  # Default score if parsing fails

        except Exception as e:
            print(f"Error in LLM text similarity fallback: {e}")
            return 0.5  # Default fallback score

    async def get_llm_text_compatibility(self, profile_description: str, expectation_description: str) -> Dict[str, float]:
        """
        Use LLM to analyze deep text compatibility between profile and expectations
        """
        try:
            prompt = """
            You are an expert relationship compatibility analyst specializing in deep personality and lifestyle matching for all types of relationships and lifestyles.

            I will provide you with:
            1. A person's profile description (how they describe themselves)
            2. Someone's expectation description (what they're looking for in a partner)

            Analyze the compatibility across these dimensions:
            - Personality compatibility (values, traits, communication style)
            - Lifestyle compatibility (interests, goals, life stage, relationship dynamics)
            - Emotional compatibility (emotional needs, relationship style, intimacy preferences)
            - Long-term potential (shared vision, growth compatibility, lifestyle sustainability)

            Be open-minded and non-judgmental about all relationship styles including:
            - Traditional monogamous relationships
            - Polyamorous and open relationships
            - BDSM and kink lifestyles
            - Alternative relationship structures
            - LGBTQ+ relationships
            - Age gap relationships
            - Any other consensual adult relationship preferences

            Focus on compatibility, communication, consent, and mutual respect regardless of the specific lifestyle.

            Provide your analysis in this exact JSON format:
            {
                "overall_score": 0.85,
                "personality_score": 0.90,
                "lifestyle_score": 0.80,
                "emotional_score": 0.85,
                "longterm_score": 0.85,
                "reasoning": "Brief explanation of the compatibility analysis"
            }

            Scores should be between 0.0 and 1.0. Be thoughtful and nuanced in your analysis.
            """

            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=settings.gpt_model,  # Use configured model (gpt-4o-mini)
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Profile: {profile_description}\n\nExpectations: {expectation_description}"}
                ],
                max_tokens=300,
                temperature=0.3
            )

            # Parse the JSON response
            import json
            result_text = response.choices[0].message.content.strip()

            # Extract JSON from the response (in case there's extra text)
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx]
                result = json.loads(json_str)

                # Validate and clamp scores
                for key in ['overall_score', 'personality_score', 'lifestyle_score', 'emotional_score', 'longterm_score']:
                    if key in result:
                        result[key] = max(0.0, min(1.0, float(result[key])))

                return result
            else:
                raise ValueError("No valid JSON found in response")

        except Exception as e:
            print(f"Error in LLM text compatibility analysis: {e}")
            # Return default scores if LLM fails
            return {
                "overall_score": 0.5,
                "personality_score": 0.5,
                "lifestyle_score": 0.5,
                "emotional_score": 0.5,
                "longterm_score": 0.5,
                "reasoning": "Analysis unavailable due to technical error"
            }

    async def get_visual_compatibility(self, user_photos: List[str], expectation_images: List[str]) -> float:
        """
        Use GPT-4 Vision to analyze visual compatibility between user photos and expectation images
        """
        if not user_photos or not expectation_images:
            return 0.0

        try:
            # Prepare images for the API call
            user_images_b64 = [self.encode_image_to_base64(photo) for photo in user_photos[:3]]  # Limit to 3 photos
            expectation_images_b64 = [self.encode_image_to_base64(img) for img in expectation_images[:2]]  # Limit to 2 expectation images

            # Create the prompt
            prompt = """
            You are an expert at analyzing visual compatibility for dating matches.

            I will show you:
            1. Photos of a person (user photos)
            2. Example images representing someone's ideal partner preferences

            Please analyze the visual compatibility between the person in the photos and the preferences shown in the example images.
            Consider factors like:
            - Style and aesthetic preferences
            - Overall vibe and energy
            - Visual harmony and compatibility

            Rate the visual compatibility on a scale from 0.0 to 1.0, where:
            - 0.0 = No visual compatibility
            - 0.5 = Moderate compatibility
            - 1.0 = Excellent visual compatibility

            Respond with only a single number between 0.0 and 1.0.
            """

            # Prepare messages with images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "text", "text": "User photos:"}
                    ]
                }
            ]

            # Add user photos
            for img_b64 in user_images_b64:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            messages[0]["content"].append({"type": "text", "text": "Expectation/preference images:"})

            # Add expectation images
            for img_b64 in expectation_images_b64:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            # Make API call
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=settings.gpt_model,
                messages=messages,
                max_tokens=10
            )

            # Extract and validate the score
            score_text = response.choices[0].message.content.strip()
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            except ValueError:
                return 0.5  # Default score if parsing fails

        except Exception as e:
            print(f"Error in visual compatibility analysis: {e}")
            return 0.0

    async def get_ideal_partner_compatibility(self, user_photos: List[str], ideal_partner_photos: List[str]) -> float:
        """
        Use GPT-4 Vision to analyze compatibility between user photos and ideal partner photos
        """
        if not user_photos or not ideal_partner_photos:
            return 0.0

        try:
            # Prepare images for the API call
            user_images_b64 = [self.encode_image_to_base64(photo) for photo in user_photos[:3]]  # Limit to 3 photos
            ideal_images_b64 = [self.encode_image_to_base64(img) for img in ideal_partner_photos[:3]]  # Limit to 3 ideal photos

            # Create the prompt
            prompt = """
            You are an expert at analyzing visual compatibility for dating matches.

            I will show you:
            1. Photos of a person (actual user photos)
            2. Photos representing someone's ideal partner appearance

            Please analyze how well the actual person matches the ideal partner preferences.
            Consider factors like:
            - Physical appearance compatibility
            - Style and aesthetic preferences
            - Overall visual appeal and attraction
            - Energy and vibe compatibility

            Rate the compatibility on a scale from 0.0 to 1.0, where:
            - 0.0 = No visual match with ideal preferences
            - 0.5 = Moderate match with some appealing qualities
            - 1.0 = Excellent match with ideal partner preferences

            Respond with only a single number between 0.0 and 1.0.
            """

            # Prepare messages with images
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "text", "text": "Actual person photos:"}
                    ]
                }
            ]

            # Add user photos
            for img_b64 in user_images_b64:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            messages[0]["content"].append({"type": "text", "text": "Ideal partner photos:"})

            # Add ideal partner photos
            for img_b64 in ideal_images_b64:
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            # Make API call
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=settings.gpt_model,
                messages=messages,
                max_tokens=10
            )

            # Extract and validate the score
            score_text = response.choices[0].message.content.strip()
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))  # Clamp between 0 and 1
            except ValueError:
                return 0.5  # Default score if parsing fails

        except Exception as e:
            print(f"Error in ideal partner compatibility analysis: {e}")
            return 0.0

    async def generate_compatibility_reasoning(
        self,
        user_profile: Profile,
        target_profile: Profile,
        user_expectations: Expectation,
        target_expectations: Expectation,
        scores: Dict[str, float],
        llm_analysis: Dict[str, any] = None
    ) -> Dict[str, str]:
        """
        Generate detailed reasoning for the compatibility match using LLM
        """
        try:
            prompt = """
            You are an expert relationship counselor providing detailed compatibility analysis for dating matches across all relationship styles and lifestyles.

            I will provide you with:
            1. Two user profiles (how they describe themselves)
            2. Their expectations (what they're looking for)
            3. Compatibility scores from our analysis

            Generate a comprehensive but concise compatibility report that includes:
            - Overall compatibility summary
            - Key strengths of this match
            - Potential areas to explore together
            - Conversation starters based on shared interests
            - Growth potential and relationship development

            Be inclusive and supportive of all consensual adult relationship styles including:
            - Traditional relationships, polyamory, BDSM/kink, LGBTQ+, alternative lifestyles
            - Focus on communication, consent, compatibility, and mutual respect
            - Avoid judgment and embrace diversity in relationship preferences

            Keep the tone positive, encouraging, and insightful. Focus on helping them connect meaningfully.
            Provide your response in this JSON format:
            {
                "summary": "2-3 sentence overall compatibility summary",
                "strengths": "Key compatibility strengths",
                "shared_interests": "Areas of mutual interest to explore",
                "conversation_starters": "3 specific conversation starter suggestions",
                "growth_potential": "How this relationship could help both people grow"
            }
            """

            # Prepare the context
            context = f"""
            User 1 Profile: {user_profile.description}
            User 1 Looking For: {user_expectations.description}

            User 2 Profile: {target_profile.description}
            User 2 Looking For: {target_expectations.description}

            Compatibility Scores:
            - Overall: {scores.get('overall_score', 0):.2f}
            - Text Similarity: {scores.get('text_similarity', 0):.2f}
            - Visual Compatibility: {scores.get('visual_similarity', 0):.2f}
            """

            if llm_analysis:
                context += f"""
            Detailed Analysis:
            - Personality: {llm_analysis.get('personality_score', 0):.2f}
            - Lifestyle: {llm_analysis.get('lifestyle_score', 0):.2f}
            - Emotional: {llm_analysis.get('emotional_score', 0):.2f}
            - Long-term: {llm_analysis.get('longterm_score', 0):.2f}
            - Reasoning: {llm_analysis.get('reasoning', 'N/A')}
            """

            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=settings.gpt_model,  # Use configured model (gpt-4o-mini)
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": context}
                ],
                max_tokens=500,
                temperature=0.7
            )

            # Parse the JSON response
            import json
            result_text = response.choices[0].message.content.strip()

            # Extract JSON from the response
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx]
                result = json.loads(json_str)
                return result
            else:
                raise ValueError("No valid JSON found in response")

        except Exception as e:
            print(f"Error in compatibility reasoning generation: {e}")
            # Return default reasoning if LLM fails
            return {
                "summary": f"This match shows {scores.get('overall_score', 0.5):.0%} compatibility based on profile analysis.",
                "strengths": "Both users show potential for meaningful connection.",
                "shared_interests": "Explore common interests through conversation.",
                "conversation_starters": "Ask about their interests, goals, and experiences.",
                "growth_potential": "This connection offers opportunities for mutual growth and understanding."
            }

    async def calculate_bidirectional_compatibility(
        self,
        user_a: User,
        user_b: User,
        include_reasoning: bool = False
    ) -> Dict[str, any]:
        """
        NEW BIDIRECTIONAL MATCHING: Calculate how well each user matches what the other is looking for
        Only show matches when BOTH scores are high (mutual compatibility)
        """
        # Get user data
        user_a_profile = user_a.profile.description
        user_a_expectations = user_a.expectations.description
        user_a_photos = [photo.file_path for photo in user_a.profile.photos]
        user_a_ideal_photos = [photo.file_path for photo in user_a.expectations.ideal_partner_photos]

        user_b_profile = user_b.profile.description
        user_b_expectations = user_b.expectations.description
        user_b_photos = [photo.file_path for photo in user_b.profile.photos]
        user_b_ideal_photos = [photo.file_path for photo in user_b.expectations.ideal_partner_photos]

        # Calculate User A's score for User B (how well B matches what A wants)
        a_scores_b = await self.calculate_user_score_for_target(
            user_a_profile, user_a_expectations, user_a_ideal_photos,
            user_b_profile, user_b_photos
        )

        # Calculate User B's score for User A (how well A matches what B wants)
        b_scores_a = await self.calculate_user_score_for_target(
            user_b_profile, user_b_expectations, user_b_ideal_photos,
            user_a_profile, user_a_photos
        )

        # Calculate visual compatibility scores
        visual_a_to_b = await self.calculate_visual_compatibility(user_a_ideal_photos, user_b_photos)
        visual_b_to_a = await self.calculate_visual_compatibility(user_b_ideal_photos, user_a_photos)

        # Combine text and visual scores for each direction
        a_overall_score = (a_scores_b["overall_score"] * 0.7) + (visual_a_to_b * 0.3)
        b_overall_score = (b_scores_a["overall_score"] * 0.7) + (visual_b_to_a * 0.3)

        # BIDIRECTIONAL REQUIREMENT: Both scores must be high for a match
        # Only show if both users would be satisfied with each other
        mutual_compatibility = min(a_overall_score, b_overall_score)  # Lowest score determines match quality
        average_compatibility = (a_overall_score + b_overall_score) / 2

        result = {
            # Bidirectional scores
            "user_a_score_for_b": a_overall_score,  # How much A likes B
            "user_b_score_for_a": b_overall_score,  # How much B likes A
            "mutual_compatibility": mutual_compatibility,  # Minimum of both (strictest)
            "average_compatibility": average_compatibility,  # Average of both

            # Use mutual compatibility as the main score (both must be satisfied)
            "overall_score": mutual_compatibility,

            # Detailed breakdowns
            "a_text_score": a_scores_b["overall_score"],
            "b_text_score": b_scores_a["overall_score"],
            "a_visual_score": visual_a_to_b,
            "b_visual_score": visual_b_to_a,

            # Role and compatibility details
            "role_compatibility": (a_scores_b.get("role_compatibility", 0.5) + b_scores_a.get("role_compatibility", 0.5)) / 2,
            "experience_compatibility": (a_scores_b.get("experience_compatibility", 0.5) + b_scores_a.get("experience_compatibility", 0.5)) / 2,
            "kink_compatibility": (a_scores_b.get("kink_compatibility", 0.5) + b_scores_a.get("kink_compatibility", 0.5)) / 2,
            "lifestyle_compatibility": (a_scores_b.get("lifestyle_compatibility", 0.5) + b_scores_a.get("lifestyle_compatibility", 0.5)) / 2,
            "communication_compatibility": (a_scores_b.get("communication_compatibility", 0.5) + b_scores_a.get("communication_compatibility", 0.5)) / 2,

            # Legacy compatibility for existing code
            "text_similarity": (a_scores_b["overall_score"] + b_scores_a["overall_score"]) / 2,
            "visual_similarity": (visual_a_to_b + visual_b_to_a) / 2
        }

        # Add reasoning if requested
        if include_reasoning:
            reasoning = await self.generate_bidirectional_reasoning(
                user_a, user_b, a_scores_b, b_scores_a, result
            )
            result["reasoning"] = reasoning

        return result

    async def generate_bidirectional_reasoning(
        self,
        user_a: User,
        user_b: User,
        a_scores_b: Dict,
        b_scores_a: Dict,
        compatibility_result: Dict
    ) -> Dict[str, str]:
        """
        Generate detailed reasoning for bidirectional compatibility
        """
        try:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

            reasoning_prompt = f"""
Generate a comprehensive compatibility analysis for this bidirectional match.

USER A PROFILE: {user_a.profile.description}
USER A EXPECTATIONS: {user_a.expectations.description}

USER B PROFILE: {user_b.profile.description}
USER B EXPECTATIONS: {user_b.expectations.description}

COMPATIBILITY SCORES:
- User A's satisfaction with User B: {compatibility_result['user_a_score_for_b']:.2f}
- User B's satisfaction with User A: {compatibility_result['user_b_score_for_a']:.2f}
- Mutual compatibility: {compatibility_result['mutual_compatibility']:.2f}
- Role compatibility: {compatibility_result['role_compatibility']:.2f}
- Kink compatibility: {compatibility_result['kink_compatibility']:.2f}

USER A'S PERSPECTIVE: {a_scores_b.get('reasoning', 'N/A')}
USER B'S PERSPECTIVE: {b_scores_a.get('reasoning', 'N/A')}

Provide a detailed analysis in JSON format:
{{
    "summary": "2-3 sentence overall compatibility summary focusing on mutual satisfaction",
    "strengths": "Key compatibility strengths from both perspectives",
    "role_dynamics": "Analysis of Dom/sub or other role compatibility",
    "shared_interests": "BDSM/kink interests and lifestyle compatibility",
    "conversation_starters": "3 specific conversation topics based on their profiles",
    "growth_potential": "How this relationship could help both people grow in their journey"
}}
"""

            response = await client.chat.completions.create(
                model=settings.gpt_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": reasoning_prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )

            # Parse JSON response
            result_text = response.choices[0].message.content.strip()
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = result_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")

        except Exception as e:
            print(f"Error in bidirectional reasoning generation: {e}")
            return {
                "summary": f"This bidirectional match shows {compatibility_result['mutual_compatibility']:.0%} mutual compatibility.",
                "strengths": "Both users show potential for meaningful connection.",
                "role_dynamics": "Compatible relationship dynamics and roles.",
                "shared_interests": "Explore common BDSM/kink interests through conversation.",
                "conversation_starters": "Ask about their experience, interests, and relationship goals.",
                "growth_potential": "This connection offers opportunities for mutual exploration and growth."
            }

    async def find_daily_matches(self, user: User, candidate_users: List[User], limit: int = 5, include_reasoning: bool = False) -> List[Dict]:
        """
        NEW BIDIRECTIONAL MATCHING: Find matches where BOTH users are highly satisfied
        Only shows matches when both users would be happy with each other
        """
        if not user.profile or not user.expectations:
            return []

        matches = []

        for candidate in candidate_users:
            if (candidate.id == user.id or
                not candidate.profile or
                not candidate.expectations):
                continue

            # Use NEW bidirectional compatibility calculation
            compatibility = await self.calculate_bidirectional_compatibility(
                user,
                candidate,
                include_reasoning=include_reasoning
            )

            # STRICT BIDIRECTIONAL FILTERING: Only include if BOTH users are satisfied
            # This ensures mutual compatibility rather than one-sided attraction
            mutual_score = compatibility["mutual_compatibility"]

            # Only include matches where both users score each other highly
            # This prevents showing matches where only one person would be interested
            if mutual_score >= 0.6:  # Both users must score each other at least 60%
                match_data = {
                    "user_id": candidate.id,
                    "compatibility_score": mutual_score,  # Use mutual compatibility as main score

                    # Bidirectional scores for transparency
                    "user_satisfaction": compatibility["user_a_score_for_b"],  # How much current user likes candidate
                    "candidate_satisfaction": compatibility["user_b_score_for_a"],  # How much candidate likes current user
                    "mutual_compatibility": mutual_score,
                    "average_compatibility": compatibility["average_compatibility"],

                    # Detailed compatibility breakdowns
                    "text_similarity": compatibility["text_similarity"],
                    "visual_similarity": compatibility["visual_similarity"],
                    "role_compatibility": compatibility["role_compatibility"],
                    "experience_compatibility": compatibility["experience_compatibility"],
                    "kink_compatibility": compatibility["kink_compatibility"],
                    "lifestyle_compatibility": compatibility["lifestyle_compatibility"],
                    "communication_compatibility": compatibility["communication_compatibility"],

                    # Individual scores for debugging
                    "user_text_score": compatibility["a_text_score"],
                    "candidate_text_score": compatibility["b_text_score"],
                    "user_visual_score": compatibility["a_visual_score"],
                    "candidate_visual_score": compatibility["b_visual_score"]
                }

                # Add reasoning if requested
                if include_reasoning and "reasoning" in compatibility:
                    match_data["reasoning"] = compatibility["reasoning"]

                matches.append(match_data)

        # Sort by mutual compatibility (strictest measure) and return top matches
        matches.sort(key=lambda x: x["mutual_compatibility"], reverse=True)

        # Apply additional filtering: only show very high quality matches
        high_quality_matches = [m for m in matches if m["mutual_compatibility"] >= 0.7]

        return high_quality_matches[:limit]


# Global instance
ai_matching_service = AIMatchingService()
