import bleach
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Book, Review, ReviewStatus

reviews_bp = Blueprint('reviews', __name__)

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'pre', 'code', 'blockquote', 'ul', 'ol', 'li'
]


def sanitize(text):
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=bleach.sanitizer.ALLOWED_ATTRIBUTES)


@reviews_bp.route('/books/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def add(book_id):
    book = Book.query.get_or_404(book_id)

    existing = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if existing:
        flash('Вы уже оставляли рецензию на эту книгу.', 'warning')
        return redirect(url_for('books.detail', book_id=book_id))

    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        text = sanitize(request.form.get('text', ''))

        if rating is None or not text.strip():
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('reviews/form.html', book=book, form_data=request.form)

        pending_status = ReviewStatus.query.filter_by(name='На рассмотрении').first()

        try:
            review = Review(
                book_id=book_id,
                user_id=current_user.id,
                rating=rating,
                text=text,
                status_id=pending_status.id
            )
            db.session.add(review)
            db.session.commit()
            flash('Ваша рецензия отправлена на рассмотрение.', 'success')
            return redirect(url_for('books.detail', book_id=book_id))
        except Exception:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    return render_template('reviews/form.html', book=book, form_data={})


@reviews_bp.route('/my-reviews')
@login_required
def my_reviews():
    reviews = (Review.query
               .filter_by(user_id=current_user.id)
               .order_by(Review.created_at.desc())
               .all())
    return render_template('reviews/my_reviews.html', reviews=reviews)
