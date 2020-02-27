from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins, generics, status
# from .serializers import DimPointSerializer, MissionSerializer

# from api.models import Mission
# from jobs.tasks import first
from kombu import Connection

import os

class MissionList(APIView):
    def post(self, request, format=None):

        # first.apply_async(args=[request.data], queue='priority_queue', serializer='json')

        return Response("", status=status.HTTP_201_CREATED)
