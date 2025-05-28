#!/usr/bin/env python3
"""
Test the new features: auto-save and mismatch information
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_matching import dating_match_score

def test_mismatch_detection():
    """Test the mismatch detection feature"""
    
    print("Testing Mismatch Detection Feature:")
    print("=" * 50)
    
    # Test case 1: Good match
    person_a = {
        'profile_text': 'I love hiking, reading books, and traveling. I am kind and adventurous.',
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
    
    score, details = dating_match_score(person_a, person_b, return_details=True)
    print(f"Test 1 - Good Match:")
    print(f"  Score: {score}")
    print(f"  Mismatches A->B: {details.get('mismatches_a_to_b', [])}")
    print(f"  Mismatches B->A: {details.get('mismatches_b_to_a', [])}")
    print(f"  Photo Issues: {details.get('photo_issues', [])}")
    print()
    
    # Test case 2: Mismatch in interests
    person_c = {
        'profile_text': 'I love video games and staying indoors',
        'expectation_text': 'Looking for someone who enjoys gaming and technology',
        'self_image_url': None,
        'ideal_partner_image_url': None
    }
    
    score2, details2 = dating_match_score(person_a, person_c, return_details=True)
    print(f"Test 2 - Interest Mismatch:")
    print(f"  Score: {score2}")
    print(f"  Mismatches A->C: {details2.get('mismatches_a_to_b', [])}")
    print(f"  Mismatches C->A: {details2.get('mismatches_b_to_a', [])}")
    print(f"  Photo Issues: {details2.get('photo_issues', [])}")
    print()
    
    # Test case 3: Brief profile
    person_d = {
        'profile_text': 'xx',
        'expectation_text': 'Looking for someone intelligent, kind, funny, and adventurous who loves travel and music',
        'self_image_url': None,
        'ideal_partner_image_url': None
    }
    
    score3, details3 = dating_match_score(person_a, person_d, return_details=True)
    print(f"Test 3 - Brief Profile:")
    print(f"  Score: {score3}")
    print(f"  Mismatches A->D: {details3.get('mismatches_a_to_b', [])}")
    print(f"  Mismatches D->A: {details3.get('mismatches_b_to_a', [])}")
    print(f"  Photo Issues: {details3.get('photo_issues', [])}")
    print()
    
    # Generate mismatch messages like the app would
    print("Generated Mismatch Messages:")
    print("-" * 30)
    
    for i, (test_name, details) in enumerate([
        ("Good Match", details),
        ("Interest Mismatch", details2), 
        ("Brief Profile", details3)
    ], 1):
        mismatch_messages = []
        
        if details.get("mismatches_a_to_b"):
            mismatch_messages.extend(details["mismatches_a_to_b"])
        
        if details.get("photo_issues"):
            mismatch_messages.extend(details["photo_issues"])
        
        if mismatch_messages:
            mismatch_text = ", ".join(mismatch_messages)
            message = f"Your match is perfect unless {mismatch_text}"
        else:
            message = "This appears to be a great match!"
        
        print(f"Test {i} ({test_name}): {message}")

if __name__ == "__main__":
    test_mismatch_detection()
