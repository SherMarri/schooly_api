import datetime
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from common.permissions import IsAdmin
from finances import serializers, models


class ExpenseItemViewSet(ModelViewSet):
    permission_classes = (IsAdmin,)
    serializer_class = serializers.ExpenseItemSerializer

    def get_queryset(self):
        """
        Needs to be refined
        :return: Queryset with expense items
        """
        return models.ExpenseItem.objects.all().order_by('-date')

    @action(detail=False)
    def today(self, request):
        queryset = self.get_queryset().filter(date=datetime.date.today())
        serializer = self.get_serializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ExpenseCategoryViewSet(ModelViewSet):
    permission_classes = (IsAdmin,)
    serializer_class = serializers.ExpenseCategorySerializer
    queryset = models.ExpenseCategory.objects.all()


class IncomeItemViewSet(ModelViewSet):
    permission_classes = (IsAdmin,)
    serializer_class = serializers.IncomeItemSerializer

    def get_queryset(self):
        """
        Needs to be refined
        :return: Queryset with income items
        """
        return models.IncomeItem.objects.all().order_by('-date')

    @action(detail=False)
    def today(self, request):
        # queryset = self.get_queryset().filter(date=datetime.date.today())
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class IncomeCategoryViewSet(ModelViewSet):
    permission_classes = (IsAdmin,)
    serializer_class = serializers.IncomeCategorySerializer
    queryset = models.IncomeCategory.objects.all()


class FeeStructureViewSet(ModelViewSet):
    permission_classes = (IsAdmin,)
    serializer_class = serializers.FeeStructureSerializer
    queryset = models.FeeStructure.objects.all()


class ChallanViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = (IsAdmin,)
    queryset = models.FeeChallan.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = serializers.CreateChallanSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED,
                        data=serializer.errors)
