from datetime import date, timedelta, datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import F, Q, Avg, Sum, Max, Min, Count
from common.permissions import IsAdmin, IsAccountant
from finances import serializers, models
from django.core.paginator import Paginator
import json
from common.models import Config
from django.http import HttpResponse
import os
import csv
from django.conf import LazySettings

settings = LazySettings()


class TransactionViewSet(CreateModelMixin, GenericViewSet):
    permission_classes = [IsAdmin | IsAccountant]
    serializer_class = serializers.TransactionSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_type = kwargs.get('transaction_type', None)

    # def get_permissions(self):
    #     if self.action in ['create']:
    #         permission_classes = [IsAdmin | IsAccountant]
    #     else:
    #         permission_classes = [IsAdmin]
    #     return [permission_class() for permission_class in permission_classes]


    def get_queryset(self):
        """
        Needs to be refined
        :return: Queryset with expense items
        """
        return models.Transaction.objects.filter(
            transaction_type=self.transaction_type
        ).select_related('category').order_by('-date')

    @action(detail=False)
    def today(self, request):
        queryset = self.get_queryset().filter(date=date.today()).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def create(self, request):
        context = {
            'user': request.user,
            'transaction_type': self.transaction_type
        }
        result = self.create_transaction(request.data, context)
        if result['success']:
            return Response(
                status=status.HTTP_200_OK,
                data=result['data']
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=results['errors']
            )

    @staticmethod
    def create_transaction(data, context):
        default_account = models.Account.objects.filter(is_default=True).first()
        data = data.copy()
        data['account'] = default_account.id
        data['transaction_type'] = context['transaction_type']
        serializer = TransactionViewSet.serializer_class(data=data, context=context)
        if not serializer.is_valid():
            return {
                'success': False,
                'errors': serializer.errors
            }

        serializer.save()
        return {
            'success': True,
            'data': serializer.data
        }


class ExpenseItemViewSet(TransactionViewSet):

    def __init__(self, **kwargs):
        kwargs['transaction_type'] = models.CREDIT
        super().__init__(**kwargs)


class IncomeItemViewSet(TransactionViewSet):

    def __init__(self, **kwargs):
        kwargs['transaction_type'] = models.DEBIT
        super().__init__(**kwargs)


class TransactionSummaryAPIView(APIView):
    permission_classes = [IsAdmin]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_type = kwargs.get('transaction_type', None)

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
        today = date.today()
        year = today.year
        month = today.month

        # 1, 5
        yearly_aggregates = models.Transaction.objects.filter(
            date__year=year,
            transaction_type=self.transaction_type
        ).aggregate(
            total=Sum('amount'), average=Avg('amount')
        )
        results['yearly_total'] = yearly_aggregates['total']
        results['average_item'] = yearly_aggregates['average']

        # 2, 3, 4, 6
        category_aggregates = models.TransactionCategory.objects.filter(
            category_type=self.transaction_type
        ).annotate(
            total_transactions=Count('transactions', filter=Q(transactions__date__year=year)),
            yearly_amount=Sum('transactions__amount', filter=Q(transactions__date__year=year)),
            monthly_amount=Sum('transactions__amount', filter=Q(transactions__date__month=month, transactions__date__year=year))
        ).filter(total_transactions__gt=0)

        results['category_wise_data'] = [{
            'name': c.name,
            'item_count': c.total_transactions,
            'yearly_total': c.yearly_amount if c.yearly_amount else 0,
            'monthly_total': c.monthly_amount if c.monthly_amount else 0,
        } for c in category_aggregates]

        # 7
        current_month_items = models.Transaction.objects.filter(
            transaction_type=self.transaction_type,
            date__year=year, date__month=month
        )

        monthly_total = 0
        daily_total = {day: 0 for day in range(1, today.day + 1)}
        for item in current_month_items:
            daily_total[item.date.day] += item.amount
            monthly_total += item.amount
        results['monthly_total'] = monthly_total
        results['daily_total'] = daily_total
        return Response(status=status.HTTP_200_OK, data=results)


class ExpenseSummaryAPIView(TransactionSummaryAPIView):
    def __init__(self, **kwargs):
        kwargs['transaction_type'] = models.CREDIT
        super().__init__(**kwargs)


