import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import F, Q, Avg, Sum, Max, Min, Count
from common.permissions import IsAdmin
from finances import serializers, models
from django.core.paginator import Paginator
import json


class ExpenseItemViewSet(ModelViewSet):
    permission_classes = (IsAdmin,)
    serializer_class = serializers.ExpenseItemSerializer

    def get_queryset(self):
        """
        Needs to be refined
        :return: Queryset with expense items
        """
        return models.ExpenseItem.objects.filter(is_active=True).order_by('-date')

    @action(detail=False)
    def today(self, request):
        queryset = self.get_queryset().filter(date=datetime.date.today())
        serializer = self.get_serializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ExpenseSummaryAPIView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        """
        Returns following statistics:
        1. Total expenses in current year -
        2. Total expenses in current month -
        3. Most popular category (item-wise) -
        4. Most expensive category -
        5. Average expense item -
        6. Data points for amount spent in each category (monthly, yearly) -
        7. Data points for amount spent every day in current month -
        """

        results = {}
        today = datetime.date.today()
        year = today.year
        month = today.month

        # 1, 5
        yearly_aggregates = models.ExpenseItem.objects.filter(
            date__year=year
        ).aggregate(
            total=Sum('amount'), average=Avg('amount')
        )
        results['yearly_total'] = yearly_aggregates['total']
        results['average_item'] = yearly_aggregates['average']

        # 2, 3, 4, 6
        category_aggregates = models.ExpenseCategory.objects.filter(
            is_active=True
        ).annotate(
            total_items=Count('items', filter=Q(items__date__year=year)),
            yearly_amount=Sum('items__amount', filter=Q(items__date__year=year)),
            monthly_amount=Sum('items__amount',
                filter=Q(items__date__month=month, items__date__year=year)
            )
        )

        results['category_wise_data'] = [{
            'name': c.name,
            'item_count': c.total_items,
            'yearly_total': c.yearly_amount,
            'monthly_total': c.monthly_amount
        } for c in category_aggregates]

        # 7
        current_month_items = models.ExpenseItem.objects.filter(
            date__lte=today, date__year=year, date__month=month
        )
        
        monthly_total = 0
        daily_total = {day: 0 for day in range(1,today.day+1)}
        for item in current_month_items:
            daily_total[item.date.day] += item.amount
            monthly_total += item.amount
        results['monthly_total'] = monthly_total
        results['daily_total'] = daily_total 
        return Response(status=status.HTTP_200_OK, data=results)
    

class ExpenseDetailsAPIView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        """
        Returns following information:
        1. Paginated expense items falling in the search criteria
        2. Category-wise expenses if category is 'none' or 'all'
        """
        params = request.query_params

        filter_serializer = serializers.ItemFilterSerializer(data=params)
        if not filter_serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=filter_serializer.errors
            )

        date_range = (filter_serializer.validated_data['start_date'],
            filter_serializer.validated_data['end_date'],
        )
        queryset = models.ExpenseItem.objects.filter(date__range=date_range)
        results = {}
        if 'category_id' in filter_serializer.validated_data and \
            filter_serializer.validated_data['category_id'] != -1:
            category_id = filter_serializer.validated_data['category_id']
            queryset = queryset.filter(category_id=category_id)
        elif 'page' not in params:  # Send category wise data as well
            category_aggregates = models.ExpenseCategory.objects.filter(
                is_active=True
            ).annotate(
                total_amount=Sum('items__amount', filter=Q(items__date__range=date_range))
            )
            category_wise_data = [{
                'id':  c.id,
                'name': c.name,
                'total_amount': c.total_amount
            } for c in category_aggregates]
            results['category_wise_data'] = category_wise_data

        queryset = queryset.select_related('category')
        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
            aggregate_queryset = models.ExpenseItem.objects.filter(
                date__range=date_range
            )
            if 'category_id' in filter_serializer.validated_data and \
                filter_serializer.validated_data['category_id'] != -1:
                category_id = filter_serializer.validated_data['category_id']
                aggregate_queryset = aggregate_queryset.filter(category_id=category_id)
            
            yearly_aggregates = aggregate_queryset.aggregate(total=Sum('amount'))
            results['sum'] = yearly_aggregates['total']
        
        serializer = serializers.ExpenseItemSerializer(page, many=True)
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK,
            data=results 
        )


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
        queryset = self.get_queryset().select_related(
            'student__profile__student_info__section__grade'
            )
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

        if 'target_type' in params and 'target_value' in params:
            target_value = json.loads(params['target_value'])
            if target_value['grade_id'] != '-1':  # If grade selected
                if target_value['section_id'] != '-1':  # If section selected
                    queryset = queryset.filter(
                        student__profile__student_info__section_id=target_value['section_id']
                    )
                else:
                    queryset = queryset.filter(
                        student__profile__student_info__section__grade_id=target_value['grade_id']
                    )
        
        if 'status' in params and params['status'] != 'all':
            if params['status'] == 'paid':
                queryset = queryset.filter(
                    total = F('paid') + F('discount') 
                )
            if params['status'] == 'unpaid':
                queryset = queryset.filter(
                    Q(total__gt = F('paid') + F('discount')) | Q(paid__isnull=True),
                )

        return queryset
