from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from authentication.forms import CustomUserCreationForm, BlogPostForm, CommentForm
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from authentication.models import Category, User, Blogpost, Like, Comment
from datetime import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth import update_session_auth_hash
from authentication.utils import (
    generate_verification_token,
    generate_password_token,
    send_forgot_password,
    send_verification_email,
)
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy


class ResetPasswordView(TemplateView):
    template_name = "authentication/reset_password.html"

    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # Important to keep the user logged in
            messages.success(request, "password changed successfully!")
            return redirect('all_blog')
        print(form.errors)
        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})


class ForgetPasswordView(TemplateView):
    template_name = "registration/password_reset_form.html"

    def get(self, request):
        return render(request, "registration/password_reset_form.html")

    def post(self, request):
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            # Ensure user exists
            print(f"User PK: {user.pk}")  # Debug primary key
            user.forgot_password_token = generate_password_token()
            user.forgot_password_sent_at = (
                timezone.now()
            )  # Set the timestamp for the reset link
            user.save()
            print(user.forgot_password_sent_at)  # Debug the sent timestamp
            user.reset_password = False
            user.save()
            send_forgot_password(user)
            messages.success(
                request, "Password reset link has been sent to your email."
            )
        else:
            messages.error(request, "Email not found.")
        return redirect("password_reset")


class ForgetPasswordDoneView(TemplateView):
    template_name = "registration/password_reset_done.html"

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")  # Get token from URL
        print("get token", token)
        user = User.objects.filter(forgot_password_token=token).first()
        print("user after get token", user)
        print("true and false", user.reset_password)

        if user and not user.reset_password:
            print(user.forgot_password_sent_at)
            if user.forgot_password_sent_at and (
                user.forgot_password_sent_at + timezone.timedelta(minutes=5)
                > timezone.now()
            ):
                print("in form")
                return render(request, self.template_name, {"token": token})
            else:
                messages.error(request, "Invalid or expired link.")
                return redirect("password_reset")
        else:
            messages.error(
                request, "Invalid link or user does not exist. Password already reset."
            )
            return redirect("password_reset")

    def post(self, request, *args, **kwargs):
        token = request.POST.get("token")
        password = request.POST.get("password1")
        print("token, user", token, password)
        user = User.objects.filter(forgot_password_token=token).first()

        if user and not user.reset_password:
            if user.forgot_password_sent_at and (
                user.forgot_password_sent_at + timezone.timedelta(minutes=5)
                > timezone.now()
            ):
                if password:
                    user.set_password(password)
                    user.reset_password = True
                    user.save()
                    messages.success(
                        request, "Your password has been reset successfully!"
                    )
                    return redirect("login")
                else:
                    messages.error(request, "Please provide a valid password.")
                    return render(request, self.template_name, {"token": token})
            else:
                messages.error(request, "Link has expired or is invalid.")
                return redirect("password_reset")

        messages.error(request, "User does not exist.")
        return redirect("password_reset")


class EmailVerificationView(TemplateView):
    template_name = "authentication/verifyy_email.html"

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        user = User.objects.filter(email_verified_token=token).first()
        print(token, user)
        # Verify the token

        if user and not user.is_email_verified:
            if (
                user.email_verified_sent_at + timezone.timedelta(minutes=5)
                > timezone.now()
            ):
                user.is_email_verified = True
                user.save()
                messages.success(request, "Your email has been verified successfully!")
                return redirect("login")
            else:
                messages.info(request, "Invalid link.")
        else:
            messages.error(request, "your email is already verified or user not exit")
        return redirect("signup")


class BootsView(TemplateView):
    template_name = "authentication/boots.html"


