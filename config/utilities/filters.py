import django_filters


class StandardFilterSet(django_filters.FilterSet):
    start_date = django_filters.DateFilter(method='filter_start_date')
    end_date = django_filters.DateFilter(method='filter_end_date')

    date_field = 'created_at'  # default

    def filter_start_date(self, queryset, name, value):
        return queryset.filter(**{f'{self.date_field}__gte': value})

    def filter_end_date(self, queryset, name, value):
        return queryset.filter(**{f'{self.date_field}__lte': value})

    class Meta:
        abstract = True