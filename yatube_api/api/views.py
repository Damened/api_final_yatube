from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters,
                            mixins,
                            pagination,
                            permissions,
                            viewsets)

from .serializers import (FollowSerializer,
                          PostSerializer,
                          GroupSerializer,
                          CommentSerializer)
from .permissions import AuthorIsReadOnly
from posts.models import Group, Post, Follow


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, AuthorIsReadOnly
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('group',)
    pagination_class = pagination.LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [AuthorIsReadOnly]

    def get_post(self):
        return get_object_or_404(
            Post, id=self.kwargs.get('post_id')
        )

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user, post=self.get_post()
        )

    def get_queryset(self):
        return self.get_post().comments.all()


class FollowViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('user', 'following')
    search_fields = ('following__username',)

    def get_queryset(self):
        follows = Follow.objects.select_related(
            'following'
        ).filter(user=self.request.user)
        return follows

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
