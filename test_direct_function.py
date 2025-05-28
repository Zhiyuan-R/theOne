#!/usr/bin/env python3
"""
Test the dating_match_score function directly
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_matching import dating_match_score

def test_direct_function():
    """Test the dating_match_score function directly"""
    
    # Test data
    person_a = {
        'profile_text': 'I am a 25-year-old software engineer who loves hiking and reading',
        'expectation_text': 'Looking for someone kind and intelligent',
        'self_image_url': 'http://localhost:8000/uploads/profiles/test1.jpg',
        'ideal_partner_image_url': 'http://localhost:8000/uploads/ideal_partners/test1.jpg'
    }
    
    person_b = {
        'profile_text': 'I am a 23-year-old teacher who enjoys hiking and books',
        'expectation_text': 'Seeking a smart and caring partner',
        'self_image_url': 'http://localhost:8000/uploads/profiles/test2.jpg',
        'ideal_partner_image_url': 'http://localhost:8000/uploads/ideal_partners/test2.jpg'
    }
    
    print("Testing dating_match_score function:")
    print(f"Person A profile: {person_a['profile_text']}")
    print(f"Person A expectations: {person_a['expectation_text']}")
    print(f"Person B profile: {person_b['profile_text']}")
    print(f"Person B expectations: {person_b['expectation_text']}")
    
    score = dating_match_score(person_a, person_b)
    print(f"\nCompatibility score: {score}")
    
    # Test with different data
    person_c = {
        'profile_text': 'xx',
        'expectation_text': 'yy',
        'self_image_url': None,
        'ideal_partner_image_url': None
    }
    
    score2 = dating_match_score(person_a, person_c)
    print(f"Score with minimal data: {score2}")

if __name__ == "__main__":
    test_direct_function()
