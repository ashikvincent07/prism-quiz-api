from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.generics import CreateAPIView, ListCreateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import authentication, permissions

from lumen.serializers import UserSerializer, ProgrammingLanguageSerializer, QuizSerializer, QuestionSerializer, ChoiceSerializer, \
                              ChoiceOwnerSerializer
from lumen.models import ProgrammingLanguage, Quiz, Question, Choice
from lumen.permissions import IsOwner, CanModifyQuiz, IsParentQuizUnpublished, IsQuizOwnerOrReadOnly, IsQuestionPublished, \
                              IsChoiceParentQuizUnpublished, IsChoiceQuestionOwner, IsChoiceQuestionOwnerObjectLevel, \
                              IsChoiceParentQuizUnpublishedObjectLevel
from lumen.utility_functions import validate_question_choices
                        



class UserRegisterView(CreateAPIView):

    permission_classes = [permissions.AllowAny]

    serializer_class = UserSerializer



class ProgrammingLanguageCreateListView(ListCreateAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = ProgrammingLanguageSerializer

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        return ProgrammingLanguage.objects.all()



class ProgrammingLanguageDeleteView(DestroyAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    serializer_class = ProgrammingLanguageSerializer

    def get_queryset(self):
        return ProgrammingLanguage.objects.all()
    


class QuizCreateListView(ListCreateAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = QuizSerializer

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Quiz.objects.filter(is_active=True)

    

class QuizRetrievUpdateDeleteView(RetrieveUpdateDestroyAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwner, CanModifyQuiz]

    serializer_class = QuizSerializer

    def get_queryset(self):
        return Quiz.objects.filter(is_active=True)
    


class QuestionCreateListView(ListCreateAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwner, IsParentQuizUnpublished]

    serializer_class = QuestionSerializer

    def perform_create(self, serializer):

        id = self.kwargs.get("pk")

        quiz_object = get_object_or_404(Quiz, id=id)

        return serializer.save(quiz=quiz_object)
    
    def get_queryset(self):
        return Question.objects.all()
    


class QuestionRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsQuizOwnerOrReadOnly, IsQuestionPublished]

    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.all()
    


class ChoiceCreateListView(ListCreateAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsChoiceQuestionOwner, IsChoiceParentQuizUnpublished]

    serializer_class = ChoiceOwnerSerializer

    def perform_create(self, serializer):

        id = self.kwargs.get("pk")

        question_object = get_object_or_404(Question, id=id)

        return serializer.save(question=question_object)
    
    
    
    def get_serializer(self, *args, **kwargs):

        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)
    
    def get_queryset(self):
        return Choice.objects.all()



class ChoiceRetrievUpdateDeleteView(RetrieveUpdateDestroyAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsChoiceQuestionOwnerObjectLevel, IsChoiceParentQuizUnpublishedObjectLevel]

    serializer_class = ChoiceOwnerSerializer

    def get_queryset(self):
        return Choice.objects.all()
    

    def perform_update(self, serializer):
        with transaction.atomic():
            instance = serializer.save()
            validate_question_choices(instance.question)

    def perform_destroy(self, instance):
        question = instance.question
        with transaction.atomic():
            instance.delete()
            validate_question_choices(question)