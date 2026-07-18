from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from apps.identity.models import User


class ConversationViewSet(viewsets.ModelViewSet):
    """
    GET /conversations/           — list YOUR OWN conversations only
    POST /conversations/          — start a new conversation with another user
    GET /conversations/{id}/messages/    — list messages in this conversation
    POST /conversations/{id}/send/       — send a message
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user).prefetch_related('participants', 'messages')

    def create(self, request, *args, **kwargs):
        """
        POST body: {"participant_id": <other user's id>}
        Reuses an existing conversation between these two users if one
        already exists, instead of creating duplicates every time.
        """
        other_user_id = request.data.get('participant_id')
        if not other_user_id:
            return Response({'detail': 'participant_id is required.'}, status=400)

        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)

        existing = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
        if existing:
            return Response(ConversationSerializer(existing, context={'request': request}).data)

        conversation = Conversation.objects.create()
        conversation.participants.set([request.user, other_user])
        return Response(ConversationSerializer(conversation, context={'request': request}).data, status=201)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.select_related('sender').all()
        return Response(MessageSerializer(messages, many=True).data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        conversation = self.get_object()
        body = request.data.get('body')
        if not body:
            return Response({'detail': 'body is required.'}, status=400)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            body=body,
        )
        return Response(MessageSerializer(message).data, status=201)