#!/usr/bin/env python3
"""
Test the final dating_match_score algorithm
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_matching import dating_match_score

def test_dating_match_score():
    """Test the dating_match_score function directly"""
    
    print("Testing dating_match_score function:")
    print("=" * 50)
    
    # Test case 1: Similar interests
    person_a = {
        'profile_text': 'I love hiking, reading books, and traveling. I am adventurous and kind.',
        'expectation_text': 'Looking for someone who enjoys outdoor activities and reading',
        'self_image_url': 'http://localhost:8000/uploads/profiles/test1.jpg',
        'ideal_partner_image_url': 'http://localhost:8000/uploads/ideal_partners/test1.jpg'
    }
    
    person_b = {
        'profile_text': 'I enjoy hiking, love books, and travel frequently. I am kind and adventurous.',
        'expectation_text': 'Seeking someone who likes outdoor activities and literature',
        'self_image_url': 'http://localhost:8000/uploads/profiles/test2.jpg',
        'ideal_partner_image_url': 'http://localhost:8000/uploads/ideal_partners/test2.jpg'
    }
    
    score1 = dating_match_score(person_a, person_b)
    print(f"Test 1 - Similar interests:")
    print(f"  Person A: {person_a['profile_text'][:50]}...")
    print(f"  Person B: {person_b['profile_text'][:50]}...")
    print(f"  Score: {score1}")
    print()
    
    # Test case 2: Different interests
    person_c = {
        'profile_text': 'I love video games, coding, and staying indoors',
        'expectation_text': 'Looking for someone who enjoys technology and gaming',
        'self_image_url': 'http://localhost:8000/uploads/profiles/test3.jpg',
        'ideal_partner_image_url': 'http://localhost:8000/uploads/ideal_partners/test3.jpg'
    }
    
    score2 = dating_match_score(person_a, person_c)
    print(f"Test 2 - Different interests:")
    print(f"  Person A: {person_a['profile_text'][:50]}...")
    print(f"  Person C: {person_c['profile_text'][:50]}...")
    print(f"  Score: {score2}")
    print()
    
    # Test case 3: Minimal data (like current users)
    person_d = {
        'profile_text': 'xx',
        'expectation_text': 'yy',
        'self_image_url': None,
        'ideal_partner_image_url': None
    }
    
    score3 = dating_match_score(person_a, person_d)
    print(f"Test 3 - Minimal data:")
    print(f"  Person A: {person_a['profile_text'][:50]}...")
    print(f"  Person D: {person_d['profile_text']}")
    print(f"  Score: {score3}")
    print()
    
    print("Algorithm Structure:")
    print("- Text matching: 25% + 25% = 50%")
    print("- Image matching: 25% + 25% = 50%")
    print("- Total: 100%")
    print("- Returns rounded score to 3 decimal places")

if __name__ == "__main__":
    test_dating_match_score()
