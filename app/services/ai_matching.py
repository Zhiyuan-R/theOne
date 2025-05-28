"""
AI-powered matching service using only OpenAI APIs (GPT-4, GPT-4 Vision, and Embeddings)
"""
import base64
from typing import List, Dict
import openai

from app.core.config import settings
from app.models.user import User, Profile, Expectation


class AIMatchingService:
    def __init__(self):
        # Using only OpenAI APIs - no open-source models
        pass

    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI Vision API"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    async def get_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts using OpenAI embeddings"""
        try:
            client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

            # Get embeddings for both texts
            response1 = await client.embeddings.create(
                model="text-embedding-3-small",  # OpenAI's latest embedding model
                input=text1
            )
            response2 = await client.embeddings.create(
                model="text-embedding-3-small",
                input=text2
            )

            # Extract embeddings
            embedding1 = response1.data[0].embedding
            embedding2 = response2.data[0].embedding

            # Calculate cosine similarity
            dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
            magnitude1 = sum(a * a for a in embedding1) ** 0.5
            magnitude2 = sum(a * a for a in embedding2) ** 0.5

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            similarity = dot_product / (magnitude1 * magnitude2)
            return max(0.0, min(1.0, similarity))  # Clamp between 0 and 1

        except Exception as e:
            print(f"Error in OpenAI text similarity: {e}")
            # Fallback to simple text analysis using LLM
            return await self.get_llm_text_similarity_fallback(text1, text2)

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

    async def calculate_compatibility_score(
        self,
        user_profile: Profile,
        target_profile: Profile,
        user_expectations: Expectation,
        target_expectations: Expectation,
        include_reasoning: bool = False
    ) -> Dict[str, any]:
        """
        Calculate comprehensive compatibility score between two users with enhanced LLM analysis
        """
        # 1. OpenAI embeddings text similarity (bidirectional) - for baseline
        user_to_target_text_sim = await self.get_text_similarity(
            user_expectations.description,
            target_profile.description
        )
        target_to_user_text_sim = await self.get_text_similarity(
            target_expectations.description,
            user_profile.description
        )
        basic_text_similarity = (user_to_target_text_sim + target_to_user_text_sim) / 2

        # 2. Enhanced LLM text compatibility analysis (bidirectional)
        user_to_target_llm = await self.get_llm_text_compatibility(
            target_profile.description,
            user_expectations.description
        )
        target_to_user_llm = await self.get_llm_text_compatibility(
            user_profile.description,
            target_expectations.description
        )

        # Average the LLM scores
        llm_text_score = (user_to_target_llm["overall_score"] + target_to_user_llm["overall_score"]) / 2

        # Combine basic similarity with LLM analysis (weighted)
        enhanced_text_similarity = (basic_text_similarity * 0.3) + (llm_text_score * 0.7)

        # 3. Visual compatibility (bidirectional) - Enhanced with ideal partner photos
        user_photos = [photo.file_path for photo in user_profile.photos]
        target_photos = [photo.file_path for photo in target_profile.photos]
        user_expectation_images = [img.file_path for img in user_expectations.example_images]
        target_expectation_images = [img.file_path for img in target_expectations.example_images]
        user_ideal_partner_photos = [img.file_path for img in user_expectations.ideal_partner_photos]
        target_ideal_partner_photos = [img.file_path for img in target_expectations.ideal_partner_photos]

        # Original visual compatibility (profile photos vs expectation images)
        user_to_target_visual = await self.get_visual_compatibility(
            target_photos, user_expectation_images
        )
        target_to_user_visual = await self.get_visual_compatibility(
            user_photos, target_expectation_images
        )

        # New ideal partner photo compatibility (profile photos vs ideal partner photos)
        user_to_target_ideal = await self.get_ideal_partner_compatibility(
            target_photos, user_ideal_partner_photos
        )
        target_to_user_ideal = await self.get_ideal_partner_compatibility(
            user_photos, target_ideal_partner_photos
        )

        # Combine both visual compatibility scores
        # Weight: 60% ideal partner matching, 40% expectation images
        user_to_target_combined = (user_to_target_ideal * 0.6) + (user_to_target_visual * 0.4)
        target_to_user_combined = (target_to_user_ideal * 0.6) + (target_to_user_visual * 0.4)
        visual_similarity = (user_to_target_combined + target_to_user_combined) / 2

        # 4. Calculate overall compatibility with enhanced weights
        text_weight = 0.65  # Increased weight for enhanced text analysis
        visual_weight = 0.35

        overall_score = (enhanced_text_similarity * text_weight) + (visual_similarity * visual_weight)

        # 5. Prepare result
        result = {
            "overall_score": overall_score,
            "text_similarity": enhanced_text_similarity,
            "visual_similarity": visual_similarity,
            "basic_text_similarity": basic_text_similarity,
            "llm_text_score": llm_text_score,
            "personality_score": (user_to_target_llm.get("personality_score", 0.5) + target_to_user_llm.get("personality_score", 0.5)) / 2,
            "lifestyle_score": (user_to_target_llm.get("lifestyle_score", 0.5) + target_to_user_llm.get("lifestyle_score", 0.5)) / 2,
            "emotional_score": (user_to_target_llm.get("emotional_score", 0.5) + target_to_user_llm.get("emotional_score", 0.5)) / 2,
            "longterm_score": (user_to_target_llm.get("longterm_score", 0.5) + target_to_user_llm.get("longterm_score", 0.5)) / 2,
            # New ideal partner compatibility scores
            "ideal_partner_score": (user_to_target_ideal + target_to_user_ideal) / 2,
            "expectation_visual_score": (user_to_target_visual + target_to_user_visual) / 2
        }

        # 6. Generate detailed reasoning if requested
        if include_reasoning:
            reasoning = await self.generate_compatibility_reasoning(
                user_profile, target_profile, user_expectations, target_expectations,
                result, user_to_target_llm
            )
            result["reasoning"] = reasoning

        return result

    async def find_daily_matches(self, user: User, candidate_users: List[User], limit: int = 5, include_reasoning: bool = False) -> List[Dict]:
        """
        Find the best daily matches for a user with enhanced AI analysis
        """
        if not user.profile or not user.expectations:
            return []

        matches = []

        for candidate in candidate_users:
            if (candidate.id == user.id or
                not candidate.profile or
                not candidate.expectations):
                continue

            # Calculate enhanced compatibility with optional reasoning
            compatibility = await self.calculate_compatibility_score(
                user.profile,
                candidate.profile,
                user.expectations,
                candidate.expectations,
                include_reasoning=include_reasoning
            )

            match_data = {
                "user_id": candidate.id,
                "compatibility_score": compatibility["overall_score"],
                "text_similarity": compatibility["text_similarity"],
                "visual_similarity": compatibility["visual_similarity"],
                "basic_text_similarity": compatibility["basic_text_similarity"],
                "llm_text_score": compatibility["llm_text_score"],
                "personality_score": compatibility["personality_score"],
                "lifestyle_score": compatibility["lifestyle_score"],
                "emotional_score": compatibility["emotional_score"],
                "longterm_score": compatibility["longterm_score"],
                "ideal_partner_score": compatibility.get("ideal_partner_score", 0.0),
                "expectation_visual_score": compatibility.get("expectation_visual_score", 0.0)
            }

            # Add reasoning if requested
            if include_reasoning and "reasoning" in compatibility:
                match_data["reasoning"] = compatibility["reasoning"]

            matches.append(match_data)

        # Sort by compatibility score and return top matches
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return matches[:limit]


# Global instance
ai_matching_service = AIMatchingService()
