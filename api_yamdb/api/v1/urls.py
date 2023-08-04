from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1 import views


reviews_url = r"titles/(?P<title_id>\d+)/reviews"
comments_url = rf"{reviews_url}/(?P<review_id>\d+)/comments"

router = DefaultRouter()

router.register("users", views.UserViewSet)
router.register("titles", views.TitleViewSet, basename="titles")
router.register("genres", views.GenreViewSet)
router.register("categories", views.CategoriesViewSet)
router.register(reviews_url, views.ReviewViewSet, basename="reviews")
router.register(comments_url, views.CommentViewSet, basename="comments")

auth_urls = [
    path("signup/", views.UserSignUp.as_view(), name="signup"),
    path("token/", views.UserGetToken.as_view(), name="token"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include(auth_urls)),
]
