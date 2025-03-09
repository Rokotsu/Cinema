from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pathlib import Path

from app.database.dependencies import get_db_session
from app.core.security import get_current_user
from app.services.movies_service import MovieService
from app.services.reviews_service import ReviewService
from app.services.subscriptions_service import SubscriptionService
from app.models.users import User
from app.schemas.movies import MovieRead

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")
movie_service = MovieService()
review_service = ReviewService()
subscription_service = SubscriptionService()

async def get_user_data(request: Request) -> dict:
    """Helper function to get common template data"""
    context = {"request": request}
    try:
        user = await get_current_user(request)
        context["user"] = user
    except:
        context["user"] = None
    return context

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render home page"""
    context = await get_user_data(request)
    return templates.TemplateResponse("index.html", context)

# Auth Routes
@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page"""
    context = await get_user_data(request)
    return templates.TemplateResponse("auth/login.html", context)

@router.get("/auth/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Render registration page"""
    context = await get_user_data(request)
    return templates.TemplateResponse("auth/register.html", context)

# Movie Routes
@router.get("/movies", response_class=HTMLResponse)
async def movies_page(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    genre: Optional[str] = None,
    release_year_from: Optional[int] = None,
    release_year_to: Optional[int] = None,
    rating_min: Optional[float] = None,
    rating_max: Optional[float] = None,
    sort_by: str = "release_date",
    order: str = "desc",
    skip: int = 0,
    limit: int = 12
):
    """Render movies catalog or return movie grid fragment for HTMX"""
    context = await get_user_data(request)
    movies = await movie_service.list_movies(
        db, genre, None, None, release_year_from, release_year_to,
        rating_min, rating_max, None, sort_by, order, skip, limit
    )
    context["movies"] = movies

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "components/movies_grid.html",
            context
        )
    return templates.TemplateResponse("movies/catalog.html", context)

@router.get("/movies/{movie_id}", response_class=HTMLResponse)
async def movie_details(
    request: Request,
    movie_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Render movie details page"""
    context = await get_user_data(request)
    movie = await movie_service.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    context["movie"] = movie
    return templates.TemplateResponse("movies/details.html", context)

@router.get("/movies/{movie_id}/watch", response_class=HTMLResponse)
async def watch_movie(
    request: Request,
    movie_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Render movie watch page"""
    context = await get_user_data(request)
    if not context["user"]:
        return RedirectResponse(url="/auth/login", status_code=303)

    movie = await movie_service.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    context["movie"] = movie
    context["age_confirmed"] = request.cookies.get("age_confirmed") == "true"

    if movie.required_subscription:
        subscription = await subscription_service.get_active_subscription(
            db, context["user"].id
        )
        context["subscription_valid"] = (
            subscription and
            subscription.plan.lower() == movie.required_subscription.lower()
        )
    else:
        context["subscription_valid"] = True

    return templates.TemplateResponse("movies/watch.html", context)

# Profile Routes
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Render user profile page"""
    context = await get_user_data(request)
    if not context["user"]:
        return RedirectResponse(url="/auth/login", status_code=303)

    subscription = await subscription_service.get_active_subscription(
        db, context["user"].id
    )
    context["subscription"] = subscription
    return templates.TemplateResponse("profile/index.html", context)

@router.get("/profile/edit", response_class=HTMLResponse)
async def edit_profile(request: Request):
    """Render profile edit page"""
    context = await get_user_data(request)
    if not context["user"]:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("profile/edit.html", context)

# Subscription Routes
@router.get("/subscription/plans", response_class=HTMLResponse)
async def subscription_plans(request: Request):
    """Render subscription plans page"""
    context = await get_user_data(request)
    if not context["user"]:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("subscription/plans.html", context)

# Review Routes
@router.get("/reviews/movie/{movie_id}", response_class=HTMLResponse)
async def movie_reviews(
    request: Request,
    movie_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Return movie reviews fragment for HTMX"""
    context = await get_user_data(request)
    reviews = await review_service.list_reviews_for_movie(db, movie_id)
    context["reviews"] = reviews
    return templates.TemplateResponse("reviews/movie_reviews.html", context)

@router.get("/reviews/{review_id}/edit", response_class=HTMLResponse)
async def edit_review(
    request: Request,
    review_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Return review edit form fragment for HTMX"""
    context = await get_user_data(request)
    if not context["user"]:
        raise HTTPException(status_code=401, detail="Unauthorized")

    review = await review_service.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != context["user"].id and context["user"].role != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden")

    context["review"] = review
    return templates.TemplateResponse(
        "components/review_edit_form.html",
        context
    )

# Payment Results
@router.get("/payment/success", response_class=HTMLResponse)
async def payment_success(request: Request):
    """Render payment success page"""
    context = await get_user_data(request)
    return templates.TemplateResponse("payment/success.html", context)

@router.get("/payment/cancel", response_class=HTMLResponse)
async def payment_cancel(request: Request):
    """Render payment cancellation page"""
    context = await get_user_data(request)
    return templates.TemplateResponse("payment/cancel.html", context)