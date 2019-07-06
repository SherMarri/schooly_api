import datetime
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from common.permissions import IsAdmin
from finances import serializers, models
from django.core.paginator import Paginator


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


class ChallanViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = (IsAdmin,)
    queryset = models.FeeChallan.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = serializers.CreateChallanSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)
        
    def list(self, request):
        params = request.query_params
        queryset = self.get_queryset().select_related('student__profile')
        queryset = self.apply_filters(queryset, params)
        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
        
        serializer = serializers.FeeChallanSerializer(page, many=True)
        return Response(status=status.HTTP_200_OK,
            data= {
                'data': serializer.data,
                'page': page.number,
                'count': paginator.count,
            }
        )

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        challan = self.get_object()
        data = request.data
        serializer = serializers.FeeChallanPaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        challan.paid = challan.paid + data['paid'] if challan.paid else data['paid']
        challan.discount = challan.discount
        challan.paid_at = datetime.datetime.now()
        challan.save()
        serializer = serializers.FeeChallanSerializer(instance=challan)
        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data
        )

    def apply_filters(self, queryset, params):
        if 'from' in params:
            queryset = queryset.filter(due_date__gte=params['from'])

        if 'to' in params:
            queryset = queryset.filter(due_date__lte=params['to'])

        return queryset
