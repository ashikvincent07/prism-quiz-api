from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db import transaction

from rest_framework.generics import CreateAPIView, ListCreateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework import status

from lumen.serializers import UserSerializer, ProgrammingLanguageSerializer, QuizSerializer, QuestionSerializer,\
                              ChoiceOwnerSerializer, QuizAttemptSerializer, QuizResponseSerializer
from lumen.models import ProgrammingLanguage, Quiz, Question, Choice, QuizResponse, QuizAttempt
from lumen.permissions import IsOwner, CanModifyQuiz, IsParentQuizUnpublished, IsQuizOwnerOrReadOnly, IsQuestionPublished, \
                              IsChoiceParentQuizUnpublished, IsChoiceQuestionOwner, IsChoiceQuestionOwnerObjectLevel, \
                              IsChoiceParentQuizUnpublishedObjectLevel

                        



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

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        question_id = self.kwargs.get("pk")
        question_object = get_object_or_404(Question, id=question_id)

        context = self.get_serializer_context()
        context['question'] = question_object
        kwargs['context'] = context

        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        question_object = serializer.context.get('question')
        
        if not question_object:
            question_object = get_object_or_404(Question, id=self.kwargs.get("pk"))
            
        serializer.save(question=question_object)
    
    def get_queryset(self):
        return Choice.objects.filter(question_id=self.kwargs.get("pk"))



class ChoiceRetrievUpdateDeleteView(RetrieveUpdateDestroyAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsChoiceQuestionOwnerObjectLevel, IsChoiceParentQuizUnpublishedObjectLevel]

    serializer_class = ChoiceOwnerSerializer

    def get_queryset(self):
        return Choice.objects.all()
    


class QuizAttemptCreateView(CreateAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = QuizAttemptSerializer

    def perform_create(self, serializer):
        id = self.kwargs.get("pk")
        quiz = get_object_or_404(Quiz, id=id)
        return serializer.save(owner=self.request.user, quiz=quiz)
    


class QuizSubmissionView(CreateAPIView):
    serializer_class = QuizResponseSerializer

    def create(self, request, *args, **kwargs):
  
        attempt = get_object_or_404(QuizAttempt, id=self.kwargs.get('pk'))

        if not attempt.quiz.is_published:
            return Response({"error": "This quiz is not active."}, status=status.HTTP_403_FORBIDDEN)

        if attempt.is_completed or attempt.is_expired:
            if not attempt.is_completed:
                attempt.calculate_final_score()
            return Response({"error": "Time is up or quiz already submitted."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        attempt.responses.all().delete()
        
        for item in serializer.validated_data:
            res_obj = QuizResponse.objects.create(
                attempt=attempt,
                question=item['question']
            )
            res_obj.selected_choices.set(item['selected_choices'])

        final_score = attempt.calculate_final_score()

        return Response({
            "message": "Quiz submitted successfully",
            "score": final_score,
            "is_completed": attempt.is_completed
        }, status=status.HTTP_201_CREATED)