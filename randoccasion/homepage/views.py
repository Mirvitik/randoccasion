from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'homepage/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context