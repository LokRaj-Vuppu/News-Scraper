from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import generic
from django.shortcuts import reverse
from .models import NewsItem, ScrapeHistory
from .forms import ScrapeForm
from .tasks import scrape_async


class ScrapeRecordListView(generic.FormView):
	template_name = 'scrape-history.html'
	form_class = ScrapeForm

	def get_success_url(self):
		return reverse("scrape-history")

	def form_valid(self, form):
		scrape_async.delay()
		return super(ScrapeRecordListView, self).form_valid(form)


	def get_context_data(self, **kwargs):
		context = super(ScrapeRecordListView, self).get_context_data(**kwargs)
		page = self.request.GET.get('page', 1)
		query_set = ScrapeHistory.objects.all()
		paginator = Paginator(query_set, 15)
		try:
			query_set = paginator.page(page)
		except PageNotAnInteger:
			query_set = paginator.page(1)
		except EmptyPage:
			query_set = paginator.page(paginator.num_pages)
		context.update({
			"object_list": query_set
		})
		return context


class NewsItemsListView(generic.ListView):
	model = NewsItem
	template_name = 'news-item-list.html'
	paginate_by = 15


	def get_queryset(self):
		query_set = NewsItem.objects.all()

		title = self.request.GET.get('title', None)

		if title:
			query_set = query_set.filter(title__icontains=title)
			
		return query_set.order_by("-published_date")

	
	def get_context_data(self, **kwargs):
		context = super(NewsItemsListView, self).get_context_data(**kwargs)
		count = NewsItem.objects.all().count()

		context.update({
			"total_count":  count
		})
		return context