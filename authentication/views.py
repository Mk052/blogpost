from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from authentication.forms import CustomUserCreationForm, BlogPostForm, CommentForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.urls import reverse
from authentication.models import Category, User, Blogpost, Like, Comment


class LoginView(TemplateView):
    __doc__ = """This is login"""
    template_name = "authentication/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('all_blog')  # Redirect to the home page if user is authenticated

        return render(request, self.template_name)  # Render login page if not authenticated

    def post(self, request):
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        
        # Check if email exists and use it for authentication
        # Note: Assumes email is unique, you might need a custom User model or authentication backend for email-based login
        user = authenticate(request, username=email, password=password1)

        if user is not None:
            login(request, user)  # Log the user in and create a session
            return redirect('all_blog')  # Redirect to the homepage or desired page
        else:
            return render(request, self.template_name, {'error1': 'Invalid email or password'})  # Show error on invalid login
         

# signup view
class SignupView(TemplateView):
    template_name = 'authentication/signup.html'

    def get(self, request):
        form = CustomUserCreationForm()
        context = {
            "form": form
        }
        return render(request, self.template_name, context)
     
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)  # Automatically log the user in
            return redirect('all_blog')  # Redirect after successful signup
        return render(request, self.template_name, {'form': form})


# list of all blogs
class AllBlogView(TemplateView):
    template_name = "authentication/home.html"
       
    def get(self, request, **kwargs):
        context = {
            'blogs': Blogpost.objects.all().order_by('-created_at')
        }
        return render(request, self.template_name, context)  


# specific view
class PostBlogView(TemplateView):
    template_name = "authentication/view_post.html"

    def get(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id).first()
        context = {
            'blog': blog,
        }
        return render(request, self.template_name, context)  


# create a new post
class CreateView(TemplateView):
    template_name = "authentication/create_blog.html"

    def get_context_data(self, **kwargs):
        context = {
            'form': BlogPostForm()
        }
        return context

    def post(self, request, **kwargs):
        form = BlogPostForm(request.POST)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            blog = form.save()
            blog.user = request.user
            blog.save()
            return redirect('all_blog')
        return self.render_to_response({'form': form})


# update a view
class UpdateView(TemplateView):
    template_name = "authentication/update.html"

    def get_context_data(self, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id).first()
        form = BlogPostForm(instance=blog)
        context = {
            'form': form,
            'blog': blog
        }
        return context
    
    def post(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id).first()
        form = BlogPostForm(instance=blog, data=request.POST)
        print(form.is_valid)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('view_post', kwargs={'blog_id': blog.id}))
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
            

# delete a view
class DeleteView(TemplateView):
    template_name = "authentication/delete.html"

    def get_context_data(self, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        print(blog_id)
        blog = Blogpost.objects.filter(id=blog_id, user=self.request.user).first()
        # form = BlogPostForm(instance=blog)
        context = {
            'blog': blog
        }
        return context

    def post(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id, user=self.request.user).first()
        blog.delete()
        return redirect('all_blog')


class LikeView(TemplateView):
    template_name = "authentication/blog.html"

    def get(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog_post = Blogpost.objects.filter(id=blog_id).first()

        context = {
            "category": blog_post.category
        }

        return context

    def post(self, request, **kwargs):

        blog_id = self.kwargs.get('blog_id')
        blog_post = Blogpost.objects.filter(id=blog_id).first()

        like = Like.objects.filter(blog_post=blog_post, user=request.user).first()

        if like:
            like.delete()
        else:
            Like.objects.create(blog_post=blog_post, user=request.user)

        return redirect('blog', category_id=blog_post.category.id)


# logout
class LogoutView(TemplateView):
    template_name = "logout.html"  # Template to show after logout

    def get(self, request, *args, **kwargs):
        
        logout(request)
        # Redirect to the login page or any other page
        return HttpResponseRedirect(reverse('login'))  # Replace 'login' with the name of your login URl


class BaseView(TemplateView):
    template_name = "authentication/base.html"


class HHomeView(TemplateView):
    template_name = "authentication/home.html"


class CommentView(TemplateView):
    template_name = "authentication/comment.html"

    def get_context_data(self, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        print(blog_id)
        blog = Comment.objects.filter(id=blog_id).first()
        comments = Comment.objects.filter(blog=blog).order_by('-created_at')
        form = CommentForm()
        context = {
            'blog': blog,
            'comments': comments,
            'form': form
        }
        return context
    
    def post(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Comment.objects.filter(id=blog_id).first()
        form = CommentForm(request.POST)
        print(blog.user)
        if form.is_valid():
            blog_comment = form.save()
            blog_comment.blog = blog
            blog_comment.user = request.user
            blog_comment.save()
            return redirect(reverse_lazy('commment_blog', kwargs={'blog_id': blog_id}))
        else:
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)