class LoginView(TemplateView):
    __doc__ = """This is login"""
    template_name = "authentication/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(
                "all_blog"
            )  # Redirect to the homepage if user is authenticated
        return render(
            request, self.template_name
        )  # Render login page if not authenticated

    def post(self, request):
        email = request.POST.get("email")
        password1 = request.POST.get("password")

        # Authenticate user with provided email and password
        user = authenticate(request, username=email, password=password1)

        if user is not None:
            login(request, user)  # Log the user in
            return redirect("all_blog")  # Redirect to the desired page
        else:
            # Return to login page with an error message
            return render(
                request, self.template_name, {"error1": "Invalid email or password"}
            )


# signup view
class SignupView(TemplateView):
    template_name = "authentication/signup.html"

    def get(self, request):
        form = CustomUserCreationForm()
        context = {"form": form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        print(form.is_multipart())
        print(form.errors)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_verified_token = generate_verification_token()
            user.email_verified_sent_at = timezone.now()
            user.is_email_verified = False
            user.save()
            send_verification_email(user)
            # login(request, user)

            messages.info(
                request,
                "A verification email has been sent to your email address. Please check your inbox",
            )
            return redirect("signup")  # Redirect after successful signup
        return render(request, self.template_name, {"form": form})


class MyBlogView(TemplateView):
    template_name = "authentication/my_blog.html"

    def get(self, request, **kwargs):
        user = self.request.user
        my_blog = Blogpost.objects.filter(user=user).order_by("-created_at")
        context = {"my_blog": my_blog}
        return render(request, self.template_name, context)


class AllBlogView(TemplateView):
    template_name = "authentication/home.html"

    def get(self, request, **kwargs):
        category_name = self.request.GET.get("category")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        page = request.GET.get("page", 1)

        # conver str date to date formate
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        #  Convert date to datetime range if start and end are provided
        if start_date and end_date:
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.max.time())

        # print(date)
        blogs = Blogpost.objects.all().order_by("-created_at")

        if category_name and category_name != "All":
            blogs = blogs.filter(category__name=category_name)
            selected_category = category_name
        else:
            selected_category = "All"

        if start_date:
            blogs = blogs.filter(created_at__gte=start_date)
        if end_date:
            blogs = blogs.filter(created_at__lte=end_date)

        categories = Category.objects.all()
        paginator = Paginator(blogs, 10)

        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        context = {
            "blogs": blogs,
            "selected_category": selected_category,
            "categories": categories,
            "start_date": start_date,
            "end_date": end_date,
        }
        return render(request, self.template_name, context)


# specific view
class PostBlogView(TemplateView):
    template_name = "authentication/view_post.html"

    def get(self, request, **kwargs):
        blog_id = self.kwargs.get("blog_id")
        blog = Blogpost.objects.filter(id=blog_id).first()
        comments = blog.comments.order_by("-created_at")
        context = {"blog": blog, "comments": comments, "comment_form": CommentForm()}
        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        blog_id = self.kwargs.get("blog_id")
        blog = Blogpost.objects.filter(id=blog_id).first()
        form = CommentForm(request.POST)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            comment_blog = form.save(commit=False)
            comment_blog.blog = blog
            comment_blog.user = request.user
            comment_blog.save()
            return redirect("view_post", blog_id=blog_id)
        else:
            context = self.get_context_data(**kwargs)
            context["comment_form"] = form
            return self.render_to_response(context)


# create a new post
class CreateView(TemplateView):
    template_name = "authentication/create_blog.html"

    def get_context_data(self, **kwargs):
        context = {"form": BlogPostForm()}
        return context

    def post(self, request, **kwargs):
        form = BlogPostForm(request.POST)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            blog = form.save()
            blog.user = request.user
            blog.save()
            return redirect("all_blog")
        return self.render_to_response({"form": form})


