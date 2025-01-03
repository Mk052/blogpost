from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from authentication.forms import CustomUserCreationForm, BlogPostForm, CommentForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.urls import reverse
from authentication.models import Category, User, Blogpost, Like, Comment
from datetime import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from authentication.utils import generate_verification_token, verify_token
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages


def send_verification_email(user):
    name = user.full_name[:2]
    token = generate_verification_token(name)
    verification_url = f"{settings.SITE_URL}/verify-email/?token={token}"
    subject = "Verify your email address"
    message = f"hi {user.email}, click the link to verify your email: {verification_url}"
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email])


class EmailVerificationView(TemplateView):
    template_name = "authentication/verifyy_email.html"

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        print(token)
        # Verify the token
        name = verify_token(token)
        print("hi")
        print(name)

        if name:
            try:
                user = User.objects.get(full_name__startswith=name)
                if not user.is_email_verified:
                    user.is_email_verified = True
                    user.save()
                    messages.success(request, "Your email has been verified successfully!")
                else:
                    messages.info(request, "Your email is already verified.")
            except User.DoesNotExist:
                messages.error(request, "Invalid verification link")
        else:
            messages.error(request, "Invalid verification link.")
        return redirect('all_blog')


class BootsView(TemplateView):
    template_name = "authentication/boots.html"


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
        print(form.is_multipart())
        print(form.errors)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.save()
            send_verification_email(user)
            #login(request, user)  
            
            messages.info(request, "A verification email has been sent to your email address. Please check your inbox") 
            return redirect('login')  # Redirect after successful signup
        return render(request, self.template_name, {'form': form})


class MyBlogView(TemplateView):
    template_name = "authentication/my_blog.html"

    def get(self, request, **kwargs):
        user = self.request.user
        my_blog = Blogpost.objects.filter(user=user).order_by('-created_at')
        context = {
            'my_blog': my_blog
        }
        return render(request, self.template_name, context)


# list of all blogs
# class AllBlogView(TemplateView):
#     template_name = "authentication/home.html"
       
#     def get(self, request, **kwargs):
#         category_name = self.request.GET.get('category')
#         start = self.request.GET.get("start_date")                                                                                                                                                                                           
#         end = self.request.GET.get("end_date")
#         blogs = Blogpost.objects.filter(category__name=category_name).order_by('-created_at')
#         print(blogs)
#         print(type(start), type(end))
#         print(category_name)

#         # conver str date to date formate
#         if start and end:
#             start = datetime.strptime(start, "%Y-%m-%d").date()
#             end = datetime.strptime(end, "%Y-%m-%d").date()
#         else:
#             start = end = None

#         # Convert date to datetime range if start and end are provided
#         if start and end:
#             start_datetime = datetime.combine(start, datetime.min.time())
#             end_datetime = datetime.combine(end, datetime.max.time())
#         else:
#             start_datetime = end_datetime = None

#         date = Blogpost.objects.filter(created_at__gte=start_datetime, created_at__lte=end_datetime),
#         print(date)

#         if category_name and (start and end):
#             if category_name != "All":
#                 blogs = Blogpost.objects.filter(category__name=category_name).order_by('-created_at')
#             if category_name == "All":
#                 blogs = Blogpost.objects.all().order_by('-created_at')
#             if start and end:
#                 blogs = Blogpost.objects.filter((created_at__gte =start_datetime, created_at__lte=end_datetime))

#             context = {
#                 'blogs': Blogpost.objects.filter(category__name=category_name, created_at__gte=start_datetime, created_at__lte=end_datetime),
#                 'categories': Category.objects.all()
#                 }
#             return render(request, self.template_name, context)

#         if category_name and (not(start and end)):
#             if category_name != "All":
#                 context = {
#                     'blogs': blog,
#                     'categories': Category.objects.all()
#                 }
#                 print(context) 
#             else:
#                 context = {
#                     'blogs': Blogpost.objects.all().order_by('-created_at'),
#                     'categories': Category.objects.all()
#                 }
#             return render(request, self.template_name, context)
        
#         if start and end:
#             context = {
#                 'blogs': Blogpost.objects.filter(created_at__gte =start_datetime, created_at__lte=end_datetime),
#                 'categories': Category.objects.all()
#             }
#             return render(request, self.template_name, context)

        

#         context = {
#             'blogs': Blogpost.objects.all().order_by('-created_at'),
#             'categories': Category.objects.all()
#         }
#         return render(request, self.template_name, context)  


class AllBlogView(TemplateView):
    template_name = "authentication/home.html"
       
    def get(self, request, **kwargs):
        category_name = self.request.GET.get('category')
        start_date = self.request.GET.get("start_date")                                                                                                                                                                                           
        end_date = self.request.GET.get("end_date")
        page = request.GET.get("page",1)

        # conver str date to date formate
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        #  Convert date to datetime range if start and end are provided
        if start_date and end_date:
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.max.time())

        # print(date)
        blogs = Blogpost.objects.all().order_by('-created_at')

        if category_name and category_name != "All":
            blogs = blogs.filter(category__name=category_name)
            selected_category = category_name
        else:
            selected_category = "All"
                
        if start_date:
            blogs = blogs.filter(created_at__gte =start_date)
        if end_date:
            blogs = blogs.filter(created_at__lte=end_date)
              
        categories = Category.objects.all()
        paginator = Paginator(blogs,10)


        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        context = {
            'blogs': blogs,
            'selected_category': selected_category,
            'categories': categories,
            'start_date':start_date,
            'end_date':end_date
        }
        return render(request, self.template_name, context)  


