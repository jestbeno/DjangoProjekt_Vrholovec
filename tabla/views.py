from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import Http404
from django.db.models import Count

from .forms import NewIdejaForm, PostForm
from .models import Tabla,Ideja,Post

def index(request):
    return render(request,'index.html')

def home(request):
    tabla = Tabla.objects.all()
    return render(request, 'home.html', {'tabla': tabla})

#HOME PAGE z uporabo GCBV - Generic view
class TablaListView(ListView):
    model = Tabla
    context_object_name = 'tabla'
    template_name = 'home.html'
# osnovna
def IdejeNaTabli1(request, pk):
    tabla = get_object_or_404(Tabla, pk=pk)
    ideje = tabla.ideje.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'idejenatabeli.html', {'tabla': tabla, 'ideje': ideje})

def IdejeNaTabli21(request, pk):
    tabla = get_object_or_404(Tabla, pk=pk)
    queryset = tabla.ideje.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 10) #prikaže 10 elementov na stran!

    try:
        ideje = paginator.page(page)
    except PageNotAnInteger:
        # poslji na prvo stran
        ideje = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        ideje = paginator.page(paginator.num_pages)

    return render(request, 'idejenatabeli.html', {'tabla': tabla, 'ideje': ideje})

class IdejeNaTabli(ListView):
    model = Ideja
    context_object_name = 'ideje'
    template_name = 'idejenatabeli.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['tabla'] = self.tabla
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.tabla = get_object_or_404(Tabla, pk=self.kwargs.get('pk'))
        queryset = self.tabla.ideje.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

@login_required
def novaIdeja(request, pk):
    tabla = get_object_or_404(Tabla, pk=pk)
    user = User.objects.first()
    if request.method == 'POST':
        form = NewIdejaForm(request.POST)
        if form.is_valid():
            ideja = form.save(commit=False)
            ideja.tabla=tabla
            ideja.starter=user
            ideja.save()
            post = Post.objects.create(
                message = form.cleaned_data.get('message'),
                ideja=ideja,
                created_by=request.user
            )
            return redirect('PostiIdeje', pk=pk, ideja_pk=ideja.pk)



# In the line tabla=tabla,, we set the tabla field in Ideja model, which is a ForeignKey(Tabla). With that, now our Tabla instance is aware that it has an Ideja instance associated with it.
# The reason why we used board.topics.all instead of just board.topics is because board.topics is a Related Manager, which is pretty much similar to a Model Manager, usually available on the board.objects property. So, to return all topics associated with a given board, we have to run board.topics.all(). To filter some data, we could do board.topics.filter(subject__contains='Hello').

# Another important thing to note is that, inside Python code, we have to use parenthesis: board.topics.all(), because all() is a method. When writing code using the Django Template Language, in an HTML template file, we don’t use parenthesis, so it’s just board.topics.all.

#        The second thing is that we are making use of a ForeignKey:
#           {{ topic.starter.username }}
#    !!!!! v HTML KODI-  The form have three rendering options: form.as_table, form.as_ul, and form.as_p. It’s a quick way to render all the fields of a form. As the name suggests, the as_table uses table tags to format the inputs, the as_ul creates an HTML list of inputs, etc.
    else:
        form=NewIdejaForm()
    return render(request, 'nova_ideja.html', {'tabla': tabla,'form': form})

def PostiIdeje(request, pk, ideja_pk):
    ideja = get_object_or_404(Ideja, tabla__pk=pk, pk=ideja_pk)
    ideja.views += 1
    ideja.save()
    return render(request, 'PostiIdeje.html', {'ideja': ideja})

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'PostiIdeje.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.ideja.pk)
        if not self.request.session.get(session_key, False):
            self.ideja.views += 1
            self.ideja.save()
            self.request.session[session_key] = True
        kwargs['ideja'] = self.ideja
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.ideja = get_object_or_404(Ideja, tabla__pk=self.kwargs.get('pk'), pk=self.kwargs.get('ideja_pk'))
        queryset = self.ideja.posts.order_by('created_at')
        return queryset

@login_required
def reply_post(request, pk, ideja_pk):
    ideja = get_object_or_404(Ideja, tabla__pk=pk, pk=ideja_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.ideja = ideja
            post.created_by = request.user
            post.save()

            ideja.last_updated = timezone.now()
            ideja.save()

# nek dodatek, ki ga je uporabil v tutorialu, nisem uporabil!
            # ideja_url = reverse('topic_posts', kwargs={'pk': pk, 'ideja_pk': ideja_pk})
            # ideja_post_url = '{url}?page={page}#{id}'.format(
            #     url=ideja_url,
            #     id=post.pk,
            #     page=ideja.get_page_count()
            # )
            #
            # return redirect(ideja_post_url)

            return redirect('PostiIdeje', pk=pk, ideja_pk=ideja_pk)
    else:
        form = PostForm()
    return render(request, 'reply_ideja.html', {'ideja': ideja, 'form': form})


# We can’t decorate the class directly with the @login_required decorator. We have to use the utility @method_decorator, and pass a decorator (or a list of decorators) and tell which method should be decorated. In class-based views it’s common to decorate the dispatch method. It’s an internal method Django use (defined inside the View class). All requests pass through this method, so it’s safe to decorate it.
@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    # The pk_url_kwarg will be used to identify the name of the keyword argument used to retrieve the Post object. It’s the same as we define in the urls.py.
    pk_url_kwarg = 'post_pk'
    # If we don’t set the context_object_name attribute, the Post object will be available in the template as “object.” So, here we are using the context_object_name to rename it to post instead. You will see how we are using it in the template below.
    context_object_name = 'post'
# With the line queryset = super().get_queryset() we are reusing the get_queryset method from the parent class, that is, the UpateView class. Then, we are adding an extra filter to the queryset, which is filtering the post using the logged in user, available inside the request object.
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('PostiIdeje', pk=post.ideja.tabla.pk, ideja_pk=post.ideja.pk)

