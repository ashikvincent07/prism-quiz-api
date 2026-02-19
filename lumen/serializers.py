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

    class Meta:

        model = ProgrammingLanguage
        fields = "__all__"
        


class QuizSerializer(serializers.ModelSerializer):

    class Meta:

        model = Quiz
        fields = "__all__"
        read_only_fields = ['programming_language', 'created_by']



class QuestionSerializer(serializers.ModelSerializer):

    class Meta:

        model = Question
        fields = "__all__"
        read_only_fields = ['quiz']



class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:

        model = Choice
        fields = "__all__"
        read_only_fields = ['question']



class QuizAttemptSerializer(serializers.ModelSerializer):

    class Meta:

        model = QuizAttempt
        fields = "__all__"
        read_only_fields = ['user','quiz']



class QuizResponseSerializer(serializers.ModelSerializer):

    class Meta:

        model = QuizResponse
        fields = "__all__"
        read_only_fields = ['attempt', 'question', 'choice']



