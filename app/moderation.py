from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Review, ReviewStatus

moderation_bp = Blueprint('moderation', __name__, url_prefix='/moderation')


def require_moderator():
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.is_moderator():
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return False
    return True


@moderation_bp.route('/')
@login_required
def index():
    if not require_moderator():
        return redirect(url_for('books.index'))

    page = request.args.get('page', 1, type=int)
    pending_status = ReviewStatus.query.filter_by(name='На рассмотрении').first()

    pagination = (Review.query
                  .filter_by(status_id=pending_status.id)
                  .order_by(Review.created_at.asc())
                  .paginate(page=page,
                            per_page=current_app.config['REVIEWS_PER_PAGE'],
                            error_out=False))

    return render_template('moderation/index.html', pagination=pagination, reviews=pagination.items)


@moderation_bp.route('/review/<int:review_id>')
@login_required
def review_detail(review_id):
    if not require_moderator():
        return redirect(url_for('books.index'))

    review = Review.query.get_or_404(review_id)
    return render_template('moderation/review_detail.html', review=review)


@moderation_bp.route('/review/<int:review_id>/approve', methods=['POST'])
@login_required
def approve(review_id):
    if not require_moderator():
        return redirect(url_for('books.index'))

    review = Review.query.get_or_404(review_id)
    approved = ReviewStatus.query.filter_by(name='Одобрена').first()
    review.status_id = approved.id
    db.session.commit()
    flash('Рецензия одобрена и опубликована.', 'success')
    return redirect(url_for('moderation.index'))


@moderation_bp.route('/review/<int:review_id>/reject', methods=['POST'])
@login_required
def reject(review_id):
    if not require_moderator():
        return redirect(url_for('books.index'))

    review = Review.query.get_or_404(review_id)
    rejected = ReviewStatus.query.filter_by(name='Отклонена').first()
    review.status_id = rejected.id
    db.session.commit()
    flash('Рецензия отклонена.', 'warning')
    return redirect(url_for('moderation.index'))
