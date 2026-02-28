from rest_framework import serializers

from django.utils import timezone

from lumen.models import User, ProgrammingLanguage, Quiz, Question, Choice, QuizAttempt, QuizResponse



class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ['username', 'password', 'email', 'phone']
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    


class ProgrammingLanguageSerializer(serializers.ModelSerializer):

    owner = serializers.StringRelatedField()

    class Meta:

        model = ProgrammingLanguage
        fields = "__all__"
        read_only_fields = ['owner']

        

class QuizSerializer(serializers.ModelSerializer):

    class Meta:

        model = Quiz
        fields = "__all__"
        read_only_fields = ['owner']
    
    programming_language = serializers.PrimaryKeyRelatedField(
        queryset=ProgrammingLanguage.objects.all()
    )


    def validate(self, data):
        
        if data.get('is_published') is True:
            
            if not self.instance:
                raise serializers.ValidationError("Add questions before trying to publish.")

            questions = self.instance.questions.all()
            
            if questions.count() < 5:
                raise serializers.ValidationError("A quiz must have at least 5 questions to be published.")

            for q in questions:
 
                choices = q.choices.all()
                choice_count = choices.count()
                correct_count = choices.filter(is_correct=True).count()

                if q.question_type == 'single':
                    if choice_count != 4:
                        raise serializers.ValidationError(f"Question '{q.text}' must have exactly 4 choices.")
                    if correct_count != 1:
                        raise serializers.ValidationError(f"Question '{q.text}' must have exactly one correct answer.")

                elif q.question_type == 'multiple':
             
                    if not (4 <= choice_count <= 6):
                        raise serializers.ValidationError(f"Question '{q.text}' must have between 4 and 6 choices.")
                    if correct_count < 1:
                        raise serializers.ValidationError(f"Question '{q.text}' must have at least one correct answer.")

        return data



class QuestionSerializer(serializers.ModelSerializer):

    class Meta:

        model = Question
        fields = "__all__"
        read_only_fields = ['quiz']



class ChoiceListSerializer(serializers.ListSerializer):
    
    def validate(self, data):
        question = self.context.get('question')

        if question:
        
            incoming_choices_count = len(data)
            
            existing_choices_count = question.choices.count()
            
            total_count = existing_choices_count + incoming_choices_count
            q_type = question.question_type

            if q_type == 'single':
                if total_count > 4:
                    raise serializers.ValidationError(
                        f"Single-choice questions cannot have more than 4 choices. "
                        f"Current: {existing_choices_count}, New: {incoming_choices_count}."
                    )
            
            elif q_type == 'multiple':
                if total_count > 6:
                    raise serializers.ValidationError(
                        f"Multiple-choice questions cannot have more than 6 choices. "
                        f"Current: {existing_choices_count}, New: {incoming_choices_count}."
                    )
        
        return data



class ChoiceOwnerSerializer(serializers.ModelSerializer):

    class Meta:

        model = Choice
        fields = "__all__"
        list_serializer_class = ChoiceListSerializer
        read_only_fields = ['question']



class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:

        model = Choice
        fields = "__all__"
        read_only_fields = ['question']
        extra_kwargs = {'is_correct':{'write_only':True}}



class QuizAttemptSerializer(serializers.ModelSerializer):

    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = QuizAttempt
        fields = "__all__"
        read_only_fields = ['owner', 'quiz', 'score', 'start_time', 'end_time', 'is_completed']

    def validate(self, attrs):
        instance = self.instance 
        
        if not instance:
            return attrs

        if not instance.quiz.is_published:
            raise serializers.ValidationError("This quiz is not currently active.")

        if instance.is_completed:
            raise serializers.ValidationError("This attempt is already completed.")

        if instance.is_expired:

            instance.calculate_final_score() 
            raise serializers.ValidationError("Time's up! Your attempt has been closed.")

        return attrs



class QuizResponseSerializer(serializers.ModelSerializer):
    
    selected_choices = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Choice.objects.all()
    )

    class Meta:
        model = QuizResponse
        fields = ['question', 'selected_choices']

    def validate(self, data):
        question = data['question']
        choices = data['selected_choices']

        for choice in choices:
            if choice.question != question:
                raise serializers.ValidationError(
                    f"Choice '{choice.text}' does not belong to question '{question.id}'."
                )
        return data



