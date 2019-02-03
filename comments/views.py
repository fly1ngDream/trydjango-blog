from django.views import generic
from django.views.generic.edit import FormMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


from .models import Comment
from .forms import CommentForm


class CommentDetailView(FormMixin, generic.DetailView):
    form_class = CommentForm
    template_name = 'comment_detail.html'
    success_url = '.'

    def get_queryset(self):
        return Comment.objects.filter(id=self.kwargs['pk'], parent=None)

    def get_context_data(self, **kwargs):
        context = super(CommentDetailView, self).get_context_data(**kwargs)
        initial_data = {
            "content_type": self.object.get_content_type,
            "object_id": self.object.pk
        }

        form = CommentForm(self.request.POST or None, initial=initial_data)

        context['comment_form'] = form

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        form = context['comment_form']

        if form.is_valid():
            c_type = form.cleaned_data.get('content_type')
            content_type = ContentType.objects.get(model=c_type)
            obj_id = form.cleaned_data.get('object_id')
            content_data = form.cleaned_data.get('content')
            parent_obj = None

            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None

            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    parent_obj = parent_qs.first()

            new_comment, created = Comment.objects.get_or_create(
                                        user = self.request.user,
                                        content_type = content_type,
                                        object_id = obj_id,
                                        content = content_data,
                                        parent = parent_obj,
                                    )

        return self.form_valid(form)


class CommentDeleteView(generic.DeleteView):
    model = Comment
    template_name = 'comment_delete.html'

    def get_success_url(self, **kwargs):
        obj = self.get_object()
        if obj.parent:
            return reverse_lazy('thread', args=str(obj.parent.pk))
        else:
            return reverse_lazy('post_detail', args=str(obj.content_object.pk))

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