# update a view
class UpdateView(TemplateView):
    template_name = "authentication/update.html"

    def get_context_data(self, **kwargs):
        blog_id = self.kwargs.get("blog_id")
        blog = Blogpost.objects.filter(id=blog_id).first()
        if not self.request.user.is_superuser and blog.user != self.request.user:
            return redirect("all_blog")
        form = BlogPostForm(instance=blog)
        context = {"form": form, "blog": blog}
        return context

    def post(self, request, **kwargs):
        blog_id = self.kwargs.get("blog_id")
        blog = Blogpost.objects.filter(id=blog_id).first()
        if not self.request.user.is_superuser and blog.user != self.request.user:
            return redirect("view_post")
        form = BlogPostForm(instance=blog, data=request.POST)
        print(form.is_valid)
        print(form.errors)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy("view_post", kwargs={"blog_id": blog.id}))
        else:
            context = self.get_context_data(**kwargs)
            context["form"] = form
            return self.render_to_response(context)


# delete a view
class DeleteView(TemplateView):
    template_name = "authentication/delete.html"

    def get_context_data(self, **kwargs):
        blog_id = self.kwargs.get("blog_id")
        print(blog_id)
        blog = Blogpost.objects.filter(id=blog_id).first()
        # form = BlogPostForm(instance=blog)
        if not self.request.user.is_superuser and blog.user != self.request.user:
            return redirect("view_post")
        context = {"blog": blog}
        return context

    def post(self, request, **kwargs):
        blog_id = self.kwargs.get("blog_id")
        blog = Blogpost.objects.filter(id=blog_id).first()
        if not self.request.user.is_superuser and blog.user != self.request.user:
            return redirect("view_post")
        blog.delete()
        return redirect("all_blog")


class LikeView(TemplateView):
    template_name = "authentication/blog.html"

    def get(self, request, **kwargs):
        blog_id = self.kwargs.get("blog_id")
        blog_post = Blogpost.objects.filter(id=blog_id).first()

        context = {"category": blog_post.category}

        return context

    def post(self, request, **kwargs):

        blog_id = self.kwargs.get("blog_id")
        blog_post = Blogpost.objects.filter(id=blog_id).first()

        like = Like.objects.filter(blog_post=blog_post, user=request.user).first()

        if like:
            like.delete()
        else:
            Like.objects.create(blog_post=blog_post, user=request.user)

        return redirect("blog", category_id=blog_post.category.id)


# logout
class LogoutView(TemplateView):
    template_name = "logout.html"  # Template to show after logout

    def get(self, request, *args, **kwargs):

        logout(request)
        # Redirect to the login page or any other page
        return HttpResponseRedirect(
            reverse("login")
        )  # Replace 'login' with the name of your login URl


class BaseView(TemplateView):
    template_name = "authentication/base.html"


class HHomeView(TemplateView):
    template_name = "authentication/home.html"


class EditCommentView(TemplateView):
    template_name = "authentication/comment_edit.html"

    def get(self, request, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        comment = Comment.objects.filter(id=comment_id).first()

        if not self.request.user.is_superuser and comment.user != self.request.user:
            return redirect("all_blog")

        form = CommentForm(instance=comment)
        context = {"form": form, "comment": comment}

        return render(request, self.template_name, context)

    def post(self, request, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        comment = Comment.objects.filter(id=comment_id).first()

        if not self.request.user.is_superuser and comment.user != self.request.user:
            return redirect("all_blog")

        form = CommentForm(instance=comment, data=request.POST)

        if form.is_valid():
            form.save()
            return redirect(
                reverse_lazy("comment-edit", kwargs={"comment_id": comment.blog.id})
            )

        context = {"form": form, "comment": comment}
        return render(request, self.template_name, context)


class deleteCommentView(TemplateView):
    template_name = "authentication/comment_delete.html"

    def get_context_data(self, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        comment = Comment.objects.filter(id=comment_id).first()

        if not self.request.user.is_superuser and self.request.user != comment.user:
            return redirect("all_blogs")

        context = {"comment": comment}
        return render(self.request, self.template_name, context)

    def post(self, **kwargs):
        comment_id = self.kwargs.get("comment_id")
        comment = Comment.objects.filter(id=comment_id).first()

        if not self.request.user.is_superuser and self.request.user != comment.user:
            return redirect("all_blogs")
        blog_id = comment.blog.id
        comment.delete()
        return redirect("view_post", comment_id=blog_id)
