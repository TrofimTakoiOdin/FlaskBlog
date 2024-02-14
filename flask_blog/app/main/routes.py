from flask import render_template, request, Blueprint, flash, redirect, url_for, current_app, make_response, session, \
    abort
from flask_login import login_required, current_user

from flask_blog import db
from flask_blog.app.decorators import permission_required, admin_required
from flask_blog.app.posts.forms import PostForm
from flask_blog.app.users.forms import UpdateAccountForm, EditProfileAdminForm, EditProfileForm
from flask_blog.app.users.utils import save_picture
from flask_blog.models import Post, Permission, User, Role

main = Blueprint('main', __name__)


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route("/")
@main.route("/home")
def home():
    per_page = 5
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    posts = query.order_by(Post.date_posted.desc()).paginate(
        page=page, per_page=per_page,
        error_out=False)

    return render_template('home.html',
                           show_followed=show_followed,posts=posts)


@main.route("/about")
def about():
    return render_template('about.html', title='About')


@main.route("/my_account", methods=['GET', 'POST'])
@login_required
def my_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('main.my_account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.about_me.data = current_user.about_me

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('my_account.html', title='Login', image_file=image_file, form=form)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('admin/edit_profile.html', form=form)

@main.route('/admin')
@login_required
@admin_required
def admin_index():
    # Add any necessary logic for your administration panel
    return render_template('admin/index.html')


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_profile(id):
    user = User.query.get_or_404(id)
    # Check if the admin is trying to edit their own profile
    is_admin_editing_own_profile = current_user.is_administrator() and user == current_user

    form = EditProfileAdminForm(user=user)
    form.email.render_kw = {'readonly': True}
    form.username.render_kw = {'readonly': True}

    if form.validate_on_submit():
        # Prevent changing confirmation status and role if the admin is editing their own profile
        if is_admin_editing_own_profile:
            form.confirmed.data = user.confirmed
            form.role.data = user.role_id

        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.username = form.username.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.', 'success')

        # Retrieve the previous endpoint from the session
        prev_endpoint = session.pop('prev_endpoint', None)

        return redirect(prev_endpoint or url_for('.admin_users'))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('admin/edit_profile.html', form=form, user=user)

@main.route('/admin/users')
@login_required
@admin_required
def admin_users():
    session['prev_endpoint'] = '/admin/users'
    users_per_page = 4
    page = request.args.get('page', 1, type=int)

    # Paginate the confirmed users query excluding admins and moderators
    confirmed_users_pagination = User.query.join(Role) \
        .filter(User.confirmed == True, ~Role.name.in_(['Administrator', 'Moderator'])) \
        .paginate(page=page, per_page=users_per_page, error_out=False)

    # Paginate the unconfirmed users query excluding admins and moderators
    unconfirmed_users_pagination = User.query.join(Role) \
        .filter(User.confirmed == False, ~Role.name.in_(['Administrator', 'Moderator'])) \
        .paginate(page=page, per_page=users_per_page, error_out=False)

    # Retrieve the lists of confirmed and unconfirmed users
    confirmed_users = confirmed_users_pagination.items
    unconfirmed_users = unconfirmed_users_pagination.items

    return render_template(
        'admin/users.html',
        confirmed_users_pagination=confirmed_users_pagination,
        unconfirmed_users_pagination=unconfirmed_users_pagination,
        confirmed_users=confirmed_users,
        unconfirmed_users=unconfirmed_users
    )

@main.route('/admin/moderators')
@login_required
@admin_required
def admin_moderators():
    # Store the current endpoint in the session
    session['prev_endpoint'] = '/admin/moderators'
    users_per_page = 4
    page = request.args.get('page', 1, type=int)

    # Paginate the moderators query
    moderators_pagination = User.query.join(Role).filter(Role.name == 'Moderator') \
        .paginate(page=page, per_page=users_per_page, error_out=False)

    # Retrieve the list of moderators
    moderators = moderators_pagination.items

    return render_template('admin/moderators.html', moderators=moderators,
                           moderators_pagination=moderators_pagination)

@main.route("/user/<string:username>")
@login_required
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.', 'success')
        return redirect(url_for('main.user_posts', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username, 'success')
    return redirect(url_for('main.user_posts', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.home'))
    if not current_user.is_following(user):
        flash('You are not following this user.', 'warning')
        return redirect(url_for('main.user_posts', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username, 'warning')
    return redirect(url_for('main.user_posts', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page=page, per_page=5,
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page=page, per_page=5,
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.home')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.home')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp
