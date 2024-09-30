from django.contrib import admin
from IMDB.models import *
from IMDB.forms import *
from IMDB.modelTraining.modelTraining import *
from collections import Counter

class DatasetEntryInline(admin.TabularInline):
    model = DatasetEntry
    extra = 0

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    inlines = [DatasetEntryInline]
    list_display = ['name', 'file']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.file:
            Dataset.process_csv_data(obj.pk) 

@admin.register(DatasetEntry)
class DatasetEntryAdmin(admin.ModelAdmin):
    list_display = ['review', 'sentiment', 'dataset']
    list_filter = ['dataset']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['dataset'].queryset = Dataset.objects.all()
        return form


    def change_view(self, request, object_id, form_url='', extra_context=None):
        if 'dataset' in request.GET:
            selected_dataset_id = int(request.GET['dataset'])
            queryset = DatasetEntry.objects.filter(dataset_id=selected_dataset_id)
            self.queryset = queryset

        return super().change_view(request, object_id, form_url, extra_context)

    def train_model_action(self, request, queryset):
        all_reviews = ' '.join(queryset.values_list('review', flat=True))
        all_sentiments = ' '.join(queryset.values_list('sentiment', flat=True))
        word_counter = Counter(all_reviews.split())
        common_words = [word for word, _ in word_counter.most_common(5000)]
        filtered_reviews = []
        for entry in queryset:
            filtered_review = ' '.join([word for word in entry.review.split() if word in common_words])
            filtered_reviews.append(filtered_review)

        start_model(filtered_reviews, all_sentiments)
        self.message_user(request, "Model trained successfully!")

    train_model_action.short_description = "Train Model"

    actions = ['train_model_action']

admin.site.register(FilmReview)
admin.site.register(Actor)
admin.site.register(Film)
admin.site.register(Producers)
admin.site.register(ExtendedUser)
admin.site.site_title = "MadaDB Administration"
admin.site.site_header = "MadaDB Administration"