class IncomeSummaryAPIView(TransactionSummaryAPIView):
    def __init__(self, **kwargs):
        kwargs['transaction_type'] = models.DEBIT
        super().__init__(**kwargs)


class TransactionDetailsAPIView(APIView):
    permission_classes = [IsAdmin]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transaction_type = kwargs.get('transaction_type', None)

    def get(self, request):
        """
        Returns following information:
        1. Paginated transaction items falling in the search criteria
        2. Category-wise transactions if category is 'none' or 'all'
        """
        params = request.query_params

        filter_serializer = serializers.ItemFilterSerializer(data=params)
        if not filter_serializer.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=filter_serializer.errors
            )

        date_range = (
            filter_serializer.validated_data['start_date'],
            filter_serializer.validated_data['end_date'] + timedelta(days=1)
        )
        queryset = models.Transaction.objects.filter(
            date__range=date_range
        ).select_related('category')
        if self.transaction_type:
            queryset = queryset.filter(transaction_type=self.transaction_type)
        results = {}
        if 'category_id' in filter_serializer.validated_data and \
                filter_serializer.validated_data['category_id'] != -1:
            category_id = filter_serializer.validated_data['category_id']
            queryset = queryset.filter(category_id=category_id)

        queryset = queryset.order_by('-date')
        if 'download' in params and params['download'] == 'true':
            return self.get_downloadable_link(queryset, self.transaction_type)
        elif 'page' not in params:  # Send category wise data as well
            category_aggregates = models.TransactionCategory.objects.filter(
                category_type=self.transaction_type
            ).annotate(
                total_amount=Sum(
                    'transactions__amount',
                    filter=Q(transactions__date__range=date_range)
                )
            ).filter(total_amount__gt=0)
            category_wise_data = [{
                'id': c.id,
                'name': c.name,
                'total_amount': c.total_amount if c.total_amount else 0
            } for c in category_aggregates]
            results['category_wise_data'] = category_wise_data

        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)
            aggregate_queryset = models.TransactionCategory.objects.filter(
                category_type=self.transaction_type,
                transactions__date__range=date_range
            )
            if 'category_id' in filter_serializer.validated_data and \
                    filter_serializer.validated_data['category_id'] != -1:
                category_id = filter_serializer.validated_data['category_id']
                aggregate_queryset = aggregate_queryset.filter(id=category_id)

            yearly_aggregates = aggregate_queryset.aggregate(
                total=Sum('transactions__amount')
            )
            results['sum'] = yearly_aggregates['total']

        serializer = serializers.TransactionSerializer(page, many=True)
        results['data'] = serializer.data
        results['page'] = page.number
        results['count'] = paginator.count
        return Response(status=status.HTTP_200_OK, data=results)

    @staticmethod
    def get_downloadable_link(queryset, transaction_type):
        timestamp = datetime.now().strftime("%f")
        report_type = 'income' if transaction_type == 1 else 'expenses'
        file_name = f'{report_type}_{timestamp}.csv'
        with open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'), mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([
                'Title', 'Category', 'Amount', 'Date',
            ])
            for income_record in queryset:
                writer.writerow(TransactionDetailsAPIView.get_csv_row(income_record))
        return Response(file_name, status=status.HTTP_200_OK)

    @staticmethod
    def get_csv_row(income_record):
        row = [income_record.title, income_record.category.name, income_record.amount, income_record.date.strftime('%Y-%m-%d')]
        return row


class ExpenseDetailsAPIView(TransactionDetailsAPIView):
    def __init__(self, **kwargs):
        kwargs['transaction_type'] = models.CREDIT
        super().__init__(**kwargs)


class IncomeDetailsAPIView(TransactionDetailsAPIView):
    def __init__(self, **kwargs):
        kwargs['transaction_type'] = models.DEBIT
        super().__init__(**kwargs)


class ExpenseCategoryViewSet(ModelViewSet):
    permission_classes = [IsAdmin | IsAccountant]
    serializer_class = serializers.TransactionCategorySerializer
    queryset = models.TransactionCategory.objects.filter(
        category_type=models.CREDIT, is_active=True
    )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IncomeCategoryViewSet(ModelViewSet):
    permission_classes = [IsAdmin | IsAccountant]
    serializer_class = serializers.TransactionCategorySerializer
    queryset = models.TransactionCategory.objects.filter(
        category_type=models.DEBIT, is_active=True
    )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeeStructureViewSet(ModelViewSet):
    permission_classes = [IsAdmin | IsAccountant]
    serializer_class = serializers.FeeStructureSerializer
    queryset = models.FeeStructure.objects.all()


class ChallanViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    permission_classes = [IsAdmin | IsAccountant]
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
        queryset = self.apply_filters(queryset, params).order_by('-created_at')
        if 'download' in params and params['download'] == 'true':
            return self.get_downloadable_link(queryset)

        paginator = Paginator(queryset, 20)
        if 'page' in params:
            page = paginator.page(int(params['page']))
        else:
            page = paginator.page(1)

        serializer = serializers.FeeChallanSerializer(page, many=True)
        return Response(status=status.HTTP_200_OK, data={'data': serializer.data, 'page': page.number, 'count': paginator.count, })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.paid + instance.discount > 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @staticmethod
    def get_downloadable_link(queryset):
        timestamp = datetime.now().strftime("%f")
        file_name = f'fees_{timestamp}.csv'
        with open(os.path.join(settings.BASE_DIR, f'downloadables/{file_name}'), mode='w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow([
                'Invoice #', 'GR #', 'Name', 'Section', 'Fee (Rs.)', 'Paid (Rs.)', 'Discount (Rs.)', 'Due Date', 'Status',
            ])
            for challan in queryset:
                writer.writerow(ChallanViewSet.get_csv_row(challan))
        return Response(file_name, status=status.HTTP_200_OK)

    @staticmethod
    def get_csv_row(challan):
        if challan.paid:
            if challan.discount:
                status = 'Paid' if challan.paid + challan.discount >= challan.total else 'Unpaid'
            else:
                status = 'Paid' if challan.paid >= challan.total else 'Unpaid'
        else:
            status = 'Unpaid'

        return [
            challan.id,
            challan.student.profile.student_info.gr_number,
            challan.student.profile.fullname,
            f'{challan.student.profile.student_info.section.grade.name} - {challan.student.profile.student_info.section.name}',
            f'{challan.total:,}',
            f'{challan.paid:,}',
            f'{challan.discount:,}',
            challan.due_date,
            status,
        ]

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        challan = self.get_object()
        data = request.data
        serializer = serializers.FeeChallanPaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        challan.paid = challan.paid + data['paid']
        challan.late_fee = challan.late_fee + data['late_fee']
        challan.discount = serializer.validated_data['discount']
        challan.paid_at = serializer.validated_data['payment_date']
        challan.save()
        self.add_to_transactions(challan, data['paid'])
        serializer = serializers.FeeChallanSerializer(instance=challan)
        return Response(
            status=status.HTTP_200_OK,
            data=serializer.data
        )

    def add_to_transactions(self, challan, amount):
        fees_category_id = Config.objects.filter(
            name='FEES_CATEGORY_ID'
        ).first().value
        data = {
            'title': 'Invoice #: {0}'.format(challan.id),
            'category_id': fees_category_id,
            'amount': amount,
        }
        context = {
            'user': self.request.user,
            'transaction_type': models.DEBIT,
        }
        results = TransactionViewSet.create_transaction(data, context)
        # TODO rollback payment incase of failure

    def apply_filters(self, queryset, params):
        if 'from' in params:
            queryset = queryset.filter(due_date__gte=params['from'])

        if 'to' in params:
            queryset = queryset.filter(due_date__lte=params['to'])

        if 'target_type' in params and 'target_value' in params:
            target_value = json.loads(params['target_value'])
            if target_value['grade_id'] != -1:  # If grade selected
                if target_value['section_id'] not in [-1, None]:  # If section selected
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
                    paid__gte=F('total') - F('discount')
                )
            if params['status'] == 'unpaid':
                queryset = queryset.filter(
                    Q(total__gt=F('paid') + F('discount')) | Q(paid__isnull=True),
                )

        if 'search_term' in params and params['search_term'] != '':
            q = params['search_term']
            queryset = queryset.filter(
                Q(student__profile__student_info__gr_number__icontains=q) |
                Q(student__profile__fullname__icontains=q),
            )

        return queryset

