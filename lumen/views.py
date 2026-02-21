from django.shortcuts import render

from rest_framework.generics import CreateAPIView, ListCreateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import authentication, permissions

from lumen.serializers import UserSerializer, ProgrammingLanguageSerializer, QuizSerializer
from lumen.models import ProgrammingLanguage, Quiz
from lumen.permissions import IsOwner, IsUnpublishedOrUnpublishing



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
    permission_classes = [permissions.IsAuthenticated, IsOwner, IsUnpublishedOrUnpublishing]

    serializer_class = QuizSerializer

    def get_queryset(self):
        return Quiz.objects.filter(is_active=True)