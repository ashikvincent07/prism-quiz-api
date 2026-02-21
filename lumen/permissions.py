from rest_framework import permissions


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner
    

from rest_framework import permissions

class IsUnpublishedOrUnpublishing(permissions.BasePermission):

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
    