# specific view
class PostBlogView(TemplateView):
    template_name = "authentication/view_post.html"

    def get(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id).first()
        comments = blog.comments.order_by('-created_at')
        context = {
            'blog': blog,
            'comments': comments,
            'comment_form': CommentForm()
        }
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id).first()
        form = CommentForm(request.POST)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            comment_blog = form.save(commit=False)
            comment_blog.blog = blog
            comment_blog.user = request.user
            comment_blog.save()
            return redirect('view_post', blog_id=blog_id)
        else:
            context = self.get_context_data(**kwargs)
            context['comment_form'] = form
            return self.render_to_response(context)
        

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


# class EditCommentView(TemplateView):
#     template_name = "authentication/update.html"

#     def get_context_data(self, **kwargs):
#         comment_id = self.kwargs.get('comment_id')
#         comment = Comment.objects.filter(id=comment_id).first()
#         if not self.request.user.is_superuser or comment.user != self.request.user:
#             return HttpResponseRedirect('all_blog')
#         form = CommentForm(instance=comment)
#         context = {
#             'form': form,
#             'comment': comment
#         }
#         return context
    
#     def post(self, **kwargs):
#         comment_id = self.kwargs.get('comment_id')
#         comment = Comment.objects.filter(id=comment_id).first()
#         if not self.request.user.is_superuser and comment.user != self.request.user:
#             return HttpResponseRedirect('view_post')
#         form = CommentForm(instance=comment, data=self.request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect(reverse_lazy('view_post', kwargs={'comment_id': comment.blog.id}))
#         return self.render_to_response({'form': form, 'comment': comment})


# update a view
class UpdateView(TemplateView):
    template_name = "authentication/update.html"

    def get_context_data(self, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id).first()
        if not self.request.user.is_superuser and blog.user != self.request.user:
            return redirect('all_blog')
        form = BlogPostForm(instance=blog)
        context = {
            'form': form,
            'blog': blog
        }
        return context
    
    def post(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id).first()
        if not self.request.user.is_superuser and blog.user != self.request.user:
            return redirect('view_post')
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
        blog = Blogpost.objects.filter(id=blog_id).first()
        # form = BlogPostForm(instance=blog)
        if not self.request.user.is_superuser and blog.user != self.request.user:
            return redirect('view_post')
        context = {
            'blog': blog
        }
        return context

    def post(self, request, **kwargs):
        blog_id = self.kwargs.get('blog_id')
        blog = Blogpost.objects.filter(id=blog_id).first()
        if not self.request.user.is_superuser and blog.user != self.request.user:
            return redirect('view_post')
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


# class CommentView(TemplateView):
#     template_name = "authentication/view_post.html"

#     def get_context_data(self, **kwargs):
#         blog_id = self.kwargs.get('blog_id')
#         print(blog_id)
#         blog = Comment.objects.filter(id=blog_id).first()
#         comments = Comment.objects.filter(blog=blog)
#         form = CommentForm()
#         context = {
#             'blog': blog,
#             'comments': comments,
#             'form': form
#         }
#         return context
    
#     def post(self, request, **kwargs):
#         blog_id = self.kwargs.get('blog_id')
#         blog = Comment.objects.filter(id=blog_id).first()
#         form = CommentForm(request.POST)
#         print(blog.user)
#         if form.is_valid():
#             blog_comment = form.save()
#             blog_comment.blog = blog
#             blog_comment.user = request.user
#             blog_comment.save()
#             return redirect(reverse_lazy('commment_blog', kwargs={'blog_id': blog_id}))
#         else:
#             context = self.get_context_data(**kwargs)
#             context['form'] = form
#             return self.render_to_response(context)


class EditCommentView(TemplateView):
    template_name = "authentication/comment_edit.html"

    def get(self, request, **kwargs):
        comment_id = self.kwargs.get('comment_id')
        comment = Comment.objects.filter(id=comment_id).first()
        
        if not self.request.user.is_superuser and comment.user != self.request.user:
            return redirect('all_blog')
        
        form = CommentForm(instance=comment)
        context = {
            'form': form,
            'comment': comment
        }
        
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        comment_id = self.kwargs.get('comment_id')
        comment = Comment.objects.filter(id=comment_id).first()
        
        if not self.request.user.is_superuser and comment.user != self.request.user:
            return redirect('all_blog')
        
        form = CommentForm(instance=comment, data=request.POST)
        
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('comment-edit', kwargs={'comment_id': comment.blog.id}))
        
        context = {
            'form': form,
            'comment': comment
        } 
        return render(request, self.template_name, context)
    

class deleteCommentView(TemplateView):
    template_name = "authentication/comment_delete.html"

    def get_context_data(self, **kwargs):
        comment_id = self.kwargs.get('comment_id')
        comment = Comment.objects.filter(id=comment_id).first()

        if not self.request.user.is_superuser and self.request.user != comment.user:
            return redirect('all_blogs')
        
        context = {
            'comment': comment
        }
        return render(self.request, self.template_name, context)
    
    def post(self, **kwargs):
        comment_id = self.kwargs.get('comment_id')
        comment = Comment.objects.filter(id=comment_id).first()

        if not self.request.user.is_superuser and self.request.user != comment.user:
            return redirect('all_blogs')
        blog_id = comment.blog.id
        comment.delete()
        return redirect('view_post', comment_id=blog_id)
        
