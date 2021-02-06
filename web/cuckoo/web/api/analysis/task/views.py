# Copyright (C) 2020 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from cuckoo.common.result import (
    retriever, ResultDoesNotExistError, InvalidResultDataError, Results
)

class Task(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, analysis_id, task_id):
        try:
            task = retriever.get_task(
                analysis_id, task_id, include=[Results.TASK]
            ).task
        except ResultDoesNotExistError:
            return Response(status=404)
        except InvalidResultDataError as e:
            return Response({"error": str(e)}, status=500)

        return Response(task.to_dict())

class Post(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, analysis_id, task_id):
        try:
            post = retriever.get_task(
                analysis_id, task_id, include=[Results.POST]
            ).post
        except ResultDoesNotExistError:
            return Response(status=404)
        except InvalidResultDataError as e:
            return Response({"error": str(e)}, status=500)

        return Response(post.to_dict())

class Machine(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, analysis_id, task_id):
        try:
            machine = retriever.get_task(
                analysis_id, task_id, include=[Results.MACHINE]
            ).machine
        except ResultDoesNotExistError:
            return Response(status=404)
        except InvalidResultDataError as e:
            return Response({"error": str(e)}, status=500)

        return Response(machine.to_dict())

class CompositeRequest(serializers.Serializer):
    retrieve = serializers.ListField(
        allow_empty=False, child=serializers.CharField(),
        help_text="A list of one or more task information types to "
                  "retrieve",
    )

class CompositeTask(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request, analysis_id, task_id):
        serializer = CompositeRequest(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        retrieve = [r.lower() for r in serializer.data["retrieve"]]
        try:
            composite = retriever.get_task(
                analysis_id, task_id, include=retrieve
            )
            composite.load_requested(missing_report_default={})
        except ResultDoesNotExistError:
            return Response(status=404)
        except InvalidResultDataError as e:
            return Response({"error": str(e)}, status=500)

        return Response(composite.to_dict())