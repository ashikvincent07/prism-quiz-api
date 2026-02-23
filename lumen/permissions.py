from rest_framework import permissions

from django.shortcuts import get_object_or_404

from lumen.models import Quiz, Question, Choice


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj.owner
    


class CanModifyQuiz(permissions.BasePermission):

    message = "Published quizzes cannot be edited or deleted. You must unpublish the quiz first by setting 'is_published' to false via a PATCH request."

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if not obj.is_published:
            return True

        if request.method == 'PATCH':
           
            data = request.data
            is_switching_off = data.get('is_published') is False
            
           
            only_status_change = len(data.keys()) == 1 and 'is_published' in data
            
            if is_switching_off and only_status_change:
                return True

        return False



class IsParentQuizUnpublished(permissions.BasePermission):
    message = "Cannot add questions to a published quiz. Please unpublish the quiz first."

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True
   
        quiz_id = view.kwargs.get('pk')
        if not quiz_id:
            return False
        
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        return not quiz.is_published
    


class IsQuizOwnerOrReadOnly(permissions.BasePermission):

    message = "Only owner can make changes."

    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        quiz = obj.quiz
        
        return quiz.owner == request.user
    

    
class IsQuestionPublished(permissions.BasePermission):

    message = "You can't modify questions, quiz already published."

    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        quiz = obj.quiz

        return not quiz.is_published
    


class IsChoiceQuestionOwner(permissions.BasePermission):

    message = "only owner can add choices"

    def has_permission(self, request, view):
        
        question_id = view.kwargs.get("pk")
        if not question_id:
            return False
        
        question = get_object_or_404(Question, id=question_id)

        quiz = question.quiz

        return request.user == quiz.owner
          


class IsChoiceParentQuizUnpublished(permissions.BasePermission):

    message = "Cannot add choices to a published quiz. Please unpublish the quiz first."

    def has_permission(self, request, view):

        question_id = view.kwargs.get("pk")
        if not question_id:
            return False
        
        question = get_object_or_404(Question, id=question_id)

        quiz = question.quiz

        return not quiz.is_published

        

class IsChoiceQuestionOwnerObjectLevel(permissions.BasePermission):

    message = "Only owner can make changes."

    def has_object_permission(self, request, view, obj):
        
        choice_id = view.kwargs.get("pk")

        choice = get_object_or_404(Choice, id=choice_id)

        question = choice.question

        quiz = question.quiz

        return request.user == quiz.owner


        
class IsChoiceParentQuizUnpublishedObjectLevel(permissions.BasePermission):

    message = "Can't make changes to published quiz"

    def has_object_permission(self, request, view, obj):
        
        choice_id = view.kwargs.get("pk")

        choice = get_object_or_404(Choice, id=choice_id)

        question = choice.question

        quiz = question.quiz

        return not quiz.is_published