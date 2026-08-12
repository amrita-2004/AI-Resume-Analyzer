from app import app
from flask import render_template
import sys

def test_jinja_rendering():
    """
    Test script to verify that the index.html Jinja template renders correctly
    with the expected context variables, without running the Flask server.
    """
    # Create a test request context so that Flask-specific functions like url_for work
    with app.test_request_context():
        try:
            # Mock data representing a successful resume analysis
            mock_skills = {
                "Programming Languages": ["Python", "JavaScript", "Go"],
                "Cloud & DevOps": ["Docker", "AWS"]
            }
            mock_score = 75
            mock_recommendations = [
                "Consider adding more industry-specific technical skills."
            ]
            
            print("Attempting to render 'index.html' with mock data...")
            
            # Render the template
            rendered_html = render_template(
                "index.html",
                skills=mock_skills,
                score=mock_score,
                recommendations=mock_recommendations,
                filename="mock_resume.pdf",
                error=None
            )
            
            print("Success! Template rendered without errors.")
            print("-" * 40)
            print("HTML Output Snippet (first 500 characters):")
            print("-" * 40)
            print(rendered_html[:500] + "\n...")
            print("-" * 40)
            
        except Exception as e:
            print(f"Failed to render template: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    test_jinja_rendering()
