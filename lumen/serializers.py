from rest_framework import serializers

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



class QuestionSerializer(serializers.ModelSerializer):

    class Meta:

        model = Question
        fields = "__all__"
        read_only_fields = ['quiz']



class ChoiceListSerializer(serializers.ListSerializer):
    
    def validate(self, data):

        question = self.context.get('question')
        
        correct_count = sum(1 for choice in data if choice.get('is_correct') is True)

        if correct_count == 0:
            raise serializers.ValidationError("At least one choice must be marked as correct.")

        if question and question.question_type == 'single' and correct_count > 1:
            raise serializers.ValidationError("Single-choice questions can only have one correct answer.")
        
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

    class Meta:

        model = QuizAttempt
        fields = "__all__"
        read_only_fields = ['owner','quiz']



class QuizResponseSerializer(serializers.ModelSerializer):

    class Meta:

        model = QuizResponse
        fields = "__all__"
        read_only_fields = ['attempt', 'question', 'choice']



