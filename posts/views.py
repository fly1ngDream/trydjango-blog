from urllib.parse import quote_plus

from django.views import generic
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin


from comments.models import Comment


from .models import Post
from .forms import PostForm
from comments.forms import CommentForm


class PostListView(generic.ListView):
    model = Post
    template_name = 'posts_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        if query:
            context['object_list'] = Post.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__username__icontains=query)
            ).distinct()
        else:
            context['object_list'] = Post.objects.all()
        return context


class PostDetailView(FormMixin, generic.DetailView):
    model = Post
    form_class = CommentForm
    template_name = 'post_detail.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['share_string'] = quote_plus(self.object.content)

        comments = self.object.comments
        context['comments'] = comments
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


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = PostForm
    template_name = 'post_create.html'
    login_url = 'login'

    # def dispatch(self, request, *args, **kwargs):
    #     if not self.request.user.is_staff or not self.request.user.is_superuser:
    #         raise PermissionDenied
    #     return super().dispatch(request, *args, **kwargs)



class PostUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = PostForm
    model = Post
    # fields = ('title', 'content', 'image')
    template_name = 'post_update.html'
    login_url = 'login'

    # def dispatch(self, request, *args, **kwargs):
    #     if not self.request.user.is_staff or not self.request.user.is_superuser:
    #         raise PermissionDenied
    #     return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    login_url = 'login'

    # def dispatch(self, request, *args, **kwargs):
    #     if not self.request.user.is_staff or not self.request.user.is_superuser:
    #         raise PermissionDenied
    #     return super().dispatch(request, *args, **kwargs)
