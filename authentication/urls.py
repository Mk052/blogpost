from django.urls import path
from authentication.views import *

urlpatterns = [
    path('', AllBlogView.as_view(), name="all_blog"),
    path('my/', MyBlogView.as_view(), name="my_blog"),
    path('home/', HHomeView.as_view(), name="hhome"),
    path('signup/',SignupView.as_view(),name="signup"),
    path('login/',LoginView.as_view(),name="login"),
    path('logout/',LogoutView.as_view(),name="logout"),
    path('view_post/<int:blog_id>/', PostBlogView.as_view(), name="view_post"),
    path('create/', CreateView.as_view(), name="create_blog"),
    path('blog/<int:blog_id>/update/',UpdateView.as_view(),name="update_blog"),
    path('blog/<int:blog_id>/delete/',DeleteView.as_view(),name="delete_blog"),
    path('base/',BaseView.as_view(),name="base"),
    path('blog/like/<int:blog_id>/',LikeView.as_view(),name="like_blog"),
    path('verify-email/', EmailVerificationView.as_view(), name='verify'),
    path('boots/', BootsView.as_view(), name='boots'),
    path('edit/comment/<int:comment_id>/', EditCommentView.as_view(), name='comment-edit'),
    path('delete/comment/<int:comment_id>/',deleteCommentView.as_view(),name="comment-delete") 
] 