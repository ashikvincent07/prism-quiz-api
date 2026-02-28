# from rest_framework import serializers

# def validate_question_choices(question):

#     choices = question.choices.all()
#     count = choices.all().count()


#     if question.question_type == 'single' and count > 4:
#         raise serializers.ValidationError("Single-choice questions must have only 4 choices.")
    
#     elif question.question_type == 'multiple' and count > 6:
#         raise serializers.ValidationError("Multiple-choice questions must have only 4 - 6 choices.")
