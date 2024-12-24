from django.urls import path
from authentication.views import *

urlpatterns = [
    path('', AllBlogView.as_view(), name="all_blog"),
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
    path('blog/comment/<int:blog_id>/',CommentView.as_view(),name="comment_blog") 
] 