from rest_framework import serializers

def validate_question_choices(question):
    # Helper to check the state of all choices for a given question.

    choices = question.choices.all()
    correct_count = choices.filter(is_correct=True).count()

    if correct_count == 0:
        raise serializers.ValidationError("This action would leave the question with no correct answer.")

    if question.question_type == 'single' and correct_count > 1:
        raise serializers.ValidationError("Single-choice questions must have exactly one correct answer.")